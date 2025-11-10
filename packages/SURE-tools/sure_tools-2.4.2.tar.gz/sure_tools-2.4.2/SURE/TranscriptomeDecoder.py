import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class TranscriptomeDecoder:
    def __init__(self, 
                 latent_dim: int = 100,
                 gene_dim: int = 60000,
                 hidden_dim: int = 512,  # Reduced for memory efficiency
                 device: str = None):
        """
        Whole-transcriptome decoder
        
        Args:
            latent_dim: Latent variable dimension (typically 50-100)
            gene_dim: Number of genes (full transcriptome ~60,000)
            hidden_dim: Hidden dimension (reduced for memory efficiency)
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.gene_dim = gene_dim
        self.hidden_dim = hidden_dim
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Memory optimization settings
        self.gradient_checkpointing = True
        self.mixed_precision = True
        
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
    
    class MemoryEfficientBlock(nn.Module):
        """Memory-efficient building block with gradient checkpointing"""
        def __init__(self, input_dim, output_dim, use_checkpointing=True):
            super().__init__()
            self.use_checkpointing = use_checkpointing
            self.net = nn.Sequential(
                nn.Linear(input_dim, output_dim),
                nn.BatchNorm1d(output_dim),
                nn.GELU(),
                nn.Dropout(0.1)
            )
        
        def forward(self, x):
            if self.use_checkpointing and self.training:
                return torch.utils.checkpoint.checkpoint(self.net, x)
            return self.net(x)
    
    class SparseGeneProjection(nn.Module):
        """Sparse gene projection to reduce memory usage"""
        def __init__(self, latent_dim, gene_dim, projection_dim=256):
            super().__init__()
            self.projection_dim = projection_dim
            self.gene_embeddings = nn.Parameter(torch.randn(gene_dim, projection_dim) * 0.02)
            self.latent_projection = nn.Linear(latent_dim, projection_dim)
            self.activation = nn.GELU()
            
        def forward(self, latent):
            # Project latent to gene space efficiently
            batch_size = latent.shape[0]
            latent_proj = self.latent_projection(latent)  # [batch, projection_dim]
            
            # Efficient matrix multiplication
            gene_embeds = self.gene_embeddings.T  # [projection_dim, gene_dim]
            output = torch.matmul(latent_proj, gene_embeds)  # [batch, gene_dim]
            
            return self.activation(output)
    
    class ChunkedTransformer(nn.Module):
        """Process genes in chunks to reduce memory usage"""
        def __init__(self, gene_dim, hidden_dim, chunk_size=1000, num_layers=4):
            super().__init__()
            self.chunk_size = chunk_size
            self.num_chunks = (gene_dim + chunk_size - 1) // chunk_size
            self.layers = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, hidden_dim),
                ) for _ in range(num_layers)
            ])
            
        def forward(self, x):
            # Process in chunks to save memory
            batch_size = x.shape[0]
            output = torch.zeros_like(x)
            
            for i in range(self.num_chunks):
                start_idx = i * self.chunk_size
                end_idx = min((i + 1) * self.chunk_size, x.shape[1])
                
                chunk = x[:, start_idx:end_idx]
                for layer in self.layers:
                    chunk = layer(chunk) + chunk  # Residual connection
                
                output[:, start_idx:end_idx] = chunk
            
            return output
    
    class Decoder(nn.Module):
        """Decoder model"""
        def __init__(self, latent_dim, gene_dim, hidden_dim):
            super().__init__()
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            self.hidden_dim = hidden_dim
            
            # Stage 1: Latent expansion (memory efficient)
            self.latent_expansion = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim * 2),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim * 2, hidden_dim),
            )
            
            # Stage 2: Sparse gene projection
            self.gene_projection = TranscriptomeDecoder.SparseGeneProjection(
                latent_dim, gene_dim, hidden_dim
            )
            
            # Stage 3: Chunked processing
            self.chunked_processor = TranscriptomeDecoder.ChunkedTransformer(
                gene_dim, hidden_dim, chunk_size=2000, num_layers=3
            )
            
            # Stage 4: Multi-head output with memory efficiency
            self.output_heads = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.GELU(),
                    nn.Linear(hidden_dim // 2, 1)
                ) for _ in range(2)  # Reduced from 3 to 2 heads
            ])
            
            # Adaptive fusion
            self.fusion_gate = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 4),
                nn.GELU(),
                nn.Linear(hidden_dim // 4, len(self.output_heads)),
                nn.Softmax(dim=-1)
            )
            
            # Output scaling
            self.output_scale = nn.Parameter(torch.ones(1))
            self.output_bias = nn.Parameter(torch.zeros(1))
            
            self._init_weights()
        
        def _init_weights(self):
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, latent):
            batch_size = latent.shape[0]
            
            # 1. Latent expansion
            latent_expanded = self.latent_expansion(latent)
            
            # 2. Gene projection (memory efficient)
            gene_features = self.gene_projection(latent)
            
            # 3. Add latent information
            print(f'{gene_features.shape}; {latent_expanded.shape}')
            gene_features = gene_features + latent_expanded.unsqueeze(1)
            
            # 4. Chunked processing (memory efficient)
            gene_features = self.chunked_processor(gene_features)
            
            # 5. Multi-head output with chunking
            final_output = torch.zeros(batch_size, self.gene_dim, device=latent.device)
            
            # Process output in chunks
            chunk_size = 5000
            for i in range(0, self.gene_dim, chunk_size):
                end_idx = min(i + chunk_size, self.gene_dim)
                chunk = gene_features[:, i:end_idx]
                
                head_outputs = []
                for head in self.output_heads:
                    head_out = head(chunk).squeeze(-1)
                    head_outputs.append(head_out)
                
                # Adaptive fusion
                gate_weights = self.fusion_gate(chunk.mean(dim=1, keepdim=True))
                gate_weights = gate_weights.unsqueeze(1)
                
                # Weighted fusion
                chunk_output = torch.zeros_like(head_outputs[0])
                for j, head_out in enumerate(head_outputs):
                    chunk_output = chunk_output + gate_weights[:, :, j] * head_out
                
                final_output[:, i:end_idx] = chunk_output
            
            # Final activation
            final_output = F.softplus(final_output * self.output_scale + self.output_bias)
            
            return final_output
    
    def _build_model(self):
        """Build model"""
        return self.Decoder(self.latent_dim, self.gene_dim, self.hidden_dim)
    
    def train(self,
              train_latent: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 16,  # Reduced batch size for memory
              num_epochs: int = 100,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'transcriptome_decoder.pth'):
        """
        Memory-efficient training with optimizations
        
        Args:
            train_latent: Training latent variables
            train_expression: Training expression data
            val_latent: Validation latent variables
            val_expression: Validation expression data
            batch_size: Reduced batch size for memory constraints
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            checkpoint_path: Model save path
        """
        print("🚀 Starting Training...")
        print(f"📊 Batch size: {batch_size}")
        
        # Enable memory optimizations
        torch.backends.cudnn.benchmark = True
        if self.mixed_precision:
            scaler = torch.cuda.amp.GradScaler()
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_expression)
        
        if val_latent is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_expression)
        else:
            # Auto split
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_dataset, val_dataset = torch.utils.data.random_split(
                train_dataset, [train_size, val_size]
            )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, 
                                 pin_memory=True, num_workers=2)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                               pin_memory=True, num_workers=2)
        
        # Optimizer with memory-friendly settings
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            betas=(0.9, 0.999)
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
        
        # Loss function
        criterion = nn.MSELoss()
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'learning_rate': [], 'memory_usage': []
        }
        
        best_val_loss = float('inf')
        
        for epoch in range(1, num_epochs + 1):
            print(f"\n📍 Epoch {epoch}/{num_epochs}")
            
            # Training phase with memory monitoring
            train_loss = self._train_epoch(
                train_loader, optimizer, criterion, scaler if self.mixed_precision else None
            )
            
            # Validation phase
            val_loss = self._validate_epoch(val_loader, criterion)
            
            # Update scheduler
            scheduler.step()
            
            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['learning_rate'].append(optimizer.param_groups[0]['lr'])
            
            # Memory usage tracking
            if torch.cuda.is_available():
                memory_used = torch.cuda.memory_allocated() / 1024**3  # GB
                history['memory_usage'].append(memory_used)
                print(f"💾 GPU Memory: {memory_used:.1f}GB / 20GB")
            
            print(f"📊 Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
            print(f"⚡ Learning Rate: {optimizer.param_groups[0]['lr']:.2e}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_checkpoint(epoch, optimizer, scheduler, best_val_loss, history, checkpoint_path)
                print("💾 Best model saved!")
        
        self.is_trained = True
        self.training_history = history
        self.best_val_loss = best_val_loss
        
        print(f"\n🎉 Training completed! Best validation loss: {best_val_loss:.4f}")
        return history
    
    def _train_epoch(self, train_loader, optimizer, criterion, scaler=None):
        """Training epoch"""
        self.model.train()
        total_loss = 0
        
        pbar = tqdm(train_loader, desc='Training')
        for latent, target in pbar:
            latent = latent.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            
            optimizer.zero_grad(set_to_none=True)  # Memory optimization
            
            if scaler:  # Mixed precision training
                with torch.cuda.amp.autocast():
                    pred = self.model(latent)
                    loss = criterion(pred, target)
                
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                pred = self.model(latent)
                loss = criterion(pred, target)
                loss.backward()
                optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({'Loss': f'{loss.item():.4f}'})
            
            # Clear memory
            del pred, loss
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return total_loss / len(train_loader)
    
    def _validate_epoch(self, val_loader, criterion):
        """Validation"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for latent, target in val_loader:
                latent = latent.to(self.device, non_blocking=True)
                target = target.to(self.device, non_blocking=True)
                
                pred = self.model(latent)
                loss = criterion(pred, target)
                total_loss += loss.item()
                
                # Clear memory
                del pred, loss
        
        return total_loss / len(val_loader)
    
    def _create_dataset(self, latent_data, expression_data):
        """Create dataset"""
        class EfficientDataset(Dataset):
            def __init__(self, latent, expression):
                self.latent = torch.FloatTensor(latent)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.expression[idx]
        
        return EfficientDataset(latent_data, expression_data)
    
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
                'hidden_dim': self.hidden_dim
            }
        }, path)
    
    def predict(self, latent_data: np.ndarray, batch_size: int = 8) -> np.ndarray:
        """
        Prediction
        
        Args:
            latent_data: Latent variables [n_samples, latent_dim]
            batch_size: Prediction batch size for memory control
        
        Returns:
            expression: Predicted expression [n_samples, gene_dim]
        """
        if not self.is_trained:
            warnings.warn("Model not trained. Predictions may be inaccurate.")
        
        self.model.eval()
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        
        # Predict in batches to save memory
        predictions = []
        with torch.no_grad():
            for i in range(0, len(latent_data), batch_size):
                batch_latent = latent_data[i:i+batch_size].to(self.device)
                batch_pred = self.model(batch_latent)
                predictions.append(batch_pred.cpu())
                
                # Clear memory
                del batch_pred
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
        print(f"✅ Model loaded! Best validation loss: {self.best_val_loss:.4f}")
    
    def get_memory_info(self) -> Dict:
        """Get memory usage information"""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            return {
                'allocated_gb': memory_allocated,
                'reserved_gb': memory_reserved,
                'available_gb': 20 - memory_allocated,
                'utilization_percent': (memory_allocated / 20) * 100
            }
        return {'available_gb': 'N/A (CPU mode)'}
    
'''
# Example usage with memory monitoring
def example_usage():
    """Memory-efficient example"""
    
    # 1. Initialize memory-efficient decoder
    decoder = TranscriptomeDecoder(
        latent_dim=100,
        gene_dim=2000,  # Reduced for example
        hidden_dim=256   # Reduced for memory
    )
    
    # Check memory info
    memory_info = decoder.get_memory_info()
    print(f"📊 Memory Info: {memory_info}")
    
    # 2. Generate example data
    n_samples = 500  # Reduced for memory
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    expression_data = np.random.randn(n_samples, 2000).astype(np.float32)
    expression_data = np.maximum(expression_data, 0)  # Non-negative
    
    print(f"📈 Data shapes: Latent {latent_data.shape}, Expression {expression_data.shape}")
    
    # 3. Train with memory monitoring
    history = decoder.train(
        train_latent=latent_data,
        train_expression=expression_data,
        batch_size=8,  # Small batch for memory
        num_epochs=20   # Reduced for example
    )
    
    # 4. Memory-efficient prediction
    test_latent = np.random.randn(5, 100).astype(np.float32)
    predictions = decoder.predict(test_latent, batch_size=2)
    print(f"🔮 Prediction shape: {predictions.shape}")
    
    # 5. Final memory check
    final_memory = decoder.get_memory_info()
    print(f"💾 Final memory usage: {final_memory}")
    
    return decoder

if __name__ == "__main__":
    example_usage()
    
'''