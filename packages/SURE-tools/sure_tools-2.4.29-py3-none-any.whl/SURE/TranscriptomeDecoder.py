import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class TranscriptomeDecoder:
    """Transcriptome decoder"""
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dim: int = 512,
                 device: str = None):
        """
        Simple but powerful decoder for latent to transcriptome mapping
        
        Args:
            latent_dim: Latent variable dimension (typically 50-100)
            gene_dim: Number of genes (full transcriptome ~60,000)
            hidden_dim: Hidden dimension optimized
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.gene_dim = gene_dim
        self.hidden_dim = hidden_dim
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        self.model = self._build_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        
        print(f"🚀 SimpleTranscriptomeDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimension: {hidden_dim}")
        print(f"   - Device: {self.device}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class Decoder(nn.Module):
        """Memory-efficient decoder architecture with dimension handling"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dim: int):
            super().__init__()
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            self.hidden_dim = hidden_dim
            
            # Stage 1: Latent variable expansion
            self.latent_expansion = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim * 2),
                nn.BatchNorm1d(hidden_dim * 2),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.GELU(),
            )
            
            # Stage 2: Direct projection to gene dimension (simpler approach)
            self.gene_projector = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim * 2),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim * 2, gene_dim),  # Direct projection to gene_dim
            )
            
            # Stage 3: Lightweight gene interaction
            self.gene_interaction = nn.Sequential(
                nn.Conv1d(1, 32, kernel_size=3, padding=1),
                nn.GELU(),
                nn.Dropout1d(0.1),
                nn.Conv1d(32, 1, kernel_size=3, padding=1),
            )
            
            # Output scaling
            self.output_scale = nn.Parameter(torch.ones(1))
            self.output_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _init_weights(self):
            """Weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
                elif isinstance(module, nn.Conv1d):
                    nn.init.kaiming_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, latent: torch.Tensor) -> torch.Tensor:
            batch_size = latent.shape[0]
            
            # 1. Expand latent variables
            latent_features = self.latent_expansion(latent)  # [batch_size, hidden_dim]
            
            # 2. Direct projection to gene dimension
            gene_output = self.gene_projector(latent_features)  # [batch_size, gene_dim]
            
            # 3. Gene interaction with dimension safety
            if self.gene_dim > 1:  # Only apply if gene_dim > 1
                gene_output = gene_output.unsqueeze(1)  # [batch_size, 1, gene_dim]
                interaction_output = self.gene_interaction(gene_output)  # [batch_size, 1, gene_dim]
                gene_output = gene_output + interaction_output  # Residual connection
                gene_output = gene_output.squeeze(1)  # [batch_size, gene_dim]
            
            # 4. Final activation (ensure non-negative)
            gene_output = F.softplus(gene_output * self.output_scale + self.output_bias)
            
            return gene_output
    
    def _build_model(self):
        """Build the decoder model"""
        return self.Decoder(self.latent_dim, self.gene_dim, self.hidden_dim)
    
    def _create_dataset(self, latent_data, expression_data):
        """Create dataset with dimension validation"""
        class SimpleDataset(Dataset):
            def __init__(self, latent, expression):
                # Ensure dimensions match
                assert latent.shape[0] == expression.shape[0], "Sample count mismatch"
                assert latent.shape[1] == self.latent_dim, f"Latent dim mismatch: expected {self.latent_dim}, got {latent.shape[1]}"
                assert expression.shape[1] == self.gene_dim, f"Gene dim mismatch: expected {self.gene_dim}, got {expression.shape[1]}"
                
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return SimpleDataset(latent_data, expression_data)
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 100,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'transcriptome_decoder.pth'):
        """
        Train the decoder model with dimension safety
        
        Args:
            train_latent: Training latent variables [n_samples, latent_dim]
            train_expression: Training expression data [n_samples, gene_dim]
            val_latent: Validation latent variables (optional)
            val_expression: Validation expression data (optional)
            batch_size: Batch size optimized for memory
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            checkpoint_path: Path to save the best model
        """
        print("🚀 Starting training...")
        
        # Dimension validation
        self._validate_data_dimensions(train_latent, train_expression, "Training")
        if val_latent is not None and val_expression is not None:
            self._validate_data_dimensions(val_latent, val_expression, "Validation")
        
        # Data preparation
        train_dataset = self._create_safe_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_safe_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
            print(f"📈 Using provided validation data: {len(val_dataset)} samples")
        else:
            # Auto split
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=2)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=2)
            print(f"📈 Auto-split validation: {val_size} samples")
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"📊 Batch size: {batch_size}")
        
        # Optimizer configuration
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            betas=(0.9, 0.999)
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
        
        # Loss function with dimension safety
        def safe_loss(pred, target):
            # Ensure dimensions match
            if pred.shape != target.shape:
                print(f"⚠️ Dimension mismatch: pred {pred.shape}, target {target.shape}")
                # Truncate to minimum dimension (safety measure)
                min_dim = min(pred.shape[1], target.shape[1])
                pred = pred[:, :min_dim]
                target = target[:, :min_dim]
                
            def correlation_loss(pred, target):
                pred_centered = pred - pred.mean(dim=1, keepdim=True)
                target_centered = target - target.mean(dim=1, keepdim=True)
        
                correlation = (pred_centered * target_centered).sum(dim=1) / (
                    torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * 
                    torch.sqrt(torch.sum(target_centered ** 2, dim=1)) + 1e-8
                )
        
                return 1 - correlation.mean()
            
            mse_loss = F.mse_loss(pred, target)
            poisson_loss = (pred - target * torch.log(pred + 1e-8)).mean()
            corr_loss = correlation_loss(pred, target)
            return mse_loss + 0.5 * poisson_loss + 0.3 * corr_loss
        
        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }
        
        best_val_loss = float('inf')
        patience = 15
        patience_counter = 0
        
        print("\n📈 Starting training loop...")
        for epoch in range(1, num_epochs + 1):
            # Training phase
            train_loss = self._train_epoch(train_loader, optimizer, safe_loss)
            
            # Validation phase
            val_loss = self._validate_epoch(val_loader, safe_loss)
            
            # Update scheduler
            scheduler.step()
            current_lr = scheduler.get_last_lr()[0]
            
            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['learning_rate'].append(current_lr)
            
            # Print progress
            if epoch % 5 == 0 or epoch == 1:
                print(f"📍 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train Loss: {train_loss:.4f} | "
                      f"Val Loss: {val_loss:.4f} | "
                      f"LR: {current_lr:.2e}")
            
            # Early stopping and model saving
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self._save_checkpoint(epoch, optimizer, scheduler, best_val_loss, history, checkpoint_path)
                if epoch % 10 == 0:
                    print(f"💾 Best model saved (Val Loss: {best_val_loss:.4f})")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"🛑 Early stopping at epoch {epoch}")
                    break
        
        # Training completed
        self.is_trained = True
        self.training_history = history
        self.best_val_loss = best_val_loss
        
        print(f"\n🎉 Training completed!")
        print(f"🏆 Best validation loss: {best_val_loss:.4f}")
        print(f"📊 Final training loss: {history['train_loss'][-1]:.4f}")
        
        return history
    
    def _validate_data_dimensions(self, latent_data, expression_data, data_type):
        """Validate input data dimensions"""
        assert latent_data.shape[1] == self.latent_dim, (
            f"{data_type} latent dimension mismatch: expected {self.latent_dim}, got {latent_data.shape[1]}")
        assert expression_data.shape[1] == self.gene_dim, (
            f"{data_type} gene dimension mismatch: expected {self.gene_dim}, got {expression_data.shape[1]}")
        assert latent_data.shape[0] == expression_data.shape[0], (
            f"{data_type} sample count mismatch: latent {latent_data.shape[0]}, expression {expression_data.shape[0]}")
        print(f"✅ {data_type} data dimensions validated")
    
    def _create_safe_dataset(self, latent_data, expression_data):
        """Create dataset with safety checks"""
        class SafeDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
                
                # Safety check
                if self.latent.shape[0] != self.expression.shape[0]:
                    raise ValueError(f"Sample count mismatch: latent {self.latent.shape[0]}, expression {self.expression.shape[0]}")
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return SafeDataset(latent_data, expression_data)
    
    def _train_epoch(self, train_loader, optimizer, loss_fn):
        """Train for one epoch with dimension safety"""
        self.model.train()
        total_loss = 0
        
        for batch_idx, (latent, target) in enumerate(train_loader):
            latent = latent.to(self.device)
            target = target.to(self.device)
            
            # Dimension check
            if latent.shape[1] != self.latent_dim:
                print(f"⚠️ Batch {batch_idx}: Latent dim mismatch {latent.shape[1]} != {self.latent_dim}")
                continue
                
            optimizer.zero_grad()
            pred = self.model(latent)
            
            # Final dimension check before loss calculation
            if pred.shape[1] != target.shape[1]:
                min_dim = min(pred.shape[1], target.shape[1])
                pred = pred[:, :min_dim]
                target = target[:, :min_dim]
                if batch_idx == 0:  # Only warn once
                    print(f"⚠️ Truncating to min dimension: {min_dim}")
            
            loss = loss_fn(pred, target)
            loss.backward()
            
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def _validate_epoch(self, val_loader, loss_fn):
        """Validate for one epoch with dimension safety"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch_idx, (latent, target) in enumerate(val_loader):
                latent = latent.to(self.device)
                target = target.to(self.device)
                
                pred = self.model(latent)
                
                # Dimension safety
                if pred.shape[1] != target.shape[1]:
                    min_dim = min(pred.shape[1], target.shape[1])
                    pred = pred[:, :min_dim]
                    target = target[:, :min_dim]
                
                loss = loss_fn(pred, target)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def _save_checkpoint(self, epoch, optimizer, scheduler, best_loss, history, path):
        """Save model checkpoint"""
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_val_loss': best_loss,
            'training_history': history,
            'model_config': {
                'latent_dim': self.latent_dim,
                'gene_dim': self.gene_dim,
                'hidden_dim': self.hidden_dim
            }
        }, path)
    
    def predict(self, latent_data: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """
        Predict gene expression from latent variables
        
        Args:
            latent_data: Latent variables [n_samples, latent_dim]
            batch_size: Prediction batch size
        
        Returns:
            expression: Predicted expression [n_samples, gene_dim]
        """
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Predictions may be inaccurate.")
        
        self.model.eval()
        
        # Input validation
        if latent_data.shape[1] != self.latent_dim:
            raise ValueError(f"Latent dimension mismatch: expected {self.latent_dim}, got {latent_data.shape[1]}")
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
        # Predict in batches to save memory
        predictions = []
        with torch.no_grad():
            for i in range(0, len(latent_data), batch_size):
                batch_latent = latent_data[i:i+batch_size].to(self.device)
                batch_pred = self.model(batch_latent)
                predictions.append(batch_pred.cpu())
        
        return torch.cat(predictions).numpy()
    
    def load_model(self, model_path: str):
        """Load pre-trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Check model configuration
        if 'model_config' in checkpoint:
            config = checkpoint['model_config']
            if (config['latent_dim'] != self.latent_dim or 
                config['gene_dim'] != self.gene_dim):
                print("⚠️ Model configuration mismatch. Reinitializing model.")
                self.model = self._build_model()
                self.model.to(self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        
        print(f"✅ Model loaded successfully!")
        print(f"🏆 Best validation loss: {self.best_val_loss:.4f}")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'is_trained': self.is_trained,
            'best_val_loss': self.best_val_loss,
            'parameters': sum(p.numel() for p in self.model.parameters()),
            'latent_dim': self.latent_dim,
            'gene_dim': self.gene_dim,
            'hidden_dim': self.hidden_dim,
            'device': str(self.device)
        }
'''
# Example usage
def example_usage():
    """Example demonstration with dimension safety"""
    
    # 1. Initialize decoder
    decoder = SimpleTranscriptomeDecoder(
        latent_dim=100,
        gene_dim=2000,  # Reduced for example
        hidden_dim=256
    )
    
    # 2. Generate example data with correct dimensions
    n_samples = 1000
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    
    # Create simulated expression data
    weights = np.random.randn(100, 2000) * 0.1
    expression_data = np.tanh(latent_data.dot(weights))
    expression_data = np.maximum(expression_data, 0)  # Non-negative
    
    print(f"📊 Data shapes: Latent {latent_data.shape}, Expression {expression_data.shape}")
    
    # 3. Train the model
    history = decoder.train(
        train_latent=latent_data,
        train_expression=expression_data,
        batch_size=32,
        num_epochs=50,
        learning_rate=1e-4
    )
    
    # 4. Make predictions
    test_latent = np.random.randn(10, 100).astype(np.float32)
    predictions = decoder.predict(test_latent)
    print(f"🔮 Prediction shape: {predictions.shape}")
    
    # 5. Get model info
    info = decoder.get_model_info()
    print(f"\n📋 Model Info:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    return decoder

if __name__ == "__main__":
    example_usage()
    
'''