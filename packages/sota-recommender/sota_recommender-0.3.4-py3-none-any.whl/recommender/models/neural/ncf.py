"""
NCF: Neural Collaborative Filtering

Reference:
Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu and Tat-Seng Chua. 2017.
Neural Collaborative Filtering. In WWW '17.

NCF combines Generalized Matrix Factorization (GMF) with Multi-Layer Perceptron (MLP)
for collaborative filtering.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple, Any, Optional
from ...core.base import ImplicitRecommender

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class NCFDataset(Dataset):
        """Dataset for NCF training."""
        
        def __init__(self, user_ids, item_ids, labels):
            self.user_ids = torch.LongTensor(user_ids)
            self.item_ids = torch.LongTensor(item_ids)
            self.labels = torch.FloatTensor(labels)
        
        def __len__(self):
            return len(self.user_ids)
        
        def __getitem__(self, idx):
            return self.user_ids[idx], self.item_ids[idx], self.labels[idx]


    class NCFModel(nn.Module):
        """Neural Collaborative Filtering model."""
        
        def __init__(
            self,
            n_users: int,
            n_items: int,
            embedding_dim: int = 64,
            hidden_layers: List[int] = [128, 64, 32],
            dropout: float = 0.2
        ):
            super(NCFModel, self).__init__()
            
            self.n_users = n_users
            self.n_items = n_items
            self.embedding_dim = embedding_dim
            
            # GMF embeddings
            self.gmf_user_embedding = nn.Embedding(n_users, embedding_dim)
            self.gmf_item_embedding = nn.Embedding(n_items, embedding_dim)
            
            # MLP embeddings
            self.mlp_user_embedding = nn.Embedding(n_users, embedding_dim)
            self.mlp_item_embedding = nn.Embedding(n_items, embedding_dim)
            
            # MLP layers
            mlp_layers = []
            input_size = embedding_dim * 2
            
            for hidden_size in hidden_layers:
                mlp_layers.append(nn.Linear(input_size, hidden_size))
                mlp_layers.append(nn.ReLU())
                mlp_layers.append(nn.Dropout(dropout))
                input_size = hidden_size
            
            self.mlp = nn.Sequential(*mlp_layers)
            
            # Final prediction layer
            self.output = nn.Linear(embedding_dim + hidden_layers[-1], 1)
            self.sigmoid = nn.Sigmoid()
            
            # Initialize weights
            self._init_weights()
        
        def _init_weights(self):
            """Initialize model weights."""
            for module in self.modules():
                if isinstance(module, nn.Embedding):
                    nn.init.normal_(module.weight, std=0.01)
                elif isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, user_ids, item_ids):
            """
            Forward pass.
            
            Args:
                user_ids: User indices
                item_ids: Item indices
                
            Returns:
                Predicted scores
            """
            # GMF part
            gmf_user = self.gmf_user_embedding(user_ids)
            gmf_item = self.gmf_item_embedding(item_ids)
            gmf_output = gmf_user * gmf_item
            
            # MLP part
            mlp_user = self.mlp_user_embedding(user_ids)
            mlp_item = self.mlp_item_embedding(item_ids)
            mlp_input = torch.cat([mlp_user, mlp_item], dim=-1)
            mlp_output = self.mlp(mlp_input)
            
            # Concatenate GMF and MLP
            combined = torch.cat([gmf_output, mlp_output], dim=-1)
            
            # Final prediction
            output = self.output(combined)
            output = self.sigmoid(output)
            
            return output.squeeze()


class NCFRecommender(ImplicitRecommender):
    """
    Neural Collaborative Filtering Recommender.
    
    Combines:
    - GMF (Generalized Matrix Factorization): element-wise product of embeddings
    - MLP: neural network on concatenated embeddings
    
    Architecture: NeuMF = GMF ⊕ MLP
    """
    
    def __init__(
        self,
        embedding_dim: int = 64,
        hidden_layers: List[int] = [128, 64, 32],
        dropout: float = 0.2,
        learning_rate: float = 0.001,
        batch_size: int = 256,
        epochs: int = 20,
        n_negatives: int = 4,
        device: str = 'auto'
    ):
        """
        Initialize NCF recommender.
        
        Args:
            embedding_dim: Dimension of embeddings
            hidden_layers: Sizes of MLP hidden layers
            dropout: Dropout rate
            learning_rate: Learning rate
            batch_size: Batch size for training
            epochs: Number of training epochs
            n_negatives: Number of negative samples per positive
            device: Device to use ('auto', 'cpu', 'cuda')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for NCF. Install with: pip install torch")
        
        super().__init__()
        
        self.embedding_dim = embedding_dim
        self.hidden_layers = hidden_layers
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.n_negatives = n_negatives
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model = None
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'NCFRecommender':
        """
        Train NCF model.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id']
            
        Returns:
            self
        """
        print(f"Training NCF model on {self.device}...")
        
        # Create mappings
        self._create_mappings(interactions)
        self._build_seen_items(interactions)
        
        # Prepare training data with negative sampling
        train_data = self._prepare_training_data(interactions)
        
        # Create model
        self.model = NCFModel(
            n_users=self.n_users,
            n_items=self.n_items,
            embedding_dim=self.embedding_dim,
            hidden_layers=self.hidden_layers,
            dropout=self.dropout
        ).to(self.device)
        
        # Setup training
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.BCELoss()
        
        # Create dataset and dataloader
        dataset = NCFDataset(
            train_data['user_idx'],
            train_data['item_idx'],
            train_data['label']
        )
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        # Training loop
        print(f"Training for {self.epochs} epochs...")
        self.model.train()
        
        for epoch in range(self.epochs):
            total_loss = 0.0
            n_batches = 0
            
            for user_ids, item_ids, labels in dataloader:
                user_ids = user_ids.to(self.device)
                item_ids = item_ids.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                predictions = self.model(user_ids, item_ids)
                loss = criterion(predictions, labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                n_batches += 1
            
            avg_loss = total_loss / n_batches
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"  Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}")
        
        self.is_fitted = True
        print("NCF training complete!")
        
        return self
    
    def _prepare_training_data(self, interactions: pd.DataFrame) -> pd.DataFrame:
        """Prepare training data with negative sampling."""
        from ...data.samplers import UniformSampler
        
        # Positive samples
        positive_samples = []
        for _, row in interactions.iterrows():
            user_idx = self.user_mapping[row['user_id']]
            item_idx = self.item_mapping[row['item_id']]
            positive_samples.append({
                'user_idx': user_idx,
                'item_idx': item_idx,
                'label': 1
            })
        
        # Negative sampling
        sampler = UniformSampler(n_items=self.n_items)
        negative_samples = []
        
        for user_idx, positive_items in self.seen_items.items():
            n_negatives = len(positive_items) * self.n_negatives
            neg_items = sampler.sample(user_idx, positive_items, n_negatives)
            
            for neg_item in neg_items:
                negative_samples.append({
                    'user_idx': user_idx,
                    'item_idx': neg_item,
                    'label': 0
                })
        
        # Combine
        all_samples = positive_samples + negative_samples
        train_df = pd.DataFrame(all_samples)
        
        print(f"Training data: {len(positive_samples)} positives, "
              f"{len(negative_samples)} negatives")
        
        return train_df
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict scores for user-item pairs."""
        self._check_fitted()
        
        self.model.eval()
        
        predictions = []
        
        with torch.no_grad():
            for user_id, item_id in zip(user_ids, item_ids):
                if user_id not in self.user_mapping or item_id not in self.item_mapping:
                    predictions.append(0.0)
                    continue
                
                user_idx = self.user_mapping[user_id]
                item_idx = self.item_mapping[item_id]
                
                user_tensor = torch.LongTensor([user_idx]).to(self.device)
                item_tensor = torch.LongTensor([item_idx]).to(self.device)
                
                score = self.model(user_tensor, item_tensor).item()
                predictions.append(score)
        
        return np.array(predictions)
    
    def recommend(
        self,
        user_ids: np.ndarray,
        k: int = 10,
        exclude_seen: bool = True,
        **kwargs
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """Generate top-K recommendations."""
        self._check_fitted()
        
        self.model.eval()
        recommendations = {}
        
        with torch.no_grad():
            for user_id in user_ids:
                if user_id not in self.user_mapping:
                    recommendations[user_id] = []
                    continue
                
                user_idx = self.user_mapping[user_id]
                
                # Compute scores for all items
                user_tensor = torch.LongTensor([user_idx] * self.n_items).to(self.device)
                item_tensor = torch.LongTensor(list(range(self.n_items))).to(self.device)
                
                scores = self.model(user_tensor, item_tensor).cpu().numpy()
                
                # Exclude seen items
                if exclude_seen:
                    seen_items = self.seen_items.get(user_idx, set())
                    for item_idx in seen_items:
                        scores[item_idx] = -np.inf
                
                # Get top-k
                top_indices = np.argsort(scores)[-k:][::-1]
                
                rec_list = []
                for item_idx in top_indices:
                    if scores[item_idx] > -np.inf:
                        item_id = self.reverse_item_mapping[item_idx]
                        score = scores[item_idx]
                        rec_list.append((item_id, float(score)))
                
                recommendations[user_id] = rec_list
        
        return recommendations
    
    def _get_model_state(self) -> Dict[str, Any]:
        """Get model state for serialization."""
        return {
            'model_state_dict': self.model.state_dict() if self.model else None,
            'seen_items': self.seen_items,
            'embedding_dim': self.embedding_dim,
            'hidden_layers': self.hidden_layers,
            'dropout': self.dropout
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.seen_items = state['seen_items']
        self.embedding_dim = state['embedding_dim']
        self.hidden_layers = state['hidden_layers']
        self.dropout = state['dropout']
        
        if state['model_state_dict'] is not None:
            self.model = NCFModel(
                n_users=self.n_users,
                n_items=self.n_items,
                embedding_dim=self.embedding_dim,
                hidden_layers=self.hidden_layers,
                dropout=self.dropout
            ).to(self.device)
            self.model.load_state_dict(state['model_state_dict'])

