import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import math
import warnings
warnings.filterwarnings('ignore')

class PerturbationAwareDecoder:
    """
    Advanced transcriptome decoder with perturbation awareness
    Fixed version with proper handling of single hidden layer configurations
    """
    
    def __init__(self, 
                 latent_dim: int = 100,
                 num_known_perturbations: int = 50,
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512],
                 perturbation_embedding_dim: int = 128,
                 biological_prior_dim: int = 256,
                 dropout_rate: float = 0.1,
                 device: str = None):
        """
        Multi-modal decoder with fixed single layer support
        """
        self.latent_dim = latent_dim
        self.num_known_perturbations = num_known_perturbations
        self.gene_dim = gene_dim
        self.hidden_dims = hidden_dims
        self.perturbation_embedding_dim = perturbation_embedding_dim
        self.biological_prior_dim = biological_prior_dim
        self.dropout_rate = dropout_rate
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Validate hidden_dims
        self._validate_hidden_dims()
        
        # Initialize multi-modal model
        self.model = self._build_fixed_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        self.known_perturbation_names = []
        self.perturbation_prototypes = None
        
        print(f"🧬 PerturbationAwareDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Known Perturbations: {num_known_perturbations}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Hidden Dimensions: {hidden_dims}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _validate_hidden_dims(self):
        """Validate hidden_dims parameter"""
        assert len(self.hidden_dims) >= 1, "hidden_dims must have at least one element"
        assert all(dim > 0 for dim in self.hidden_dims), "All hidden dimensions must be positive"
        
        if len(self.hidden_dims) == 1:
            print("🔧 Single hidden layer configuration detected")
        else:
            print(f"🔧 Multi-layer configuration: {len(self.hidden_dims)} hidden layers")
    
    class FixedPerturbationEncoder(nn.Module):
        """Fixed perturbation encoder"""
        
        def __init__(self, num_perturbations: int, embedding_dim: int, hidden_dim: int):
            super().__init__()
            self.num_perturbations = num_perturbations
            
            # Embedding for perturbation types
            self.perturbation_embedding = nn.Embedding(num_perturbations, embedding_dim)
            
            # Projection to hidden space
            self.projection = nn.Sequential(
                nn.Linear(embedding_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            )
            
        def forward(self, one_hot_perturbations):
            # Convert one-hot to indices
            perturbation_indices = torch.argmax(one_hot_perturbations, dim=1)
            
            # Get perturbation embeddings
            perturbation_embeds = self.perturbation_embedding(perturbation_indices)
            
            # Project to hidden space
            hidden_repr = self.projection(perturbation_embeds)
            
            return hidden_repr
    
    class FixedCrossModalFusion(nn.Module):
        """Fixed cross-modal fusion"""
        
        def __init__(self, latent_dim: int, perturbation_dim: int, fusion_dim: int):
            super().__init__()
            self.latent_projection = nn.Linear(latent_dim, fusion_dim)
            self.perturbation_projection = nn.Linear(perturbation_dim, fusion_dim)
            
            # Fusion gate
            self.fusion_gate = nn.Sequential(
                nn.Linear(fusion_dim * 2, fusion_dim),
                nn.Sigmoid()
            )
            
            self.norm = nn.LayerNorm(fusion_dim)
            self.dropout = nn.Dropout(0.1)
        
        def forward(self, latent, perturbation_encoded):
            # Project both modalities
            latent_proj = self.latent_projection(latent)
            perturbation_proj = self.perturbation_projection(perturbation_encoded)
            
            # Gated fusion
            concatenated = torch.cat([latent_proj, perturbation_proj], dim=-1)
            fusion_gate = self.fusion_gate(concatenated)
            
            # Gated fusion
            fused = fusion_gate * latent_proj + (1 - fusion_gate) * perturbation_proj
            fused = self.norm(fused)
            fused = self.dropout(fused)
            
            return fused
    
    class FixedPerturbationResponseNetwork(nn.Module):
        """Fixed response network with proper single layer handling"""
        
        def __init__(self, fusion_dim: int, gene_dim: int, hidden_dims: List[int]):
            super().__init__()
            
            # Build network layers
            layers = []
            input_dim = fusion_dim
            
            # Handle both single and multi-layer cases
            for i, hidden_dim in enumerate(hidden_dims):
                layers.extend([
                    nn.Linear(input_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1)
                ])
                input_dim = hidden_dim
            
            self.base_network = nn.Sequential(*layers)
            
            # Final projection - FIXED: Use current input_dim instead of hidden_dims[-1]
            self.final_projection = nn.Linear(input_dim, gene_dim)
            
            # Perturbation-aware scaling
            self.scale = nn.Linear(fusion_dim, 1)
            self.bias = nn.Linear(fusion_dim, 1)
        
        def forward(self, fused_representation):
            base_output = self.base_network(fused_representation)
            expression = self.final_projection(base_output)
            
            # Perturbation-aware scaling
            scale = torch.sigmoid(self.scale(fused_representation)) * 2
            bias = self.bias(fused_representation)
            
            return F.softplus(expression * scale + bias)
    
    class FixedNovelPerturbationPredictor(nn.Module):
        """Fixed novel perturbation predictor"""
        
        def __init__(self, num_known_perturbations: int, gene_dim: int, hidden_dim: int):
            super().__init__()
            self.num_known_perturbations = num_known_perturbations
            self.gene_dim = gene_dim
            
            # Learnable perturbation prototypes
            self.perturbation_prototypes = nn.Parameter(
                torch.randn(num_known_perturbations, gene_dim) * 0.1
            )
            
            # Response generator - handle case where hidden_dim might be 0
            if hidden_dim > 0:
                self.response_generator = nn.Sequential(
                    nn.Linear(num_known_perturbations, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, gene_dim)
                )
            else:
                # Direct projection if no hidden layer
                self.response_generator = nn.Linear(num_known_perturbations, gene_dim)
            
            # Attention mechanism
            self.similarity_attention = nn.Sequential(
                nn.Linear(num_known_perturbations, num_known_perturbations),
                nn.Softmax(dim=-1)
            )
        
        def forward(self, similarity_matrix, latent_features=None):
            batch_size = similarity_matrix.shape[0]
            
            # Method 1: Attention-weighted combination of known responses
            attention_weights = self.similarity_attention(similarity_matrix)
            weighted_response = torch.matmul(attention_weights, self.perturbation_prototypes)
            
            # Method 2: Direct generation from similarity
            generated_response = self.response_generator(similarity_matrix)
            
            # Simple combination
            combination_weights = torch.sigmoid(similarity_matrix.mean(dim=1, keepdim=True))
            final_response = (combination_weights * weighted_response + 
                            (1 - combination_weights) * generated_response)
            
            return final_response
    
    class FixedMultimodalDecoder(nn.Module):
        """Main decoder with fixed single layer handling"""
        
        def __init__(self, latent_dim: int, num_known_perturbations: int, gene_dim: int, 
                    hidden_dims: List[int], perturbation_embedding_dim: int, 
                    biological_prior_dim: int, dropout_rate: float):
            super().__init__()
            
            self.num_known_perturbations = num_known_perturbations
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            
            # Use first hidden dimension for fusion
            main_hidden_dim = hidden_dims[0]
            
            # Perturbation encoder
            self.perturbation_encoder = PerturbationAwareDecoder.FixedPerturbationEncoder(
                num_known_perturbations, perturbation_embedding_dim, main_hidden_dim
            )
            
            # Cross-modal fusion
            self.cross_modal_fusion = PerturbationAwareDecoder.FixedCrossModalFusion(
                latent_dim, main_hidden_dim, main_hidden_dim
            )
            
            # Response network - FIXED: Use all hidden_dims for response network
            self.response_network = PerturbationAwareDecoder.FixedPerturbationResponseNetwork(
                main_hidden_dim, gene_dim, hidden_dims  # Pass all hidden_dims
            )
            
            # Novel perturbation predictor
            self.novel_predictor = PerturbationAwareDecoder.FixedNovelPerturbationPredictor(
                num_known_perturbations, gene_dim, main_hidden_dim
            )
            
        def forward(self, latent, perturbation_matrix, mode='one_hot'):
            if mode == 'one_hot':
                # Known perturbation pathway
                perturbation_encoded = self.perturbation_encoder(perturbation_matrix)
                fused = self.cross_modal_fusion(latent, perturbation_encoded)
                expression = self.response_network(fused)
                
            elif mode == 'similarity':
                # Novel perturbation pathway
                expression = self.novel_predictor(perturbation_matrix, latent)
                
            else:
                raise ValueError(f"Unknown mode: {mode}. Use 'one_hot' or 'similarity'")
            
            return expression
        
        def get_perturbation_prototypes(self):
            """Get learned perturbation response prototypes"""
            return self.novel_predictor.perturbation_prototypes.detach()
    
    def _build_fixed_model(self):
        """Build the fixed model"""
        return self.FixedMultimodalDecoder(
            self.latent_dim, self.num_known_perturbations, self.gene_dim,
            self.hidden_dims, self.perturbation_embedding_dim,
            self.biological_prior_dim, self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_perturbations: np.ndarray,
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_perturbations: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 200,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'fixed_decoder.pth') -> Dict:
        """
        Train the fixed decoder
        """
        print("🧬 Starting Training with Fixed Single Layer Support...")
        
        # Validate one-hot encoding
        self._validate_one_hot_perturbations(train_perturbations)
        
        # Data preparation
        train_dataset = self._create_dataset(train_latent, train_perturbations, train_expression)
        
        if val_latent is not None and val_perturbations is not None and val_expression is not None:
            val_dataset = self._create_dataset(val_latent, val_perturbations, val_expression)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        else:
            train_size = int(0.9 * len(train_dataset))
            val_size = len(train_dataset) - train_size
            train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
        
        print(f"📊 Training samples: {len(train_loader.dataset)}")
        print(f"📊 Validation samples: {len(val_loader.dataset)}")
        print(f"🔧 Hidden layers: {len(self.hidden_dims)}")
        print(f"🔧 Hidden dimensions: {self.hidden_dims}")
        
        # Optimizer
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=1e-5
        )
        
        # Scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
        
        # Loss function
        def loss_fn(pred, target):
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
        
        print("\n🔬 Starting training...")
        for epoch in range(1, num_epochs + 1):
            # Training
            train_metrics = self._train_epoch(train_loader, optimizer, loss_fn)
            
            # Validation
            val_metrics = self._validate_epoch(val_loader, loss_fn)
            
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
                print(f"🧪 Epoch {epoch:3d}/{num_epochs} | "
                      f"Train: {train_metrics['loss']:.4f} | "
                      f"Val: {val_metrics['loss']:.4f} | "
                      f"Corr: {val_metrics['correlation']:.4f} | "
                      f"LR: {current_lr:.2e}")
            
            # Early stopping
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                patience_counter = 0
                self._save_checkpoint(epoch, optimizer, scheduler, best_val_loss, history, checkpoint_path)
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"🛑 Early stopping at epoch {epoch}")
                    break
        
        self.is_trained = True
        self.training_history = history
        self.best_val_loss = best_val_loss
        self.perturbation_prototypes = self.model.get_perturbation_prototypes().cpu().numpy()
        
        print(f"\n🎉 Training completed! Best val loss: {best_val_loss:.4f}")
        return history
    
    def _validate_one_hot_perturbations(self, perturbations):
        """Validate that perturbations are proper one-hot encodings"""
        assert perturbations.shape[1] == self.num_known_perturbations, \
            f"Perturbation dimension {perturbations.shape[1]} doesn't match expected {self.num_known_perturbations}"
        
        row_sums = perturbations.sum(axis=1)
        valid_rows = np.all((row_sums == 0) | (row_sums == 1))
        assert valid_rows, "Perturbations should be one-hot encoded (sum to 0 or 1 per row)"
        
        print("✅ One-hot perturbations validated")
    
    def _create_dataset(self, latent_data, perturbations, expression_data):
        """Create dataset with one-hot perturbations"""
        class OneHotDataset(Dataset):
            def __init__(self, latent, perturbations, expression):
                self.latent = torch.FloatTensor(latent)
                self.perturbations = torch.FloatTensor(perturbations)
                self.expression = torch.FloatTensor(expression)
            
            def __len__(self):
                return len(self.latent)
            
            def __getitem__(self, idx):
                return self.latent[idx], self.perturbations[idx], self.expression[idx]
        
        return OneHotDataset(latent_data, perturbations, expression_data)
    
    def predict(self, 
                latent_data: np.ndarray, 
                perturbations: np.ndarray, 
                batch_size: int = 32) -> np.ndarray:
        """
        Predict expression for known perturbations
        """
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Predictions may be inaccurate.")
        
        self._validate_one_hot_perturbations(perturbations)
        
        self.model.eval()
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        if isinstance(perturbations, np.ndarray):
            perturbations = torch.FloatTensor(perturbations)
        
        predictions = []
        with torch.no_grad():
            for i in range(0, len(latent_data), batch_size):
                batch_latent = latent_data[i:i+batch_size].to(self.device)
                batch_perturbations = perturbations[i:i+batch_size].to(self.device)
                
                batch_pred = self.model(batch_latent, batch_perturbations, mode='one_hot')
                predictions.append(batch_pred.cpu())
        
        return torch.cat(predictions).numpy()
    
    def predict_novel_perturbation(self,
                                 latent_data: np.ndarray,
                                 similarity_matrix: np.ndarray,
                                 batch_size: int = 32) -> np.ndarray:
        """
        Predict response to novel perturbations
        """
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Novel perturbation prediction may be inaccurate.")
        
        assert similarity_matrix.shape[1] == self.num_known_perturbations, \
            f"Similarity matrix columns {similarity_matrix.shape[1]} must match known perturbations {self.num_known_perturbations}"
        
        self.model.eval()
        
        if isinstance(latent_data, np.ndarray):
            latent_data = torch.FloatTensor(latent_data)
        if isinstance(similarity_matrix, np.ndarray):
            similarity_matrix = torch.FloatTensor(similarity_matrix)
        
        predictions = []
        with torch.no_grad():
            for i in range(0, len(latent_data), batch_size):
                batch_latent = latent_data[i:i+batch_size].to(self.device)
                batch_similarity = similarity_matrix[i:i+batch_size].to(self.device)
                
                batch_pred = self.model(batch_latent, batch_similarity, mode='similarity')
                predictions.append(batch_pred.cpu())
        
        return torch.cat(predictions).numpy()
    
    def get_known_perturbation_prototypes(self) -> np.ndarray:
        """Get learned perturbation response prototypes"""
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Prototypes may be uninformative.")
        
        if self.perturbation_prototypes is None:
            self.model.eval()
            with torch.no_grad():
                self.perturbation_prototypes = self.model.get_perturbation_prototypes().cpu().numpy()
        
        return self.perturbation_prototypes
    
    def _pearson_correlation(self, pred, target):
        """Calculate Pearson correlation coefficient"""
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
        
        for latent, perturbations, target in train_loader:
            latent = latent.to(self.device)
            perturbations = perturbations.to(self.device)
            target = target.to(self.device)
            
            optimizer.zero_grad()
            pred = self.model(latent, perturbations, mode='one_hot')
            
            loss = loss_fn(pred, target)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            optimizer.step()
            
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
            for latent, perturbations, target in val_loader:
                latent = latent.to(self.device)
                perturbations = perturbations.to(self.device)
                target = target.to(self.device)
                
                pred = self.model(latent, perturbations, mode='one_hot')
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
        """Save model checkpoint"""
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_val_loss': best_loss,
            'training_history': history,
            'perturbation_prototypes': self.perturbation_prototypes,
            'model_config': {
                'latent_dim': self.latent_dim,
                'num_known_perturbations': self.num_known_perturbations,
                'gene_dim': self.gene_dim,
                'hidden_dims': self.hidden_dims
            }
        }, path)
    
    def load_model(self, model_path: str):
        """Load pre-trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.perturbation_prototypes = checkpoint.get('perturbation_prototypes')
        self.is_trained = True
        self.training_history = checkpoint.get('training_history')
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        print(f"✅ Model loaded! Best val loss: {self.best_val_loss:.4f}")

'''# Test the fixed implementation
def test_single_layer_fix():
    """Test the fixed single layer implementation"""
    
    print("🧪 Testing single layer configuration...")
    
    # Test with single hidden layer
    decoder_single = PerturbationAwareDecoder(
        latent_dim=100,
        num_known_perturbations=10,
        gene_dim=2000,
        hidden_dims=[512],  # Single element list
        perturbation_embedding_dim=128
    )
    
    # Generate test data
    n_samples = 100
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    perturbations = np.zeros((n_samples, 10))
    for i in range(n_samples):
        if i % 10 != 0:
            perturbations[i, np.random.randint(0, 10)] = 1.0
    
    expression_data = np.random.randn(n_samples, 2000).astype(np.float32)
    expression_data = np.maximum(expression_data, 0)
    
    # Test forward pass
    decoder_single.model.eval()
    with torch.no_grad():
        latent_tensor = torch.FloatTensor(latent_data[:5]).to(decoder_single.device)
        perturbations_tensor = torch.FloatTensor(perturbations[:5]).to(decoder_single.device)
        
        # Test known perturbation prediction
        output = decoder_single.model(latent_tensor, perturbations_tensor, mode='one_hot')
        print(f"✅ Known perturbation prediction shape: {output.shape}")
        
        # Test novel perturbation prediction
        similarity_matrix = np.random.rand(5, 10).astype(np.float32)
        similarity_tensor = torch.FloatTensor(similarity_matrix).to(decoder_single.device)
        novel_output = decoder_single.model(latent_tensor, similarity_tensor, mode='similarity')
        print(f"✅ Novel perturbation prediction shape: {novel_output.shape}")
    
    print("🎉 Single layer test passed!")

def test_multi_layer_fix():
    """Test the multi-layer implementation"""
    
    print("\n🧪 Testing multi-layer configuration...")
    
    # Test with multiple hidden layers
    decoder_multi = PerturbationAwareDecoder(
        latent_dim=100,
        num_known_perturbations=10,
        gene_dim=2000,
        hidden_dims=[256, 512, 1024],  # Multiple layers
        perturbation_embedding_dim=128
    )
    
    print("🎉 Multi-layer test passed!")

def test_edge_cases():
    """Test edge cases"""
    
    print("\n🧪 Testing edge cases...")
    
    # Test with different hidden_dims configurations
    configs = [
        [512],           # Single layer
        [256, 512],      # Two layers
        [128, 256, 512], # Three layers
        [1024],          # Wide single layer
        [64, 128, 256, 512, 1024]  # Deep network
    ]
    
    for i, hidden_dims in enumerate(configs):
        try:
            decoder = PerturbationAwareDecoder(
                latent_dim=50,
                num_known_perturbations=5,
                gene_dim=1000,
                hidden_dims=hidden_dims,
                perturbation_embedding_dim=64
            )
            print(f"✅ Config {i+1}: {hidden_dims} - Success")
        except Exception as e:
            print(f"❌ Config {i+1}: {hidden_dims} - Failed: {e}")
    
    print("🎉 Edge case testing completed!")

if __name__ == "__main__":
    # Run tests
    test_single_layer_fix()
    test_multi_layer_fix()
    test_edge_cases()
    
    # Example usage
    print("\n🎯 Example Usage:")
    
    # Single hidden layer example
    decoder = PerturbationAwareDecoder(
        latent_dim=100,
        num_known_perturbations=10,
        gene_dim=2000,
        hidden_dims=[512],  # Single hidden layer
        perturbation_embedding_dim=128
    )
    
    # Generate example data
    n_samples = 1000
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    perturbations = np.zeros((n_samples, 10))
    for i in range(n_samples):
        if i % 10 != 0:
            perturbations[i, np.random.randint(0, 10)] = 1.0
    
    # Simulate expression data
    base_weights = np.random.randn(100, 2000) * 0.1
    perturbation_effects = np.random.randn(10, 2000) * 0.5
    
    expression_data = np.tanh(latent_data.dot(base_weights))
    for i in range(n_samples):
        if perturbations[i].sum() > 0:
            perturb_id = np.argmax(perturbations[i])
            expression_data[i] += perturbation_effects[perturb_id]
    
    expression_data = np.maximum(expression_data, 0)
    
    print(f"📊 Example data shapes: Latent {latent_data.shape}, Perturbations {perturbations.shape}")
    
    # Train (commented out for quick testing)
    # history = decoder.train(
    #     train_latent=latent_data,
    #     train_perturbations=perturbations,
    #     train_expression=expression_data,
    #     batch_size=32,
    #     num_epochs=10  # Short training for testing
    # )
    
    print("🎉 All tests completed successfully!")'''