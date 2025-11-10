import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Optional, Tuple
import math
import warnings
warnings.filterwarnings('ignore')

class EfficientTranscriptomeDecoder:
    """
    High-performance, memory-efficient transcriptome decoder
    Fixed version with corrected RMSNorm implementation
    """
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512, 1024, 2048],
                 bottleneck_dim: int = 256,
                 num_experts: int = 4,
                 dropout_rate: float = 0.1,
                 device: str = None):
        """
        Advanced decoder combining multiple state-of-the-art techniques
        
        Args:
            latent_dim: Latent variable dimension
            gene_dim: Number of genes (full transcriptome)
            hidden_dims: Hidden layer dimensions
            bottleneck_dim: Bottleneck dimension for memory efficiency
            num_experts: Number of mixture-of-experts
            dropout_rate: Dropout rate
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.gene_dim = gene_dim
        self.hidden_dims = hidden_dims
        self.bottleneck_dim = bottleneck_dim
        self.num_experts = num_experts
        self.dropout_rate = dropout_rate
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model with corrected architecture
        self.model = self._build_corrected_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        
        print(f"🚀 EfficientTranscriptomeDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimensions: {hidden_dims}")
        print(f"   - Bottleneck Dimension: {bottleneck_dim}")
        print(f"   - Number of Experts: {num_experts}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class CorrectedRMSNorm(nn.Module):
        """Corrected RMS Normalization with proper dimension handling"""
        def __init__(self, dim: int, eps: float = 1e-8):
            super().__init__()
            self.eps = eps
            self.dim = dim
            self.weight = nn.Parameter(torch.ones(dim))  # Correct: weight has same dim as input
        
        def forward(self, x):
            # Ensure input has the right dimension
            if x.size(-1) != self.dim:
                raise ValueError(f"Input dimension {x.size(-1)} doesn't match RMSNorm dimension {self.dim}")
            
            # Calculate RMS
            rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
            # Normalize and apply weight
            return x / rms * self.weight
    
    class SimplifiedSwiGLU(nn.Module):
        """Simplified SwiGLU activation"""
        def forward(self, x):
            # Split into two parts
            x, gate = x.chunk(2, dim=-1)
            return x * F.silu(gate)
    
    class MemoryEfficientBottleneck(nn.Module):
        """Memory-efficient bottleneck with corrected dimensions"""
        def __init__(self, input_dim: int, bottleneck_dim: int, output_dim: int):
            super().__init__()
            # Ensure proper dimension matching
            self.compress = nn.Linear(input_dim, bottleneck_dim)
            self.norm1 = EfficientTranscriptomeDecoder.CorrectedRMSNorm(bottleneck_dim)
            self.expand = nn.Linear(bottleneck_dim, output_dim)
            self.norm2 = EfficientTranscriptomeDecoder.CorrectedRMSNorm(output_dim)
            self.activation = nn.SiLU()
            self.dropout = nn.Dropout(0.1)
            
        def forward(self, x):
            # Compress
            compressed = self.compress(x)
            compressed = self.norm1(compressed)
            compressed = self.activation(compressed)
            compressed = self.dropout(compressed)
            
            # Expand
            expanded = self.expand(compressed)
            expanded = self.norm2(expanded)
            
            return expanded
    
    class StableMixtureOfExperts(nn.Module):
        """Stable mixture of experts without dimension issues"""
        def __init__(self, input_dim: int, num_experts: int = 4):
            super().__init__()
            self.num_experts = num_experts
            self.input_dim = input_dim
            
            # Shared expert with different scaling factors
            self.shared_expert = nn.Sequential(
                nn.Linear(input_dim, input_dim * 2),
                nn.SiLU(),
                nn.Dropout(0.1),
                nn.Linear(input_dim * 2, input_dim)
            )
            
            # Gating network
            self.gate = nn.Sequential(
                nn.Linear(input_dim, num_experts * 4),
                nn.SiLU(),
                nn.Linear(num_experts * 4, num_experts)
            )
            
        def forward(self, x):
            # Get gate weights
            gate_weights = F.softmax(self.gate(x), dim=-1)  # [batch, num_experts]
            
            # Process through shared expert
            expert_output = self.shared_expert(x)  # [batch, input_dim]
            
            # Apply expert-specific scaling
            weighted_output = torch.zeros_like(expert_output)
            for i in range(self.num_experts):
                expert_scale = 0.5 + 0.5 * i  # Different scaling for each expert
                expert_contribution = expert_output * expert_scale
                expert_weight = gate_weights[:, i].unsqueeze(-1)  # [batch, 1]
                weighted_output += expert_weight * expert_contribution
            
            # Residual connection
            return x + weighted_output
    
    class CorrectedDecoder(nn.Module):
        """Corrected decoder with proper dimension handling"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dims: List[int], 
                     bottleneck_dim: int, num_experts: int, dropout_rate: float):
            super().__init__()
            
            # Input projection
            self.input_projection = nn.Sequential(
                nn.Linear(latent_dim, hidden_dims[0]),
                EfficientTranscriptomeDecoder.CorrectedRMSNorm(hidden_dims[0]),
                nn.SiLU(),
                nn.Dropout(dropout_rate)
            )
            
            # Main processing blocks
            self.blocks = nn.ModuleList()
            current_dim = hidden_dims[0]
            
            for i, next_dim in enumerate(hidden_dims[1:], 1):
                block = nn.ModuleDict({
                    'swiglu': nn.Sequential(
                        nn.Linear(current_dim, current_dim * 2),
                        EfficientTranscriptomeDecoder.SimplifiedSwiGLU(),
                        nn.Dropout(dropout_rate),
                        nn.Linear(current_dim, current_dim)  # Project back to same dimension
                    ),
                    'bottleneck': EfficientTranscriptomeDecoder.MemoryEfficientBottleneck(
                        current_dim, bottleneck_dim, next_dim
                    ),
                    'experts': EfficientTranscriptomeDecoder.StableMixtureOfExperts(
                        next_dim, num_experts
                    )
                })
                self.blocks.append(block)
                current_dim = next_dim
            
            # Final projection to gene dimension
            self.final_projection = nn.Sequential(
                nn.Linear(current_dim, current_dim * 2),
                nn.SiLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(current_dim * 2, gene_dim)
            )
            
            # Output parameters
            self.output_scale = nn.Parameter(torch.ones(1))
            self.output_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _init_weights(self):
            """Proper weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, x):
            # Input projection
            x = self.input_projection(x)
            
            # Process through blocks
            for block in self.blocks:
                # SwiGLU with residual
                residual = x
                x_swiglu = block['swiglu'](x)
                x = x + x_swiglu  # Residual connection
                
                # Bottleneck
                x = block['bottleneck'](x)
                
                # Mixture of Experts with residual
                x = block['experts'](x)
            
            # Final projection
            x = self.final_projection(x)
            
            # Ensure non-negative output
            x = F.softplus(x * self.output_scale + self.output_bias)
            
            return x
    
    def _build_corrected_model(self):
        """Build the corrected model"""
        return self.CorrectedDecoder(
            self.latent_dim, self.gene_dim, self.hidden_dims,
            self.bottleneck_dim, self.num_experts, self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 100,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'transcriptome_decoder.pth') -> Dict:
        """
        Train the corrected decoder
        """
        print("🚀 Starting Training...")
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, pin_memory=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, pin_memory=True)
            print(f"📈 Using provided validation data: {len(val_dataset)} samples")
        else:
            # Auto split
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, pin_memory=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, pin_memory=True)
            print(f"📈 Auto-split validation: {val_size} samples")
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"📊 Batch size: {batch_size}")
        
        # Optimizer
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            betas=(0.9, 0.999)
        )
        
        # Scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
        
        # Loss function
        def combined_loss(pred, target):
            mse_loss = F.mse_loss(pred, target)
            poisson_loss = (pred - target * torch.log(pred + 1e-8)).mean()
            correlation = self._pearson_correlation(pred, target)
            correlation_loss = 1 - correlation
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
            # Training
            train_metrics = self._train_epoch(train_loader, optimizer, combined_loss)
            
            # Validation
            val_metrics = self._validate_epoch(val_loader, combined_loss)
            
            # Update scheduler
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            # Record history
            history['train_loss'].append(train_metrics['loss'])
            history['val_loss'].append(val_metrics['loss'])
            history['train_mse'].append(train_metrics['mse'])
            history['val_mse'].append(val_metrics['mse'])
            history['train_correlation'].append(train_metrics['correlation'])
            history['val_correlation'].append(val_metrics['correlation'])
            history['learning_rates'].append(current_lr)
            
            # Print progress
            if epoch % 10 == 0 or epoch == 1:
                print(f"📍 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train Loss: {train_metrics['loss']:.4f} | "
                      f"Val Loss: {val_metrics['loss']:.4f} | "
                      f"Correlation: {val_metrics['correlation']:.4f} | "
                      f"LR: {current_lr:.2e}")
            
            # Early stopping
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
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
    
    def _create_dataset(self, latent_data, expression_data):
        """Create dataset"""
        class SimpleDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return SimpleDataset(latent_data, expression_data)
    
    def _pearson_correlation(self, pred, target):
        """Calculate Pearson correlation"""
        pred_centered = pred - pred.mean(dim=1, keepdim=True)
        target_centered = target - target.mean(dim=1, keepdim=True)
        
        numerator = (pred_centered * target_centered).sum(dim=1)
        denominator = torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * torch.sqrt(torch.sum(target_centered ** 2, dim=1))
        
        return (numerator / (denominator + 1e-8)).mean()
    
    def _train_epoch(self, train_loader, optimizer, loss_fn):
        """Train one epoch"""
        self.model.train()
        total_loss = 0
        total_mse = 0
        total_correlation = 0
        
        for latent, target in train_loader:
            latent = latent.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            
            optimizer.zero_grad()
            pred = self.model(latent)
            
            loss = loss_fn(pred, target)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            
            # Calculate metrics
            mse_loss = F.mse_loss(pred, target).item()
            correlation = self._pearson_correlation(pred, target).item()
            
            total_loss += loss.item()
            total_mse += mse_loss
            total_correlation += correlation
        
        num_batches = len(train_loader)
        return {
            'loss': total_loss / num_batches,
            'mse': total_mse / num_batches,
            'correlation': total_correlation / num_batches
        }
    
    def _validate_epoch(self, val_loader, loss_fn):
        """Validate one epoch"""
        self.model.eval()
        total_loss = 0
        total_mse = 0
        total_correlation = 0
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device, non_blocking=True)
                target = target.to(self.device, non_blocking=True)
                
                pred = self.model(latent)
                loss = loss_fn(pred, target)
                mse_loss = F.mse_loss(pred, target).item()
                correlation = self._pearson_correlation(pred, target).item()
                
                total_loss += loss.item()
                total_mse += mse_loss
                total_correlation += correlation
        
        num_batches = len(val_loader)
        return {
            'loss': total_loss / num_batches,
            'mse': total_mse / num_batches,
            'correlation': total_correlation / num_batches
        }
    
    def _save_checkpoint(self, epoch, optimizer, scheduler, best_loss, history, path):
        """Save checkpoint"""
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
                'bottleneck_dim': self.bottleneck_dim,
                'num_experts': self.num_experts
            }
        }, path)
    
    def predict(self, latent_data: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """Predict gene expression"""
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Predictions may be inaccurate.")
        
        self.model.eval()
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
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
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        print(f"✅ Model loaded! Best val loss: {self.best_val_loss:.4f}")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'is_trained': self.is_trained,
            'best_val_loss': self.best_val_loss,
            'parameters': sum(p.numel() for p in self.model.parameters()),
            'latent_dim': self.latent_dim,
            'gene_dim': self.gene_dim,
            'hidden_dims': self.hidden_dims,
            'device': str(self.device)
        }

'''
# Example usage
def example_usage():
    """Example demonstration"""
    
    # Initialize decoder
    decoder = EfficientTranscriptomeDecoder(
        latent_dim=100,
        gene_dim=2000,  # Reduced for example
        hidden_dims=[256, 512, 1024],
        bottleneck_dim=128,
        num_experts=4,
        dropout_rate=0.1
    )
    
    # Generate example data
    n_samples = 1000
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    
    # Simulate expression data
    weights = np.random.randn(100, 2000) * 0.1
    expression_data = np.tanh(latent_data.dot(weights))
    expression_data = np.maximum(expression_data, 0)
    
    print(f"📊 Data shapes: Latent {latent_data.shape}, Expression {expression_data.shape}")
    
    # Train
    history = decoder.train(
        train_latent=latent_data,
        train_expression=expression_data,
        batch_size=32,
        num_epochs=50
    )
    
    # Predict
    test_latent = np.random.randn(10, 100).astype(np.float32)
    predictions = decoder.predict(test_latent)
    print(f"🔮 Prediction shape: {predictions.shape}")
    
    return decoder

if __name__ == "__main__":
    example_usage()
'''