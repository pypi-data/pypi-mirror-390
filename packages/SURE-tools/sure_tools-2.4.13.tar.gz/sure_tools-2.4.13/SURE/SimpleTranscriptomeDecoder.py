import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class SimpleTranscriptomeDecoder:
    """MLP-based transcriptome decoder for latent to expression mapping"""
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512, 1024, 2048, 4096],
                 dropout_rate: float = 0.1,
                 device: str = None):
        """
        Multi-Layer Perceptron based decoder for transcriptome prediction
        
        Args:
            latent_dim: Latent variable dimension
            gene_dim: Number of genes (full transcriptome)
            hidden_dims: List of hidden layer dimensions
            dropout_rate: Dropout rate for regularization
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.gene_dim = gene_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout_rate
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        self.model = self._build_mlp_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        
        print(f"🚀 SimpleTranscriptomeDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimensions: {hidden_dims}")
        print(f"   - Dropout Rate: {dropout_rate}")
        print(f"   - Device: {self.device}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class MLPModel(nn.Module):
        """MLP-based decoder architecture"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dims: List[int], dropout_rate: float):
            super().__init__()
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            
            # Build the MLP layers
            layers = []
            input_dim = latent_dim
            
            # Encoder part: expand latent dimension
            for hidden_dim in hidden_dims:
                layers.extend([
                    nn.Linear(input_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.GELU(),
                    nn.Dropout(dropout_rate)
                ])
                input_dim = hidden_dim
            
            # Decoder part: project to gene dimension
            # Reverse the hidden_dims for decoder
            decoder_dims = hidden_dims[::-1]
            for i, hidden_dim in enumerate(decoder_dims[1:], 1):
                layers.extend([
                    nn.Linear(input_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.GELU(),
                    nn.Dropout(dropout_rate)
                ])
                input_dim = hidden_dim
            
            # Final projection to gene dimension
            layers.append(nn.Linear(input_dim, gene_dim))
            
            self.mlp_layers = nn.Sequential(*layers)
            
            # Output scaling parameters
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
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # Pass through MLP layers
            output = self.mlp_layers(x)
            
            # Ensure non-negative output with softplus
            output = F.softplus(output * self.output_scale + self.output_bias)
            
            return output
    
    class ResidualMLPModel(nn.Module):
        """Residual MLP decoder with skip connections"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dims: List[int], dropout_rate: float):
            super().__init__()
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            
            # Build residual blocks
            self.blocks = nn.ModuleList()
            input_dim = latent_dim
            
            for hidden_dim in hidden_dims:
                block = self._build_residual_block(input_dim, hidden_dim, dropout_rate)
                self.blocks.append(block)
                input_dim = hidden_dim
            
            # Final projection to gene dimension
            self.final_projection = nn.Sequential(
                nn.Linear(input_dim, input_dim // 2),
                nn.GELU(),
                nn.Dropout(dropout_rate),
                nn.Linear(input_dim // 2, gene_dim)
            )
            
            # Output parameters
            self.output_scale = nn.Parameter(torch.ones(1))
            self.output_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _build_residual_block(self, input_dim: int, hidden_dim: int, dropout_rate: float) -> nn.Module:
            """Build a residual block with skip connection"""
            return nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim, hidden_dim),  # Residual path
                nn.BatchNorm1d(hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout_rate),
            )
        
        def _init_weights(self):
            """Weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.kaiming_uniform_(module.weight, nonlinearity='relu')
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # Initial projection
            identity = x
            
            for block in self.blocks:
                # Residual connection
                out = block(x)
                # Skip connection if dimensions match, otherwise project
                if out.shape[1] == identity.shape[1]:
                    x = out + identity
                else:
                    x = out
                identity = x
            
            # Final projection
            output = self.final_projection(x)
            output = F.softplus(output * self.output_scale + self.output_bias)
            
            return output
    
    def _build_mlp_model(self):
        """Build the MLP model - 修正了方法名冲突"""
        # Use simple MLP model for stability
        return self.MLPModel(
            self.latent_dim, 
            self.gene_dim, 
            self.hidden_dims, 
            self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 100,
              learning_rate: float = 1e-4,
              weight_decay: float = 1e-5,
              checkpoint_path: str = 'mlp_decoder.pth') -> Dict:
        """
        Train the MLP decoder model
        
        Args:
            train_latent: Training latent variables [n_samples, latent_dim]
            train_expression: Training expression data [n_samples, gene_dim]
            val_latent: Validation latent variables (optional)
            val_expression: Validation expression data (optional)
            batch_size: Batch size for training
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            weight_decay: Weight decay for regularization
            checkpoint_path: Path to save the best model
        
        Returns:
            Training history dictionary
        """
        print("🚀 Starting MLP Decoder Training...")
        
        # Data validation
        self._validate_input_data(train_latent, train_expression, "Training")
        if val_latent is not None and val_expression is not None:
            self._validate_input_data(val_latent, val_expression, "Validation")
        
        # Create datasets and data loaders
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
            print(f"📈 Using provided validation data: {len(val_dataset)} samples")
        else:
            # Auto split
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            print(f"📈 Auto-split validation: {val_size} samples")
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"📊 Batch size: {batch_size}")
        
        # Optimizer configuration
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.999)
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.OneCycleLR(
            optimizer, 
            max_lr=learning_rate * 10,
            epochs=num_epochs,
            steps_per_epoch=len(train_loader)
        )
        
        # Loss function combining MSE and Poisson loss
        def combined_loss(pred, target):
            mse_loss = F.mse_loss(pred, target)
            poisson_loss = (pred - target * torch.log(pred + 1e-8)).mean()
            correlation_loss = 1 - self._pearson_correlation(pred, target)
            return mse_loss + 0.3 * poisson_loss + 0.1 * correlation_loss
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'train_mse': [], 'val_mse': [],
            'train_correlation': [], 'val_correlation': [],
            'learning_rates': []
        }
        
        best_val_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        print("\n📈 Starting training loop...")
        for epoch in range(1, num_epochs + 1):
            # Training phase
            train_metrics = self._train_epoch(train_loader, optimizer, scheduler, combined_loss)
            
            # Validation phase
            val_metrics = self._validate_epoch(val_loader, combined_loss)
            
            # Record history
            history['train_loss'].append(train_metrics['total_loss'])
            history['train_mse'].append(train_metrics['mse_loss'])
            history['train_correlation'].append(train_metrics['correlation'])
            
            history['val_loss'].append(val_metrics['val_loss'])
            history['val_mse'].append(val_metrics['val_mse'])
            history['val_correlation'].append(val_metrics['val_correlation'])
            
            history['learning_rates'].append(optimizer.param_groups[0]['lr'])
            
            # Print progress
            if epoch % 10 == 0 or epoch == 1:
                print(f"📍 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train Loss: {train_metrics['total_loss']:.4f} | "
                      f"Val Loss: {val_metrics['val_loss']:.4f} | "
                      f"Correlation: {val_metrics['val_correlation']:.4f} | "
                      f"LR: {optimizer.param_groups[0]['lr']:.2e}")
            
            # Early stopping and model saving
            if val_metrics['val_loss'] < best_val_loss:
                best_val_loss = val_metrics['val_loss']
                patience_counter = 0
                self._save_checkpoint(epoch, optimizer, scheduler, best_val_loss, history, checkpoint_path)
                if epoch % 20 == 0:
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
        
        return history
    
    def _validate_input_data(self, latent_data: np.ndarray, expression_data: np.ndarray, data_type: str):
        """Validate input data dimensions and types"""
        assert latent_data.shape[1] == self.latent_dim, \
            f"{data_type} latent dimension mismatch: expected {self.latent_dim}, got {latent_data.shape[1]}"
        assert expression_data.shape[1] == self.gene_dim, \
            f"{data_type} gene dimension mismatch: expected {self.gene_dim}, got {expression_data.shape[1]}"
        assert latent_data.shape[0] == expression_data.shape[0], \
            f"{data_type} sample count mismatch"
        print(f"✅ {data_type} data validated: {latent_data.shape[0]} samples")
    
    def _create_dataset(self, latent_data: np.ndarray, expression_data: np.ndarray) -> Dataset:
        """Create PyTorch dataset"""
        class TranscriptomeDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return TranscriptomeDataset(latent_data, expression_data)
    
    def _pearson_correlation(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Calculate Pearson correlation coefficient"""
        pred_centered = pred - pred.mean(dim=1, keepdim=True)
        target_centered = target - target.mean(dim=1, keepdim=True)
        
        numerator = (pred_centered * target_centered).sum(dim=1)
        denominator = torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * torch.sqrt(torch.sum(target_centered ** 2, dim=1))
        
        return (numerator / (denominator + 1e-8)).mean()
    
    def _train_epoch(self, train_loader, optimizer, scheduler, loss_fn):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        total_mse = 0
        total_correlation = 0
        
        for latent, target in train_loader:
            latent = latent.to(self.device)
            target = target.to(self.device)
            
            optimizer.zero_grad()
            pred = self.model(latent)
            
            loss = loss_fn(pred, target)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            
            # Calculate metrics
            mse_loss = F.mse_loss(pred, target).item()
            correlation = self._pearson_correlation(pred, target).item()
            
            total_loss += loss.item()
            total_mse += mse_loss
            total_correlation += correlation
        
        num_batches = len(train_loader)
        return {
            'total_loss': total_loss / num_batches,
            'mse_loss': total_mse / num_batches,
            'correlation': total_correlation / num_batches
        }
    
    def _validate_epoch(self, val_loader, loss_fn):
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        total_mse = 0
        total_correlation = 0
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device)
                target = target.to(self.device)
                
                pred = self.model(latent)
                
                loss = loss_fn(pred, target)
                mse_loss = F.mse_loss(pred, target).item()
                correlation = self._pearson_correlation(pred, target).item()
                
                total_loss += loss.item()
                total_mse += mse_loss
                total_correlation += correlation
        
        num_batches = len(val_loader)
        return {
            'val_loss': total_loss / num_batches,
            'val_mse': total_mse / num_batches,
            'val_correlation': total_correlation / num_batches
        }
    
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
                'hidden_dims': self.hidden_dims,
                'dropout_rate': self.dropout_rate
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
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
        # Predict in batches
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
                self.model = self._build_mlp_model()
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
            'hidden_dims': self.hidden_dims,
            'dropout_rate': self.dropout_rate,
            'device': str(self.device)
        }

'''
# Example usage
def example_usage():
    """Example demonstration of MLP decoder"""
    
    # 1. Initialize decoder
    decoder = SimpleTranscriptomeDecoder(
        latent_dim=100,
        gene_dim=2000,  # Reduced for example
        hidden_dims=[256, 512, 1024],  # Progressive expansion
        dropout_rate=0.1
    )
    
    # 2. Generate example data
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