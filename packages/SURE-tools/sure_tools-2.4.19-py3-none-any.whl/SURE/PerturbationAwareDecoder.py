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
    Similarity matrix columns correspond to known perturbations for novel perturbation prediction
    """
    
    def __init__(self, 
                 latent_dim: int = 100,
                 num_known_perturbations: int = 50,  # Number of known perturbation types
                 gene_dim: int = 60000,
                 hidden_dims: List[int] = [512, 1024, 2048],
                 perturbation_embedding_dim: int = 128,
                 biological_prior_dim: int = 256,
                 dropout_rate: float = 0.1,
                 device: str = None):
        """
        Multi-modal decoder with correct similarity matrix definition
        
        Args:
            latent_dim: Latent variable dimension
            num_known_perturbations: Number of known perturbation types for one-hot encoding
            gene_dim: Number of genes
            hidden_dims: Hidden layer dimensions
            perturbation_embedding_dim: Embedding dimension for perturbations
            biological_prior_dim: Dimension for biological prior knowledge
            dropout_rate: Dropout rate
            device: Computation device
        """
        self.latent_dim = latent_dim
        self.num_known_perturbations = num_known_perturbations
        self.gene_dim = gene_dim
        self.hidden_dims = hidden_dims
        self.perturbation_embedding_dim = perturbation_embedding_dim
        self.biological_prior_dim = biological_prior_dim
        self.dropout_rate = dropout_rate
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize multi-modal model
        self.model = self._build_corrected_model()
        self.model.to(self.device)
        
        # Training state
        self.is_trained = False
        self.training_history = None
        self.best_val_loss = float('inf')
        self.known_perturbation_names = []  # For mapping indices to perturbation names
        self.perturbation_prototypes = None  # Learned perturbation representations
        
        print(f"🧬 PerturbationAwareDecoder Initialized:")
        print(f"   - Latent Dimension: {latent_dim}")
        print(f"   - Known Perturbations: {num_known_perturbations}")
        print(f"   - Gene Dimension: {gene_dim}")
        print(f"   - Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    class CorrectedPerturbationEncoder(nn.Module):
        """Encoder for one-hot encoded perturbations"""
        
        def __init__(self, num_perturbations: int, embedding_dim: int, hidden_dim: int):
            super().__init__()
            self.num_perturbations = num_perturbations
            
            # Embedding for perturbation types
            self.perturbation_embedding = nn.Embedding(num_perturbations, embedding_dim)
            
            # Projection to hidden space
            self.projection = nn.Sequential(
                nn.Linear(embedding_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, hidden_dim)
            )
            
            # Attention mechanism for perturbation context
            self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True)
            self.norm = nn.LayerNorm(hidden_dim)
        
        def forward(self, one_hot_perturbations):
            """
            Args:
                one_hot_perturbations: [batch_size, num_perturbations] one-hot encoded
            """
            batch_size = one_hot_perturbations.shape[0]
            
            # Convert one-hot to indices
            perturbation_indices = torch.argmax(one_hot_perturbations, dim=1)  # [batch_size]
            
            # Get perturbation embeddings
            perturbation_embeds = self.perturbation_embedding(perturbation_indices)  # [batch_size, embedding_dim]
            
            # Project to hidden space
            hidden_repr = self.projection(perturbation_embeds)  # [batch_size, hidden_dim]
            
            # Add sequence dimension for attention
            hidden_repr = hidden_repr.unsqueeze(1)  # [batch_size, 1, hidden_dim]
            
            # Self-attention for perturbation context
            attended, _ = self.attention(hidden_repr, hidden_repr, hidden_repr)
            attended = self.norm(hidden_repr + attended)
            
            return attended.squeeze(1)  # [batch_size, hidden_dim]
    
    class CrossModalFusion(nn.Module):
        """Cross-modal fusion of latent variables and perturbation information"""
        
        def __init__(self, latent_dim: int, perturbation_dim: int, fusion_dim: int):
            super().__init__()
            self.latent_projection = nn.Linear(latent_dim, fusion_dim)
            self.perturbation_projection = nn.Linear(perturbation_dim, fusion_dim)
            
            # Cross-attention
            self.cross_attention = nn.MultiheadAttention(
                fusion_dim, num_heads=8, batch_first=True
            )
            
            # Fusion gate
            self.fusion_gate = nn.Sequential(
                nn.Linear(fusion_dim * 2, fusion_dim),
                nn.Sigmoid()
            )
            
            self.norm = nn.LayerNorm(fusion_dim)
            self.dropout = nn.Dropout(0.1)
        
        def forward(self, latent, perturbation_encoded):
            # Project both modalities
            latent_proj = self.latent_projection(latent).unsqueeze(1)  # [batch_size, 1, fusion_dim]
            perturbation_proj = self.perturbation_projection(perturbation_encoded).unsqueeze(1)
            
            # Cross-attention: latent attends to perturbation
            attended, _ = self.cross_attention(latent_proj, perturbation_proj, perturbation_proj)
            
            # Gated fusion
            concatenated = torch.cat([attended, latent_proj], dim=-1)
            fusion_gate = self.fusion_gate(concatenated)
            fused = fusion_gate * attended + (1 - fusion_gate) * latent_proj
            
            fused = self.norm(fused)
            fused = self.dropout(fused)
            
            return fused.squeeze(1)
    
    class PerturbationResponseNetwork(nn.Module):
        """Network for predicting perturbation-specific responses"""
        
        def __init__(self, fusion_dim: int, gene_dim: int, hidden_dims: List[int]):
            super().__init__()
            
            # Base network
            layers = []
            input_dim = fusion_dim
            
            for hidden_dim in hidden_dims:
                layers.extend([
                    nn.Linear(input_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1)
                ])
                input_dim = hidden_dim
            
            self.base_network = nn.Sequential(*layers)
            self.final_projection = nn.Linear(hidden_dims[-1], gene_dim)
            
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
    
    class CorrectedNovelPerturbationPredictor(nn.Module):
        """Predictor for novel perturbations using similarity to known perturbations"""
        
        def __init__(self, num_known_perturbations: int, gene_dim: int, hidden_dim: int):
            super().__init__()
            self.num_known_perturbations = num_known_perturbations
            self.gene_dim = gene_dim
            
            # Learnable perturbation prototypes (response patterns for known perturbations)
            self.perturbation_prototypes = nn.Parameter(
                torch.randn(num_known_perturbations, gene_dim) * 0.1
            )
            
            # Similarity-based response generator
            self.response_generator = nn.Sequential(
                nn.Linear(num_known_perturbations, hidden_dim),  # Input: similarity to known perturbations
                nn.ReLU(),
                nn.Linear(hidden_dim, gene_dim)
            )
            
            # Attention mechanism for combining prototypes
            self.attention_weights = nn.Parameter(torch.randn(num_known_perturbations, 1))
            
        def forward(self, similarity_matrix, latent_features=None):
            """
            Predict response to novel perturbation using similarity to known perturbations
            
            Args:
                similarity_matrix: [batch_size, num_known_perturbations] 
                    Each row: similarity scores between novel perturbation and known perturbations
                latent_features: [batch_size, latent_dim] (optional) cell state information
            
            Returns:
                expression: [batch_size, gene_dim] predicted expression
            """
            batch_size = similarity_matrix.shape[0]
            
            # Method 1: Weighted combination of known perturbation prototypes
            # similarity_matrix: [batch_size, num_known_perturbations]
            # perturbation_prototypes: [num_known_perturbations, gene_dim]
            weighted_prototypes = torch.matmul(similarity_matrix, self.perturbation_prototypes)  # [batch_size, gene_dim]
            
            # Method 2: Direct generation from similarity profile
            generated_response = self.response_generator(similarity_matrix)  # [batch_size, gene_dim]
            
            # Combine both methods with learned weights
            combination_weights = torch.sigmoid(
                similarity_matrix.mean(dim=1, keepdim=True)  # [batch_size, 1]
            )
            
            combined_response = (combination_weights * weighted_prototypes + 
                               (1 - combination_weights) * generated_response)
            
            # If latent features provided, modulate response by cell state
            if latent_features is not None:
                # Simple modulation based on latent state
                modulation = torch.sigmoid(latent_features.mean(dim=1, keepdim=True))  # [batch_size, 1]
                combined_response = combined_response * (1 + 0.5 * modulation)
            
            return F.softplus(combined_response)
    
    class CorrectedMultimodalDecoder(nn.Module):
        """Main decoder with corrected similarity matrix handling"""
        
        def __init__(self, latent_dim: int, num_known_perturbations: int, gene_dim: int, 
                    hidden_dims: List[int], perturbation_embedding_dim: int, 
                    biological_prior_dim: int, dropout_rate: float):
            super().__init__()
            
            self.num_known_perturbations = num_known_perturbations
            self.latent_dim = latent_dim
            self.gene_dim = gene_dim
            
            # Perturbation encoder for one-hot inputs
            self.perturbation_encoder = PerturbationAwareDecoder.CorrectedPerturbationEncoder(
                num_known_perturbations, perturbation_embedding_dim, hidden_dims[0]
            )
            
            # Cross-modal fusion
            self.cross_modal_fusion = PerturbationAwareDecoder.CrossModalFusion(
                latent_dim, hidden_dims[0], hidden_dims[0]
            )
            
            # Response network for known perturbations
            self.response_network = PerturbationAwareDecoder.PerturbationResponseNetwork(
                hidden_dims[0], gene_dim, hidden_dims[1:]
            )
            
            # Novel perturbation predictor
            self.novel_predictor = PerturbationAwareDecoder.CorrectedNovelPerturbationPredictor(
                num_known_perturbations, gene_dim, hidden_dims[0]
            )
            
        def forward(self, latent, perturbation_matrix, mode='one_hot'):
            """
            Forward pass with corrected similarity matrix definition
            
            Args:
                latent: [batch_size, latent_dim] latent variables
                perturbation_matrix: 
                    - one_hot mode: [batch_size, num_known_perturbations] one-hot encoded
                    - similarity mode: [batch_size, num_known_perturbations] similarity scores
                mode: 'one_hot' for known perturbations, 'similarity' for novel perturbations
            """
            if mode == 'one_hot':
                # Known perturbation pathway
                perturbation_encoded = self.perturbation_encoder(perturbation_matrix)
                fused = self.cross_modal_fusion(latent, perturbation_encoded)
                expression = self.response_network(fused)
                
            elif mode == 'similarity':
                # Novel perturbation pathway
                # perturbation_matrix: similarity to known perturbations [batch_size, num_known_perturbations]
                expression = self.novel_predictor(perturbation_matrix, latent)
                
            else:
                raise ValueError(f"Unknown mode: {mode}. Use 'one_hot' or 'similarity'")
            
            return expression
        
        def get_perturbation_prototypes(self):
            """Get learned perturbation response prototypes"""
            return self.novel_predictor.perturbation_prototypes.detach()
    
    def _build_corrected_model(self):
        """Build the corrected model"""
        return self.CorrectedMultimodalDecoder(
            self.latent_dim, self.num_known_perturbations, self.gene_dim,
            self.hidden_dims, self.perturbation_embedding_dim,
            self.biological_prior_dim, self.dropout_rate
        )
    
    def train(self,
              train_latent: np.ndarray,
              train_perturbations: np.ndarray,  # One-hot encoded [n_samples, num_known_perturbations]
              train_expression: np.ndarray,
              val_latent: np.ndarray = None,
              val_perturbations: np.ndarray = None,
              val_expression: np.ndarray = None,
              batch_size: int = 32,
              num_epochs: int = 200,
              learning_rate: float = 1e-4,
              checkpoint_path: str = 'corrected_decoder.pth') -> Dict:
        """
        Train the decoder with one-hot encoded perturbations
        """
        print("🧬 Starting Training with Corrected Similarity Definition...")
        
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
        print(f"🧪 Known perturbations: {self.num_known_perturbations}")
        
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
        print(f"📊 Learned perturbation prototypes: {self.perturbation_prototypes.shape}")
        return history
    
    def _validate_one_hot_perturbations(self, perturbations):
        """Validate that perturbations are proper one-hot encodings"""
        assert perturbations.shape[1] == self.num_known_perturbations, \
            f"Perturbation dimension {perturbations.shape[1]} doesn't match expected {self.num_known_perturbations}"
        
        # Check that each row sums to 1 (perturbation) or 0 (control)
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
        Predict expression for known perturbations using one-hot encoding
        
        Args:
            latent_data: [n_samples, latent_dim] latent variables
            perturbations: [n_samples, num_known_perturbations] one-hot encoded perturbations
            batch_size: Batch size
        
        Returns:
            expression: [n_samples, gene_dim] predicted expression
        """
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Predictions may be inaccurate.")
        
        # Validate one-hot encoding
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
                
                # Use one-hot mode for known perturbations
                batch_pred = self.model(batch_latent, batch_perturbations, mode='one_hot')
                predictions.append(batch_pred.cpu())
        
        return torch.cat(predictions).numpy()
    
    def predict_novel_perturbation(self,
                                 latent_data: np.ndarray,
                                 similarity_matrix: np.ndarray,
                                 batch_size: int = 32) -> np.ndarray:
        """
        Predict response to novel perturbations using similarity to known perturbations
        
        Args:
            latent_data: [n_samples, latent_dim] latent variables
            similarity_matrix: [n_samples, num_known_perturbations] 
                Each row: similarity scores between novel perturbation and known perturbations
                Columns correspond to model's known perturbation types
            batch_size: Batch size
        
        Returns:
            expression: [n_samples, gene_dim] predicted expression
        """
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Novel perturbation prediction may be inaccurate.")
        
        # Validate similarity matrix dimensions
        assert similarity_matrix.shape[1] == self.num_known_perturbations, \
            f"Similarity matrix columns {similarity_matrix.shape[1]} must match known perturbations {self.num_known_perturbations}"
        
        # Validate similarity scores are reasonable (0-1 range recommended)
        if np.any(similarity_matrix < 0) or np.any(similarity_matrix > 2):
            warnings.warn("⚠️ Similarity scores outside typical range [0, 1]. Consider normalizing.")
        
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
                
                # Use similarity mode for novel perturbations
                batch_pred = self.model(batch_latent, batch_similarity, mode='similarity')
                predictions.append(batch_pred.cpu())
        
        return torch.cat(predictions).numpy()
    
    def get_known_perturbation_prototypes(self) -> np.ndarray:
        """Get learned response prototypes for known perturbations"""
        if not self.is_trained:
            warnings.warn("⚠️ Model not trained. Prototypes may be uninformative.")
        
        if self.perturbation_prototypes is None:
            self.model.eval()
            with torch.no_grad():
                self.perturbation_prototypes = self.model.get_perturbation_prototypes().cpu().numpy()
        
        return self.perturbation_prototypes
    
    def compute_similarity(self, novel_perturbation_features: np.ndarray, 
                          known_perturbation_features: np.ndarray = None) -> np.ndarray:
        """
        Compute similarity matrix between novel perturbations and known perturbations
        
        Args:
            novel_perturbation_features: [n_novel, feature_dim] features of novel perturbations
            known_perturbation_features: [n_known, feature_dim] features of known perturbations
                If None, uses learned perturbation prototypes
        
        Returns:
            similarity_matrix: [n_novel, num_known_perturbations] similarity scores
        """
        if known_perturbation_features is None:
            # Use learned prototypes
            known_perturbation_features = self.get_known_perturbation_prototypes()
        
        # Normalize features for cosine similarity
        novel_norm = novel_perturbation_features / (np.linalg.norm(novel_perturbation_features, axis=1, keepdims=True) + 1e-8)
        known_norm = known_perturbation_features / (np.linalg.norm(known_perturbation_features, axis=1, keepdims=True) + 1e-8)
        
        # Compute cosine similarity
        similarity_matrix = np.dot(novel_norm, known_norm.T)
        
        return similarity_matrix
    
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

'''# Example usage
def example_usage():
    """Example demonstration of the corrected perturbation decoder"""
    
    # Initialize decoder
    decoder = PerturbationAwareDecoder(
        latent_dim=100,
        num_known_perturbations=10,  # 10 known perturbation types
        gene_dim=2000,  # Reduced for example
        hidden_dims=[256, 512, 1024],
        perturbation_embedding_dim=128
    )
    
    # Generate example data
    n_samples = 1000
    n_perturbations = 10
    
    # Latent variables
    latent_data = np.random.randn(n_samples, 100).astype(np.float32)
    
    # One-hot encoded perturbations
    perturbations = np.zeros((n_samples, n_perturbations))
    for i in range(n_samples):
        if i % 10 != 0:  # 90% perturbed, 10% control
            perturb_id = np.random.randint(0, n_perturbations)
            perturbations[i, perturb_id] = 1.0
    
    # Expression data with perturbation effects
    base_weights = np.random.randn(100, 2000) * 0.1
    perturbation_effects = np.random.randn(n_perturbations, 2000) * 0.5
    
    expression_data = np.tanh(latent_data.dot(base_weights))
    for i in range(n_samples):
        if perturbations[i].sum() > 0:  # Perturbed sample
            perturb_id = np.argmax(perturbations[i])
            expression_data[i] += perturbation_effects[perturb_id]
    
    expression_data = np.maximum(expression_data, 0)
    
    print(f"📊 Data shapes: Latent {latent_data.shape}, Perturbations {perturbations.shape}, Expression {expression_data.shape}")
    print(f"🧪 Control samples: {(perturbations.sum(axis=1) == 0).sum()}")
    print(f"🧪 Perturbed samples: {(perturbations.sum(axis=1) > 0).sum()}")
    
    # Train with one-hot perturbations
    history = decoder.train(
        train_latent=latent_data,
        train_perturbations=perturbations,
        train_expression=expression_data,
        batch_size=32,
        num_epochs=50
    )
    
    # Test predictions with one-hot perturbations
    test_latent = np.random.randn(10, 100).astype(np.float32)
    test_perturbations = np.zeros((10, n_perturbations))
    for i in range(10):
        test_perturbations[i, i % n_perturbations] = 1.0  # One-hot encoding
    
    predictions = decoder.predict(test_latent, test_perturbations)
    print(f"🔮 Known perturbation prediction shape: {predictions.shape}")
    
    # Test novel perturbation prediction with similarity matrix
    test_latent_novel = np.random.randn(5, 100).astype(np.float32)
    
    # Create similarity matrix: [5, 10] - 5 novel perturbations, similarity to 10 known perturbations
    similarity_matrix = np.random.rand(5, n_perturbations)
    similarity_matrix = similarity_matrix / similarity_matrix.sum(axis=1, keepdims=True)  # Normalize rows
    
    novel_predictions = decoder.predict_novel_perturbation(test_latent_novel, similarity_matrix)
    print(f"🔮 Novel perturbation prediction shape: {novel_predictions.shape}")
    
    # Get learned perturbation prototypes
    prototypes = decoder.get_known_perturbation_prototypes()
    print(f"📊 Perturbation prototypes shape: {prototypes.shape}")
    
    return decoder

if __name__ == "__main__":
    example_usage()'''