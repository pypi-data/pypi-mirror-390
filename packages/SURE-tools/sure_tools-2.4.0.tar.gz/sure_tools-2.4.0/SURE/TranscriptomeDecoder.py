import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Any, Union
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class TranscriptomeDecoder:
    """Transcriptome Prediction Decoder"""
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dim: int = 1024,
                 device: str = None):
        """
        Args:
            latent_dim: Latent variable dimension
            gene_dim: Number of genes (full transcriptome ~60,000)
            hidden_dim: Hidden layer dimension
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
        
        print(f"🚀 TranscriptomeDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimension: {hidden_dim}")
        print(f"   - Device: {self.device}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class HyperNet(nn.Module):
        """HyperNetwork: Generates personalized weights for each gene"""
        def __init__(self, latent_dim: int, hidden_dim: int, output_dim: int):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, output_dim)
            )
            
        def forward(self, x):
            return self.net(x)
    
    class MultiScaleAttention(nn.Module):
        """Multi-scale attention mechanism"""
        def __init__(self, dim: int, num_heads: int = 8, scales: List[int] = [1, 3, 5]):
            super().__init__()
            self.scales = scales
            self.attention_heads = nn.ModuleList([
                nn.MultiheadAttention(dim, num_heads, batch_first=True)
                for _ in scales
            ])
            self.scale_weights = nn.Parameter(torch.ones(len(scales)))
            self.out_proj = nn.Linear(dim * len(scales), dim)
            
        def forward(self, x):
            batch_size, seq_len, dim = x.shape
            
            scale_outputs = []
            for scale, attn in zip(self.scales, self.attention_heads):
                if scale > 1:
                    # Downsample
                    x_down = F.avg_pool1d(x.transpose(1, 2), kernel_size=scale, stride=scale)
                    x_down = x_down.transpose(1, 2)
                    attn_out, _ = attn(x_down, x_down, x_down)
                    # Upsample
                    attn_out = F.interpolate(attn_out.transpose(1, 2), size=seq_len)
                    attn_out = attn_out.transpose(1, 2)
                else:
                    attn_out, _ = attn(x, x, x)
                scale_outputs.append(attn_out)
            
            # Weighted fusion
            weighted_outputs = []
            for i, output in enumerate(scale_outputs):
                weight = torch.sigmoid(self.scale_weights[i])
                weighted_outputs.append(output * weight)
            
            combined = torch.cat(weighted_outputs, dim=-1)
            return self.out_proj(combined)
    
    class DynamicActivation(nn.Module):
        """Dynamic activation function"""
        def __init__(self, dim: int):
            super().__init__()
            self.alpha = nn.Parameter(torch.ones(1, dim))
            self.beta = nn.Parameter(torch.zeros(1, dim))
            self.gamma = nn.Parameter(torch.ones(1, dim))
            
        def forward(self, x):
            return self.alpha * F.elu(self.gamma * x + self.beta)
    
    class GeneSpecificNetwork(nn.Module):
        """Gene-specific processing network"""
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dim: int = 512):
            super().__init__()
            self.gene_embeddings = nn.Parameter(torch.randn(gene_dim, hidden_dim))
            self.hyper_net = TranscriptomeDecoder.HyperNet(latent_dim, hidden_dim, hidden_dim * 3)
            self.dynamic_activation = TranscriptomeDecoder.DynamicActivation(hidden_dim)
            
        def forward(self, latent, gene_features):
            batch_size = latent.shape[0]
            hyper_out = self.hyper_net(latent)
            w1, w2, w3 = hyper_out.chunk(3, dim=1)
            
            w1 = w1.unsqueeze(1)
            w2 = w2.unsqueeze(1)
            w3 = w3.unsqueeze(1)
            
            transformed = gene_features * w1 + w2
            transformed = self.dynamic_activation(transformed)
            transformed = transformed * w3
            
            return transformed
    
    class TransformerDecoderBlock(nn.Module):
        """Enhanced Transformer decoder block"""
        def __init__(self, dim: int, num_heads: int = 8, dropout: float = 0.1):
            super().__init__()
            self.self_attn = TranscriptomeDecoder.MultiScaleAttention(dim, num_heads)
            self.cross_attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
            
            self.norm1 = nn.LayerNorm(dim)
            self.norm2 = nn.LayerNorm(dim)
            self.norm3 = nn.LayerNorm(dim)
            
            self.mlp = nn.Sequential(
                nn.Linear(dim, dim * 4),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(dim * 4, dim),
                nn.Dropout(dropout)
            )
            self.dropout = nn.Dropout(dropout)
            
        def forward(self, x, memory=None):
            # Self-attention
            attn_out = self.self_attn(x)
            x = self.norm1(x + self.dropout(attn_out))
            
            # Cross-attention (if memory provided)
            if memory is not None:
                cross_out, _ = self.cross_attn(x, memory, memory)
                x = self.norm2(x + self.dropout(cross_out))
            
            # MLP
            mlp_out = self.mlp(x)
            x = self.norm3(x + self.dropout(mlp_out))
            
            return x
    
    class UltraDecoder(nn.Module):
        """Ultimate Decoder Model"""
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dim: int):
            super().__init__()
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            self.hidden_dim = hidden_dim
            
            # Latent variable expansion
            self.latent_expansion = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim * 4),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim * 4, hidden_dim * 2),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim * 2, hidden_dim),
            )
            
            # Gene embeddings
            self.gene_embeddings = nn.Parameter(torch.randn(gene_dim, hidden_dim))
            
            # Gene-specific networks
            self.gene_specific_networks = nn.ModuleList([
                TranscriptomeDecoder.GeneSpecificNetwork(latent_dim, gene_dim, hidden_dim)
                for _ in range(8)  # 8 gene-specific networks
            ])
            
            # Deep transformer layers
            self.transformer_layers = nn.ModuleList([
                TranscriptomeDecoder.TransformerDecoderBlock(hidden_dim, 16, 0.1)
                for _ in range(12)  # 12 transformer layers
            ])
            
            # Multi-scale output heads
            self.multi_scale_heads = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.GELU(),
                    nn.Linear(hidden_dim // 2, hidden_dim // 4),
                    nn.GELU(),
                    nn.Linear(hidden_dim // 4, 1)
                ) for _ in range(3)  # 3 output heads
            ])
            
            # Adaptive fusion gating
            self.fusion_gate = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.GELU(),
                nn.Linear(hidden_dim // 2, 3),
                nn.Softmax(dim=-1)
            )
            
            # Output processing
            self.output_norm = nn.LayerNorm(1)
            self.expression_scale = nn.Parameter(torch.ones(1))
            self.expression_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _init_weights(self):
            """Weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
                elif isinstance(module, nn.LayerNorm):
                    nn.init.zeros_(module.bias)
                    nn.init.ones_(module.weight)
        
        def forward(self, latent: torch.Tensor) -> torch.Tensor:
            batch_size = latent.shape[0]
            
            # 1. Latent variable expansion
            latent_expanded = self.latent_expansion(latent)
            
            # 2. Prepare gene sequence
            gene_embeds = self.gene_embeddings.unsqueeze(0).expand(batch_size, -1, -1)
            
            # 3. Gene-specific transformations
            gene_features = gene_embeds
            for gene_net in self.gene_specific_networks:
                gene_features = gene_net(latent, gene_features) + gene_features  # Residual connection
            
            # 4. Transformer processing
            x = gene_features
            for transformer in self.transformer_layers:
                x = transformer(x, memory=latent_expanded.unsqueeze(1))
            
            # 5. Multi-scale output prediction
            head_outputs = []
            for head in self.multi_scale_heads:
                head_out = head(x)  # [batch, gene_dim, 1]
                head_outputs.append(head_out)
            
            # 6. Adaptive fusion
            gate_weights = self.fusion_gate(x.mean(dim=1))  # [batch, 3]
            gate_weights = gate_weights.unsqueeze(-1).unsqueeze(-1)  # [batch, 3, 1, 1]
            
            # Weighted fusion
            final_output = torch.zeros(batch_size, self.gene_dim, 1, device=latent.device)
            for i, head_out in enumerate(head_outputs):
                final_output = final_output + gate_weights[:, i] * head_out
            
            # 7. Final processing
            final_output = final_output.squeeze(-1)  # [batch, gene_dim]
            final_output = self.output_norm(final_output.unsqueeze(-1)).squeeze(-1)
            
            # Ensure non-negative output
            final_output = F.softplus(final_output * self.expression_scale + self.expression_bias)
            
            return final_output
    
    def _build_model(self):
        """Build the model architecture"""
        return self.UltraDecoder(self.latent_dim, self.gene_dim, self.hidden_dim)
    
    def _create_loss_functions(self):
        """Create loss functions dictionary"""
        def mse_loss(pred, target):
            return F.mse_loss(pred, target)
        
        def poisson_loss(pred, target):
            return (pred - target * torch.log(pred + 1e-8)).mean()
        
        def correlation_loss(pred, target):
            pred_centered = pred - pred.mean(dim=1, keepdim=True)
            target_centered = target - target.mean(dim=1, keepdim=True)
            correlation = (pred_centered * target_centered).sum(dim=1) / (
                torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * 
                torch.sqrt(torch.sum(target_centered ** 2, dim=1)) + 1e-8
            )
            return 1 - correlation.mean()
        
        def sparsity_loss(pred, target_sparsity=0.85):
            actual_sparsity = (pred < 0.1).float().mean()
            return (actual_sparsity - target_sparsity) ** 2
        
        return {
            'mse': mse_loss,
            'poisson': poisson_loss,
            'correlation': correlation_loss,
            'sparsity': sparsity_loss
        }
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              val_ratio: float = 0.1,
              batch_size: int = 32,
              num_epochs: int = 100,
              learning_rate: float = 1e-4,
              weight_decay: float = 0.01,
              checkpoint_path: str = 'best_transcriptome_decoder.pth'):
        """
        Train the decoder model
        
        Args:
            train_latent: Training latent variables [n_samples, latent_dim]
            train_expression: Training expression data [n_samples, gene_dim]
            val_latent: Validation latent variables (optional)
            val_expression: Validation expression data (optional)
            val_ratio: Validation ratio if no validation data provided
            batch_size: Batch size for training
            num_epochs: Number of training epochs
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for regularization
            checkpoint_path: Path to save the best model
        """
        print("🚀 Starting TranscriptomeDecoder Training...")
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
            print(f"📊 Using provided validation data: {len(val_dataset)} samples")
        else:
            # Automatic validation split
            train_size = int((1 - val_ratio) * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            print(f"📊 Auto-split validation: {val_size} samples ({val_ratio*100:.1f}%)")
        
        print(f"📈 Training samples: {len(train_loader.dataset)}")
        print(f"📈 Validation samples: {len(val_loader.dataset)}")
        
        # Optimizer configuration
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.98)
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=learning_rate * 10,
            epochs=num_epochs,
            steps_per_epoch=len(train_loader),
            pct_start=0.1
        )
        
        # Loss functions
        loss_fns = self._create_loss_functions()
        loss_weights = {'mse': 1.0, 'poisson': 0.5, 'correlation': 0.3, 'sparsity': 0.2}
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'train_correlation': [], 'val_correlation': [],
            'learning_rates': [], 'grad_norms': []
        }
        
        best_val_loss = float('inf')
        patience = 15
        patience_counter = 0
        
        # Training loop
        for epoch in range(1, num_epochs + 1):
            print(f"\n{'='*60}")
            print(f"📍 Epoch {epoch}/{num_epochs}")
            print(f"{'='*60}")
            
            # Training phase
            train_metrics = self._train_epoch(
                train_loader, optimizer, scheduler, loss_fns, loss_weights, epoch
            )
            
            # Validation phase
            val_metrics = self._validate_epoch(val_loader, loss_fns)
            
            # Record history
            history['train_loss'].append(train_metrics['total_loss'])
            history['val_loss'].append(val_metrics['val_loss'])
            history['train_correlation'].append(train_metrics['correlation_loss'])
            history['val_correlation'].append(val_metrics['val_correlation'])
            history['learning_rates'].append(scheduler.get_last_lr()[0])
            history['grad_norms'].append(train_metrics['grad_norm'])
            
            # Print progress
            self._print_epoch_progress(epoch, num_epochs, train_metrics, val_metrics)
            
            # Early stopping and model saving
            if val_metrics['val_loss'] < best_val_loss:
                best_val_loss = val_metrics['val_loss']
                patience_counter = 0
                self._save_checkpoint(epoch, optimizer, scheduler, best_val_loss, history, checkpoint_path)
                print("💾 Best model saved!")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("🛑 Early stopping triggered!")
                    break
        
        # Training completed
        self.is_trained = True
        self.training_history = history
        self.best_val_loss = best_val_loss
        
        print(f"\n🎉 Training completed! Best validation loss: {best_val_loss:.4f}")
        return history
    
    def _create_dataset(self, latent_data, expression_data):
        """Create PyTorch dataset"""
        class SimpleDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return SimpleDataset(latent_data, expression_data)
    
    def _train_epoch(self, train_loader, optimizer, scheduler, loss_fns, loss_weights, epoch):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        loss_components = {name: 0 for name in loss_fns.keys()}
        grad_norms = []
        
        pbar = tqdm(train_loader, desc=f'Training Epoch {epoch}')
        for latent, target in pbar:
            latent = latent.to(self.device)
            target = target.to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            pred = self.model(latent)
            
            # Calculate losses
            batch_loss = 0
            batch_components = {}
            for name, loss_fn in loss_fns.items():
                if name == 'sparsity':
                    loss = loss_fn(pred)
                else:
                    loss = loss_fn(pred, target)
                weighted_loss = loss * loss_weights[name]
                batch_loss += weighted_loss
                batch_components[name] = loss.item()
            
            # Backward pass
            batch_loss.backward()
            grad_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            
            # Record metrics
            total_loss += batch_loss.item()
            for name in loss_components:
                loss_components[name] += batch_components[name]
            grad_norms.append(grad_norm.item())
            
            # Update progress bar
            pbar.set_postfix({
                'Loss': f'{batch_loss.item():.4f}',
                'GradNorm': f'{grad_norm:.4f}',
                'LR': f'{scheduler.get_last_lr()[0]:.2e}'
            })
        
        # Calculate averages
        num_batches = len(train_loader)
        avg_loss = total_loss / num_batches
        avg_components = {name: value / num_batches for name, value in loss_components.items()}
        avg_components['total_loss'] = avg_loss
        avg_components['grad_norm'] = np.mean(grad_norms)
        
        return avg_components
    
    def _validate_epoch(self, val_loader, loss_fns):
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        all_preds, all_targets = [], []
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device)
                target = target.to(self.device)
                
                pred = self.model(latent)
                
                # Calculate loss
                batch_loss = 0
                for name, loss_fn in loss_fns.items():
                    if name == 'sparsity':
                        loss = loss_fn(pred)
                    else:
                        loss = loss_fn(pred, target)
                    batch_loss += loss
                
                total_loss += batch_loss.item()
                all_preds.append(pred.cpu())
                all_targets.append(target.cpu())
        
        # Calculate overall correlation
        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)
        val_correlation = self._calculate_correlation(all_preds, all_targets)
        
        return {
            'val_loss': total_loss / len(val_loader),
            'val_correlation': val_correlation.item()
        }
    
    def _calculate_correlation(self, pred, target):
        """Calculate Pearson correlation coefficient"""
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return torch.corrcoef(torch.stack([pred_flat, target_flat]))[0, 1]
    
    def _print_epoch_progress(self, epoch, num_epochs, train_metrics, val_metrics):
        """Print epoch progress"""
        current_lr = train_metrics.get('learning_rate', 'N/A')
        print(f"📊 Training Loss: {train_metrics['total_loss']:.4f} | "
              f"Validation Loss: {val_metrics['val_loss']:.4f}")
        print(f"📈 Validation Correlation: {val_metrics['val_correlation']:.4f}")
        print(f"⚡ Learning Rate: {current_lr}")
        print(f"📏 Gradient Norm: {train_metrics['grad_norm']:.4f}")
    
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
    
    def predict(self, latent_data: np.ndarray) -> np.ndarray:
        """
        Predict gene expression profiles from latent variables
        
        Args:
            latent_data: Latent variables [n_samples, latent_dim]
        
        Returns:
            expression: Predicted expression profiles [n_samples, gene_dim]
        """
        if not self.is_trained:
            warnings.warn("Model not trained yet. Using random weights for prediction.")
        
        self.model.eval()
        
        # Convert to tensor if needed
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
        latent_data = latent_data.to(self.device)
        
        with torch.no_grad():
            predictions = self.model(latent_data)
        
        return predictions.cpu().numpy()
    
    def load_model(self, model_path: str):
        """Load pre-trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Check model configuration compatibility
        if 'model_config' in checkpoint:
            config = checkpoint['model_config']
            if (config['latent_dim'] != self.latent_dim or 
                config['gene_dim'] != self.gene_dim):
                warnings.warn("Model configuration mismatch. Reinitializing model.")
                self.model = self._build_model()
                self.model.to(self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        
        print(f"✅ Model loaded successfully! Best validation loss: {self.best_val_loss:.4f}")
    
    def save_model(self, model_path: str):
        """Save the current model state"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'model_config': {
                'latent_dim': self.latent_dim,
                'gene_dim': self.gene_dim,
                'hidden_dim': self.hidden_dim
            },
            'training_history': self.training_history,
            'best_val_loss': self.best_val_loss,
            'is_trained': self.is_trained
        }
        torch.save(checkpoint, model_path)
        print(f"💾 Model saved to: {model_path}")
    
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
    
    def get_training_history(self) -> Dict:
        """Get training history"""
        if self.training_history is None:
            warnings.warn("No training history available. Train the model first.")
            return {}
        return self.training_history
    


'''
# Example usage
def example_usage():
    """Example demonstration of TranscriptomeDecoder usage"""
    
    # 1. Initialize decoder
    decoder = TranscriptomeDecoder(latent_dim=100, gene_dim=2000)  # Reduced for demo
    
    # 2. Generate example data
    n_samples = 1000
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    
    # Create simulated expression data
    weights = np.random.randn(100, 2000) * 0.1
    expression_data = np.tanh(latent_data.dot(weights))
    expression_data = np.maximum(expression_data, 0)  # Ensure non-negative
    
    print(f"📊 Example data shapes: Latent {latent_data.shape}, Expression {expression_data.shape}")
    
    # 3. Train the model
    history = decoder.train(
        train_latent=latent_data,
        train_expression=expression_data,
        num_epochs=50,
        batch_size=32,
        learning_rate=1e-4
    )
    
    # 4. Make predictions
    test_latent = np.random.randn(10, 100).astype(np.float32)
    predictions = decoder.predict(test_latent)
    print(f"🔮 Prediction shape: {predictions.shape}")
    
    # 5. Get model information
    info = decoder.get_model_info()
    print(f"\n📋 Model Info:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # 6. Save model
    decoder.save_model('trained_decoder.pth')
    
    # 7. Load model
    new_decoder = TranscriptomeDecoder(latent_dim=100, gene_dim=2000)
    new_decoder.load_model('trained_decoder.pth')
    
    return decoder
'''