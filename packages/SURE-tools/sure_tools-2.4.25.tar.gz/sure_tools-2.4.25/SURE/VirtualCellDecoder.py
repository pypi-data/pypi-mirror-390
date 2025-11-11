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

class VirtualCellDecoder:
    """
    Advanced transcriptome decoder based on Virtual Cell Challenge research
    Optimized for latent-to-expression mapping with biological constraints
    """
    
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512, 1024, 2048],
                 biological_prior_dim: int = 256,
                 dropout_rate: float = 0.1,
                 device: str = None):
        """
        State-of-the-art decoder based on Virtual Cell Challenge insights
        
        Args:
            latent_dim: Latent variable dimension (typically 50-100)
            gene_dim: Number of genes (full transcriptome ~60,000)
            hidden_dims: Hidden layer dimensions for progressive expansion
            biological_prior_dim: Dimension for biological prior knowledge
            dropout_rate: Dropout rate for regularization
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.gene_dim = gene_dim
        self.hidden_dims = hidden_dims
        self.biological_prior_dim = biological_prior_dim
        self.dropout_rate = dropout_rate
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model with biological constraints
        self.model = self._build_biological_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        
        print(f"🧬 VirtualCellDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimensions: {hidden_dims}")
        print(f"   - Biological Prior Dimension: {biological_prior_dim}")
        print(f"   - Device: {self.device}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class BiologicalPriorNetwork(nn.Module):
        """Biological prior network based on gene regulatory knowledge"""
        
        def __init__(self, latent_dim: int, prior_dim: int, gene_dim: int):
            super().__init__()
            self.gene_dim = gene_dim
            self.prior_dim = prior_dim
            
            # Learnable gene regulatory matrix (sparse initialization)
            self.regulatory_matrix = nn.Parameter(
                torch.randn(gene_dim, prior_dim) * 0.01
            )
            
            # Latent to regulatory space projection
            self.latent_to_regulatory = nn.Sequential(
                nn.Linear(latent_dim, prior_dim * 2),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(prior_dim * 2, prior_dim)
            )
            
            # Regulatory to expression projection
            self.regulatory_to_expression = nn.Sequential(
                nn.Linear(prior_dim, prior_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(prior_dim, gene_dim)
            )
            
            self._init_weights()
        
        def _init_weights(self):
            """Initialize with biological constraints"""
            # Sparse initialization for regulatory matrix
            nn.init.sparse_(self.regulatory_matrix, sparsity=0.8)
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, latent):
            batch_size = latent.shape[0]
            
            # Project latent to regulatory space
            regulatory_factors = self.latent_to_regulatory(latent)  # [batch, prior_dim]
            
            # Apply regulatory matrix (gene-specific modulation)
            regulatory_effect = torch.matmul(
                regulatory_factors, self.regulatory_matrix.T  # [batch, gene_dim]
            )
            
            # Final expression projection
            expression_base = self.regulatory_to_expression(regulatory_factors)
            
            # Combine regulatory effect with base expression
            biological_prior = expression_base + regulatory_effect
            
            return biological_prior
    
    class GeneSpecificAttention(nn.Module):
        """Gene-specific attention mechanism for capturing co-expression patterns"""
        
        def __init__(self, gene_dim: int, attention_dim: int = 128, num_heads: int = 8):
            super().__init__()
            self.gene_dim = gene_dim
            self.attention_dim = attention_dim
            self.num_heads = num_heads
            
            # Gene embeddings for attention
            self.gene_embeddings = nn.Parameter(torch.randn(gene_dim, attention_dim))
            
            # Attention mechanism
            self.query_proj = nn.Linear(attention_dim, attention_dim)
            self.key_proj = nn.Linear(attention_dim, attention_dim)
            self.value_proj = nn.Linear(attention_dim, attention_dim)
            
            # Output projection
            self.output_proj = nn.Linear(attention_dim, attention_dim)
            
            self._init_weights()
        
        def _init_weights(self):
            """Initialize attention weights"""
            nn.init.xavier_uniform_(self.gene_embeddings)
            for module in [self.query_proj, self.key_proj, self.value_proj, self.output_proj]:
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
        
        def forward(self, x):
            batch_size = x.shape[0]
            
            # Prepare gene embeddings
            gene_embeds = self.gene_embeddings.unsqueeze(0).expand(batch_size, -1, -1)
            
            # Compute attention
            Q = self.query_proj(gene_embeds)
            K = self.key_proj(gene_embeds)
            V = self.value_proj(gene_embeds)
            
            # Multi-head attention
            head_dim = self.attention_dim // self.num_heads
            Q = Q.view(batch_size, self.gene_dim, self.num_heads, head_dim).transpose(1, 2)
            K = K.view(batch_size, self.gene_dim, self.num_heads, head_dim).transpose(1, 2)
            V = V.view(batch_size, self.gene_dim, self.num_heads, head_dim).transpose(1, 2)
            
            # Scaled dot-product attention
            attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(head_dim)
            attn_weights = F.softmax(attn_scores, dim=-1)
            
            # Apply attention
            attn_output = torch.matmul(attn_weights, V)
            attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, self.gene_dim, self.attention_dim)
            
            # Output projection
            output = self.output_proj(attn_output)
            
            return output
    
    class SparseActivation(nn.Module):
        """Sparse activation function for biological data"""
        
        def __init__(self, sparsity_target: float = 0.85):
            super().__init__()
            self.sparsity_target = sparsity_target
            self.alpha = nn.Parameter(torch.tensor(1.0))
            self.beta = nn.Parameter(torch.tensor(0.0))
        
        def forward(self, x):
            # Learnable softplus with sparsity constraint
            activated = F.softplus(x * self.alpha + self.beta)
            
            # Sparsity regularization (encourages biological sparsity)
            sparsity_loss = (activated.mean() - self.sparsity_target) ** 2
            self.sparsity_loss = sparsity_loss * 0.01  # Light regularization
            
            return activated
    
    class VirtualCellModel(nn.Module):
        """Main Virtual Cell Challenge inspired model"""
        
        def __init__(self, latent_dim: int, gene_dim: int, hidden_dims: List[int], 
                     biological_prior_dim: int, dropout_rate: float):
            super().__init__()
            
            # Phase 1: Latent expansion with biological constraints
            self.latent_expansion = nn.Sequential(
                nn.Linear(latent_dim, hidden_dims[0]),
                nn.BatchNorm1d(hidden_dims[0]),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dims[0], hidden_dims[1]),
                nn.BatchNorm1d(hidden_dims[1]),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            )
            
            # Phase 2: Biological prior network
            self.biological_prior = VirtualCellDecoder.BiologicalPriorNetwork(
                hidden_dims[1], biological_prior_dim, gene_dim
            )
            
            # Phase 3: Gene-specific processing
            self.gene_attention = VirtualCellDecoder.GeneSpecificAttention(gene_dim)
            
            # Phase 4: Final expression refinement
            self.expression_refinement = nn.Sequential(
                nn.Linear(gene_dim, hidden_dims[2]),
                nn.BatchNorm1d(hidden_dims[2]),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dims[2], gene_dim)
            )
            
            # Phase 5: Sparse activation
            self.sparse_activation = VirtualCellDecoder.SparseActivation()
            
            self._init_weights()
        
        def _init_weights(self):
            """Biological-inspired weight initialization"""
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    # Xavier initialization for stable training
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
                elif isinstance(module, nn.BatchNorm1d):
                    nn.init.ones_(module.weight)
                    nn.init.zeros_(module.bias)
        
        def forward(self, latent):
            # Phase 1: Latent expansion
            expanded_latent = self.latent_expansion(latent)
            
            # Phase 2: Biological prior
            biological_output = self.biological_prior(expanded_latent)
            
            # Phase 3: Gene attention
            attention_output = self.gene_attention(biological_output)
            
            # Phase 4: Refinement with residual connection
            refined_output = self.expression_refinement(attention_output) + biological_output
            
            # Phase 5: Sparse activation
            final_output = self.sparse_activation(refined_output)
            
            return final_output
    
    def _build_biological_model(self):
        """Build the biologically constrained model"""
        return self.VirtualCellModel(
            self.latent_dim, self.gene_dim, self.hidden_dims,
            self.biological_prior_dim, self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 200,
              learning_rate: float = 1e-4,
              biological_weight: float = 0.1,
              checkpoint_path: str = 'virtual_cell_decoder.pth') -> Dict:
        """
        Train with biological constraints and Virtual Cell Challenge insights
        
        Args:
            train_latent: Training latent variables
            train_expression: Training expression data
            val_latent: Validation latent variables
            val_expression: Validation expression data
            batch_size: Batch size optimized for biological data
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            biological_weight: Weight for biological constraint loss
            checkpoint_path: Model save path
        """
        print("🧬 Starting Virtual Cell Challenge Training...")
        print("📚 Incorporating biological constraints and regulatory priors")
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
            print(f"📈 Using provided validation data: {len(val_dataset)} samples")
        else:
            # Auto split (90/10)
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            print(f"📈 Auto-split validation: {val_size} samples")
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"📊 Batch size: {batch_size}")
        
        # Optimizer with biological regularization
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=1e-5,  # L2 regularization
            betas=(0.9, 0.999)
        )
        
        # Cosine annealing with warmup
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=50, T_mult=2, eta_min=1e-6
        )
        
        # Biological loss function
        def biological_loss(pred, target):
            # 1. Reconstruction loss
            mse_loss = F.mse_loss(pred, target)
            
            # 2. Poisson loss for count data
            poisson_loss = (pred - target * torch.log(pred + 1e-8)).mean()
            
            # 3. Correlation loss for pattern matching
            correlation = self._pearson_correlation(pred, target)
            correlation_loss = 1 - correlation
            
            # 4. Sparsity loss (biological constraint)
            sparsity_loss = self.model.sparse_activation.sparsity_loss
            
            # 5. Biological consistency loss
            biological_loss = self._biological_consistency_loss(pred)
            
            total_loss = (mse_loss + 0.5 * poisson_loss + 0.3 * correlation_loss + 
                         0.1 * sparsity_loss + biological_weight * biological_loss)
            
            return total_loss, {
                'mse': mse_loss.item(),
                'poisson': poisson_loss.item(),
                'correlation': correlation.item(),
                'sparsity': sparsity_loss.item(),
                'biological': biological_loss.item()
            }
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'train_mse': [], 'val_mse': [],
            'train_correlation': [], 'val_correlation': [],
            'train_sparsity': [], 'val_sparsity': [],
            'learning_rates': [], 'grad_norms': []
        }
        
        best_val_loss = float('inf')
        patience = 25
        patience_counter = 0
        
        print("\n🔬 Starting training with biological constraints...")
        for epoch in range(1, num_epochs + 1):
            # Training phase
            train_loss, train_components, grad_norm = self._train_epoch(
                train_loader, optimizer, biological_loss
            )
            
            # Validation phase
            val_loss, val_components = self._validate_epoch(val_loader, biological_loss)
            
            # Update scheduler
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_mse'].append(train_components['mse'])
            history['val_mse'].append(val_components['mse'])
            history['train_correlation'].append(train_components['correlation'])
            history['val_correlation'].append(val_components['correlation'])
            history['train_sparsity'].append(train_components['sparsity'])
            history['val_sparsity'].append(val_components['sparsity'])
            history['learning_rates'].append(current_lr)
            history['grad_norms'].append(grad_norm)
            
            # Print detailed progress
            if epoch % 10 == 0 or epoch == 1:
                print(f"🧪 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train: {train_loss:.4f} | Val: {val_loss:.4f} | "
                      f"Corr: {val_components['correlation']:.4f} | "
                      f"Sparsity: {val_components['sparsity']:.4f} | "
                      f"LR: {current_lr:.2e}")
            
            # Early stopping and model saving
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
        print(f"📊 Final correlation: {history['val_correlation'][-1]:.4f}")
        print(f"🌿 Final sparsity: {history['val_sparsity'][-1]:.4f}")
        
        return history
    
    def _biological_consistency_loss(self, pred):
        """Biological consistency loss based on Virtual Cell Challenge insights"""
        # 1. Gene expression variance consistency
        gene_variance = pred.var(dim=0)
        target_variance = torch.ones_like(gene_variance) * 0.5  # Reasonable biological variance
        variance_loss = F.mse_loss(gene_variance, target_variance)
        
        # 2. Co-expression pattern consistency
        correlation_matrix = torch.corrcoef(pred.T)
        correlation_loss = torch.mean(torch.abs(correlation_matrix))  # Encourage moderate correlations
        
        return variance_loss + 0.5 * correlation_loss
    
    def _create_dataset(self, latent_data, expression_data):
        """Create dataset with biological data validation"""
        class BiologicalDataset(Dataset):
            def __init__(self, latent, expression):
                # Validate biological data characteristics
                assert np.all(expression >= 0), "Expression data must be non-negative"
                assert np.mean(expression == 0) > 0.7, "Expression data should be sparse (typical scRNA-seq)"
                
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return BiologicalDataset(latent_data, expression_data)
    
    def _pearson_correlation(self, pred, target):
        """Calculate Pearson correlation coefficient"""
        pred_centered = pred - pred.mean(dim=1, keepdim=True)
        target_centered = target - target.mean(dim=1, keepdim=True)
        
        numerator = (pred_centered * target_centered).sum(dim=1)
        denominator = torch.sqrt(torch.sum(pred_centered ** 2, dim=1)) * torch.sqrt(torch.sum(target_centered ** 2, dim=1))
        
        return (numerator / (denominator + 1e-8)).mean()
    
    def _train_epoch(self, train_loader, optimizer, loss_fn):
        """Train one epoch with biological constraints"""
        self.model.train()
        total_loss = 0
        total_components = {'mse': 0, 'poisson': 0, 'correlation': 0, 'sparsity': 0, 'biological': 0}
        grad_norms = []
        
        for latent, target in train_loader:
            latent = latent.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            
            optimizer.zero_grad()
            pred = self.model(latent)
            
            loss, components = loss_fn(pred, target)
            loss.backward()
            
            # Gradient clipping for stability
            grad_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            
            total_loss += loss.item()
            for key in components:
                total_components[key] += components[key]
            grad_norms.append(grad_norm.item())
        
        num_batches = len(train_loader)
        avg_loss = total_loss / num_batches
        avg_components = {key: value / num_batches for key, value in total_components.items()}
        avg_grad_norm = np.mean(grad_norms)
        
        return avg_loss, avg_components, avg_grad_norm
    
    def _validate_epoch(self, val_loader, loss_fn):
        """Validate one epoch"""
        self.model.eval()
        total_loss = 0
        total_components = {'mse': 0, 'poisson': 0, 'correlation': 0, 'sparsity': 0, 'biological': 0}
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device, non_blocking=True)
                target = target.to(self.device, non_blocking=True)
                
                pred = self.model(latent)
                loss, components = loss_fn(pred, target)
                
                total_loss += loss.item()
                for key in components:
                    total_components[key] += components[key]
        
        num_batches = len(val_loader)
        avg_loss = total_loss / num_batches
        avg_components = {key: value / num_batches for key, value in total_components.items()}
        
        return avg_loss, avg_components
    
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
                'biological_prior_dim': self.biological_prior_dim,
                'dropout_rate': self.dropout_rate
            }
        }, path)
    
    def predict(self, latent_data: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """
        Predict gene expression with biological constraints
        
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
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        print(f"✅ Model loaded! Best validation loss: {self.best_val_loss:.4f}")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'is_trained': self.is_trained,
            'best_val_loss': self.best_val_loss,
            'parameters': sum(p.numel() for p in self.model.parameters()),
            'latent_dim': self.latent_dim,
            'gene_dim': self.gene_dim,
            'hidden_dims': self.hidden_dims,
            'biological_prior_dim': self.biological_prior_dim,
            'device': str(self.device)
        }

'''
# Example usage
def example_usage():
    """Example demonstration of Virtual Cell Challenge decoder"""
    
    # Initialize decoder
    decoder = VirtualCellDecoder(
        latent_dim=100,
        gene_dim=2000,  # Reduced for example
        hidden_dims=[256, 512, 1024],
        biological_prior_dim=128,
        dropout_rate=0.1
    )
    
    # Generate example data with biological characteristics
    n_samples = 1000
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    
    # Simulate biological expression data (sparse, non-negative)
    weights = np.random.randn(100, 2000) * 0.1
    expression_data = np.tanh(latent_data.dot(weights))
    expression_data = np.maximum(expression_data, 0)
    
    # Add biological sparsity (typical scRNA-seq characteristics)
    mask = np.random.random(expression_data.shape) > 0.8  # 80% sparsity
    expression_data[mask] = 0
    
    print(f"📊 Data shapes: Latent {latent_data.shape}, Expression {expression_data.shape}")
    print(f"🌿 Biological sparsity: {(expression_data == 0).mean():.3f}")
    
    # Train with biological constraints
    history = decoder.train(
        train_latent=latent_data,
        train_expression=expression_data,
        batch_size=32,
        num_epochs=50,
        learning_rate=1e-4,
        biological_weight=0.1
    )
    
    # Predict
    test_latent = np.random.randn(10, 100).astype(np.float32)
    predictions = decoder.predict(test_latent)
    print(f"🔮 Prediction shape: {predictions.shape}")
    print(f"🌿 Predicted sparsity: {(predictions < 0.1).mean():.3f}")
    
    return decoder

if __name__ == "__main__":
    example_usage()
    
'''