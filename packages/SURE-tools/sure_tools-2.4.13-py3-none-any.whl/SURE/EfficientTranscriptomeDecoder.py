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
    Combines latest research techniques for optimal performance
    """
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512, 1024, 2048],
                 bottleneck_dim: int = 256,
                 num_experts: int = 8,
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
        
        # Initialize model with advanced architecture
        self.model = self._build_advanced_model()
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
        print(f"   - Estimated GPU Memory: ~6-8GB")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class SwiGLU(nn.Module):
        """SwiGLU activation - better than GELU (PaLM, LLaMA)"""
        def forward(self, x):
            x, gate = x.chunk(2, dim=-1)
            return x * F.silu(gate)
    
    class RMSNorm(nn.Module):
        """RMS Normalization - more stable than LayerNorm (GPT-3)"""
        def __init__(self, dim: int, eps: float = 1e-8):
            super().__init__()
            self.eps = eps
            self.weight = nn.Parameter(torch.ones(dim))
        
        def forward(self, x):
            norm_x = x.norm(2, dim=-1, keepdim=True)
            rms_x = norm_x * (x.shape[-1] ** -0.5)
            return x / (rms_x + self.eps) * self.weight
    
    class MixtureOfExperts(nn.Module):
        """Mixture of Experts for conditional computation"""
        def __init__(self, input_dim: int, expert_dim: int, num_experts: int):
            super().__init__()
            self.num_experts = num_experts
            self.experts = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(input_dim, expert_dim),
                    nn.Dropout(0.1),
                    nn.Linear(expert_dim, input_dim)
                ) for _ in range(num_experts)
            ])
            self.gate = nn.Linear(input_dim, num_experts)
            self.expert_dim = expert_dim
        
        def forward(self, x):
            # Gate network
            gate_logits = self.gate(x)
            gate_weights = F.softmax(gate_logits, dim=-1)
            
            # Expert outputs
            expert_outputs = []
            for i, expert in enumerate(self.experts):
                expert_out = expert(x)
                expert_outputs.append(expert_out.unsqueeze(-1))
            
            # Combine expert outputs
            expert_outputs = torch.cat(expert_outputs, dim=-1)
            output = torch.einsum('bd, bde -> be', gate_weights, expert_outputs)
            
            return output + x  # Residual connection
    
    class AdaptiveBottleneck(nn.Module):
        """Adaptive bottleneck for memory efficiency"""
        def __init__(self, input_dim: int, bottleneck_dim: int, output_dim: int):
            super().__init__()
            self.compress = nn.Linear(input_dim, bottleneck_dim)
            self.norm1 = EfficientTranscriptomeDecoder.RMSNorm(bottleneck_dim)
            self.expand = nn.Linear(bottleneck_dim, output_dim)
            self.norm2 = EfficientTranscriptomeDecoder.RMSNorm(output_dim)
            self.dropout = nn.Dropout(0.1)
            
        def forward(self, x):
            # Compress
            compressed = self.compress(x)
            compressed = self.norm1(compressed)
            compressed = F.silu(compressed)
            compressed = self.dropout(compressed)
            
            # Expand
            expanded = self.expand(compressed)
            expanded = self.norm2(expanded)
            
            return expanded
    
    class GeneSpecificProjection(nn.Module):
        """Gene-specific projection with weight sharing"""
        def __init__(self, latent_dim: int, gene_dim: int, proj_dim: int = 64):
            super().__init__()
            self.proj_dim = proj_dim
            self.gene_embeddings = nn.Parameter(torch.randn(gene_dim, proj_dim) * 0.02)
            self.latent_projection = nn.Linear(latent_dim, proj_dim)
            self.output_layer = nn.Linear(proj_dim, 1)
            
        def forward(self, latent):
            batch_size = latent.shape[0]
            
            # Project latent to gene space
            latent_proj = self.latent_projection(latent)  # [batch_size, proj_dim]
            
            # Efficient matrix multiplication
            gene_output = torch.matmul(latent_proj, self.gene_embeddings.T)  # [batch_size, gene_dim]
            
            return gene_output
    
    class AdvancedDecoder(nn.Module):
        """Advanced decoder combining multiple techniques"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dims: List[int], 
                    bottleneck_dim: int, num_experts: int, dropout_rate: float):
            super().__init__()
            
            # Initial projection
            self.input_projection = nn.Sequential(
                nn.Linear(latent_dim, hidden_dims[0]),
                EfficientTranscriptomeDecoder.RMSNorm(hidden_dims[0]),
                nn.SiLU(),
                nn.Dropout(dropout_rate)
            )
            
            # Main processing blocks
            self.blocks = nn.ModuleList()
            current_dim = hidden_dims[0]
            
            for i, hidden_dim in enumerate(hidden_dims[1:], 1):
                block = nn.ModuleList([
                    # Mixture of Experts
                    EfficientTranscriptomeDecoder.MixtureOfExperts(current_dim, hidden_dim, num_experts),
                    
                    # Adaptive Bottleneck
                    EfficientTranscriptomeDecoder.AdaptiveBottleneck(current_dim, bottleneck_dim, hidden_dim),
                    
                    # SwiGLU activation
                    nn.Sequential(
                        nn.Linear(hidden_dim, hidden_dim * 2),
                        EfficientTranscriptomeDecoder.SwiGLU(),
                        nn.Dropout(dropout_rate)
                    )
                ])
                self.blocks.append(block)
                current_dim = hidden_dim
            
            # Gene-specific projection
            self.gene_projection = EfficientTranscriptomeDecoder.GeneSpecificProjection(
                current_dim, gene_dim, proj_dim=128
            )
            
            # Output scaling
            self.output_scale = nn.Parameter(torch.ones(1))
            self.output_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _init_weights(self):
            """Advanced weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    # Kaiming init for SiLU/SwiGLU
                    nn.init.kaiming_normal_(module.weight, nonlinearity='linear')
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, x):
            # Initial projection
            x = self.input_projection(x)
            
            # Process through blocks
            for block in self.blocks:
                # Mixture of Experts
                expert_out = block[0](x)
                
                # Adaptive Bottleneck
                bottleneck_out = block[1](expert_out)
                
                # SwiGLU activation with residual
                swiglu_out = block[2](bottleneck_out)
                x = x + swiglu_out  # Residual connection
            
            # Final gene projection
            output = self.gene_projection(x)
            
            # Ensure non-negative output
            output = F.softplus(output * self.output_scale + self.output_bias)
            
            return output
    
    def _build_advanced_model(self):
        """Build the advanced decoder model"""
        return self.AdvancedDecoder(
            self.latent_dim, self.gene_dim, self.hidden_dims,
            self.bottleneck_dim, self.num_experts, self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 16,  # Smaller batches for memory efficiency
              num_epochs: int = 200,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'efficient_decoder.pth') -> Dict:
        """
        Train with advanced optimization techniques
        
        Args:
            train_latent: Training latent variables
            train_expression: Training expression data
            val_latent: Validation latent variables
            val_expression: Validation expression data
            batch_size: Batch size (optimized for memory)
            num_epochs: Number of epochs
            learning_rate: Learning rate
            checkpoint_path: Model save path
        """
        print("🚀 Starting Advanced Training...")
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, pin_memory=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, pin_memory=True)
        else:
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, pin_memory=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, pin_memory=True)
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"📊 Batch size: {batch_size}")
        
        # Advanced optimizer configuration
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.1,  # Stronger regularization
            betas=(0.9, 0.95),  # Tuned betas
            eps=1e-8
        )
        
        # Cosine annealing with warmup
        scheduler = optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=learning_rate * 5,
            epochs=num_epochs,
            steps_per_epoch=len(train_loader),
            pct_start=0.1,
            div_factor=10.0,
            final_div_factor=100.0
        )
        
        # Advanced loss function
        def advanced_loss(pred, target):
            # 1. MSE loss for overall accuracy
            mse_loss = F.mse_loss(pred, target)
            
            # 2. Poisson loss for count data
            poisson_loss = (pred - target * torch.log(pred + 1e-8)).mean()
            
            # 3. Correlation loss for pattern matching
            correlation_loss = 1 - self._pearson_correlation(pred, target)
            
            # 4. Sparsity loss for realistic distribution
            sparsity_loss = F.mse_loss(
                (pred < 1e-3).float().mean(),
                torch.tensor(0.85, device=pred.device)  # Target sparsity
            )
            
            # 5. Spectral loss for smoothness
            spectral_loss = self._spectral_loss(pred, target)
            
            # Weighted combination
            total_loss = (mse_loss + 0.3 * poisson_loss + 0.2 * correlation_loss + 
                         0.1 * sparsity_loss + 0.05 * spectral_loss)
            
            return total_loss, {
                'mse': mse_loss.item(),
                'poisson': poisson_loss.item(),
                'correlation': correlation_loss.item(),
                'sparsity': sparsity_loss.item(),
                'spectral': spectral_loss.item()
            }
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'train_mse': [], 'val_mse': [],
            'train_correlation': [], 'val_correlation': [],
            'learning_rates': [], 'grad_norms': []
        }
        
        best_val_loss = float('inf')
        patience = 25
        patience_counter = 0
        
        print("\n📈 Starting training with advanced techniques...")
        for epoch in range(1, num_epochs + 1):
            # Training phase
            train_loss, train_components, grad_norm = self._train_epoch_advanced(
                train_loader, optimizer, scheduler, advanced_loss
            )
            
            # Validation phase
            val_loss, val_components = self._validate_epoch_advanced(val_loader, advanced_loss)
            
            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_mse'].append(train_components['mse'])
            history['val_mse'].append(val_components['mse'])
            history['train_correlation'].append(train_components['correlation'])
            history['val_correlation'].append(val_components['correlation'])
            history['learning_rates'].append(optimizer.param_groups[0]['lr'])
            history['grad_norms'].append(grad_norm)
            
            # Print detailed progress
            if epoch % 10 == 0 or epoch == 1:
                lr = optimizer.param_groups[0]['lr']
                print(f"📍 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train: {train_loss:.4f} | "
                      f"Val: {val_loss:.4f} | "
                      f"Corr: {val_components['correlation']:.4f} | "
                      f"LR: {lr:.2e} | "
                      f"Grad: {grad_norm:.4f}")
            
            # Early stopping with patience
            if val_loss < best_val_loss:
                best_val_loss = val_loss
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
        """Create memory-efficient dataset"""
        class EfficientDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return EfficientDataset(latent_data, expression_data)
    
    def _pearson_correlation(self, pred, target):
        """Calculate Pearson correlation"""
        pred_centered = pred - pred.mean(dim=1, keepdim=True)
        target_centered = target - target.mean(dim=1, keepdim=True)
        
        numerator = (pred_centered * target_centered).sum(dim=1)
        denominator = torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * torch.sqrt(torch.sum(target_centered ** 2, dim=1))
        
        return (numerator / (denominator + 1e-8)).mean()
    
    def _spectral_loss(self, pred, target):
        """Spectral loss for frequency domain matching"""
        pred_fft = torch.fft.fft(pred, dim=1)
        target_fft = torch.fft.fft(target, dim=1)
        
        magnitude_loss = F.mse_loss(torch.abs(pred_fft), torch.abs(target_fft))
        phase_loss = F.mse_loss(torch.angle(pred_fft), torch.angle(target_fft))
        
        return magnitude_loss + 0.5 * phase_loss
    
    def _train_epoch_advanced(self, train_loader, optimizer, scheduler, loss_fn):
        """Advanced training with gradient accumulation"""
        self.model.train()
        total_loss = 0
        total_components = {'mse': 0, 'poisson': 0, 'correlation': 0, 'sparsity': 0, 'spectral': 0}
        grad_norms = []
        
        # Gradient accumulation for effective larger batch size
        accumulation_steps = 4
        optimizer.zero_grad()
        
        for i, (latent, target) in enumerate(train_loader):
            latent = latent.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            
            # Forward pass with mixed precision
            with torch.cuda.amp.autocast():  # Mixed precision for memory efficiency
                pred = self.model(latent)
                loss, components = loss_fn(pred, target)
            
            # Scale loss for gradient accumulation
            loss = loss / accumulation_steps
            loss.backward()
            
            # Gradient accumulation
            if (i + 1) % accumulation_steps == 0:
                # Gradient clipping
                grad_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                
                grad_norms.append(grad_norm.item())
            
            # Accumulate losses
            total_loss += loss.item() * accumulation_steps
            for key in total_components:
                total_components[key] += components[key]
        
        # Average metrics
        num_batches = len(train_loader)
        avg_loss = total_loss / num_batches
        avg_components = {key: value / num_batches for key, value in total_components.items()}
        avg_grad_norm = np.mean(grad_norms) if grad_norms else 0.0
        
        return avg_loss, avg_components, avg_grad_norm
    
    def _validate_epoch_advanced(self, val_loader, loss_fn):
        """Advanced validation"""
        self.model.eval()
        total_loss = 0
        total_components = {'mse': 0, 'poisson': 0, 'correlation': 0, 'sparsity': 0, 'spectral': 0}
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device, non_blocking=True)
                target = target.to(self.device, non_blocking=True)
                
                pred = self.model(latent)
                loss, components = loss_fn(pred, target)
                
                total_loss += loss.item()
                for key in total_components:
                    total_components[key] += components[key]
        
        num_batches = len(val_loader)
        avg_loss = total_loss / num_batches
        avg_components = {key: value / num_batches for key, value in total_components.items()}
        
        return avg_loss, avg_components
    
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
    
    def predict(self, latent_data: np.ndarray, batch_size: int = 16) -> np.ndarray:
        """Memory-efficient prediction"""
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Predictions may be inaccurate.")
        
        self.model.eval()
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
        predictions = []
        with torch.no_grad():
            for i in range(0, len(latent_data), batch_size):
                batch_latent = latent_data[i:i+batch_size].to(self.device)
                
                with torch.cuda.amp.autocast():  # Mixed precision for memory
                    batch_pred = self.model(batch_latent)
                
                predictions.append(batch_pred.cpu())
                
                # Clear memory
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
        return torch.cat(predictions).numpy()
    
    def load_model(self, model_path: str):
        """Load pre-trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        print(f"✅ Model loaded! Best val loss: {self.best_val_loss:.4f}")

'''
# Example usage
def example_usage():
    """Demonstrate the advanced decoder"""
    
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
        batch_size=16,
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