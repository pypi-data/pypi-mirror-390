"""
LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation

Reference:
Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, Meng Wang. 2020.
LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. 
SIGIR '20.

LightGCN simplifies GCN by removing feature transformation and nonlinear activation,
keeping only the neighborhood aggregation for collaborative filtering.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple, Any, Optional
from ...core.base import ImplicitRecommender

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    import torch.optim as optim
    from scipy import sparse
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class LightGCNModel(nn.Module):
        """
        LightGCN model implementation.
        
        Key innovation: Simplify GCN by removing feature transformation and 
        nonlinear activation, keeping only neighborhood aggregation.
        """
        
        def __init__(
            self,
            n_users: int,
            n_items: int,
            embedding_dim: int = 64,
            n_layers: int = 3,
            dropout: float = 0.0
        ):
            super(LightGCNModel, self).__init__()
            
            self.n_users = n_users
            self.n_items = n_items
            self.embedding_dim = embedding_dim
            self.n_layers = n_layers
            self.dropout = dropout
            
            # Initialize embeddings
            self.user_embedding = nn.Embedding(n_users, embedding_dim)
            self.item_embedding = nn.Embedding(n_items, embedding_dim)
            
            # Initialize with Xavier
            nn.init.xavier_uniform_(self.user_embedding.weight)
            nn.init.xavier_uniform_(self.item_embedding.weight)
        
        def compute_graph_convolution(
            self,
            user_emb: torch.Tensor,
            item_emb: torch.Tensor,
            edge_index: torch.Tensor,
            edge_weight: torch.Tensor
        ) -> Tuple[torch.Tensor, torch.Tensor]:
            """
            Perform one layer of graph convolution.
            
            Args:
                user_emb: User embeddings
                item_emb: Item embeddings
                edge_index: Edge indices [2, num_edges]
                edge_weight: Edge weights (normalized)
                
            Returns:
                Updated user and item embeddings
            """
            # Combine user and item embeddings
            all_emb = torch.cat([user_emb, item_emb], dim=0)
            
            # Message passing
            # For each edge (u, i), aggregate neighbor embeddings
            src_emb = all_emb[edge_index[0]]  # Source node embeddings
            
            # Weighted aggregation
            messages = src_emb * edge_weight.unsqueeze(1)
            
            # Aggregate messages to target nodes
            new_emb = torch.zeros_like(all_emb)
            new_emb.index_add_(0, edge_index[1], messages)
            
            # Split back to user and item
            new_user_emb = new_emb[:self.n_users]
            new_item_emb = new_emb[self.n_users:]
            
            return new_user_emb, new_item_emb
        
        def forward(
            self,
            edge_index: torch.Tensor,
            edge_weight: torch.Tensor
        ) -> Tuple[torch.Tensor, torch.Tensor]:
            """
            Forward pass: multi-layer graph convolution.
            
            Args:
                edge_index: Edge indices [2, num_edges]
                edge_weight: Edge weights (normalized)
                
            Returns:
                Final user and item embeddings
            """
            # Initial embeddings (layer 0)
            user_emb = self.user_embedding.weight
            item_emb = self.item_embedding.weight
            
            # Store embeddings from each layer
            all_user_embs = [user_emb]
            all_item_embs = [item_emb]
            
            # Multi-layer propagation
            for layer in range(self.n_layers):
                user_emb, item_emb = self.compute_graph_convolution(
                    user_emb, item_emb, edge_index, edge_weight
                )
                
                # Apply dropout
                if self.dropout > 0 and self.training:
                    user_emb = F.dropout(user_emb, p=self.dropout)
                    item_emb = F.dropout(item_emb, p=self.dropout)
                
                all_user_embs.append(user_emb)
                all_item_embs.append(item_emb)
            
            # Layer combination: simple mean
            final_user_emb = torch.mean(torch.stack(all_user_embs), dim=0)
            final_item_emb = torch.mean(torch.stack(all_item_embs), dim=0)
            
            return final_user_emb, final_item_emb
        
        def predict(
            self,
            user_indices: torch.Tensor,
            item_indices: torch.Tensor,
            user_emb: torch.Tensor,
            item_emb: torch.Tensor
        ) -> torch.Tensor:
            """
            Predict scores for user-item pairs.
            
            Args:
                user_indices: User indices
                item_indices: Item indices
                user_emb: User embeddings
                item_emb: Item embeddings
                
            Returns:
                Predicted scores
            """
            u_emb = user_emb[user_indices]
            i_emb = item_emb[item_indices]
            
            # Inner product
            scores = (u_emb * i_emb).sum(dim=1)
            
            return scores
        
        def bpr_loss(
            self,
            user_indices: torch.Tensor,
            pos_item_indices: torch.Tensor,
            neg_item_indices: torch.Tensor,
            user_emb: torch.Tensor,
            item_emb: torch.Tensor
        ) -> torch.Tensor:
            """
            Bayesian Personalized Ranking (BPR) loss.
            
            Loss = -log(sigmoid(score_pos - score_neg))
            """
            # Positive scores
            pos_scores = self.predict(user_indices, pos_item_indices, user_emb, item_emb)
            
            # Negative scores
            neg_scores = self.predict(user_indices, neg_item_indices, user_emb, item_emb)
            
            # BPR loss
            loss = -torch.log(torch.sigmoid(pos_scores - neg_scores) + 1e-10).mean()
            
            return loss
        
        def regularization_loss(
            self,
            user_indices: torch.Tensor,
            pos_item_indices: torch.Tensor,
            neg_item_indices: torch.Tensor
        ) -> torch.Tensor:
            """
            L2 regularization on embeddings.
            """
            u_emb = self.user_embedding(user_indices)
            pos_i_emb = self.item_embedding(pos_item_indices)
            neg_i_emb = self.item_embedding(neg_item_indices)
            
            reg_loss = (u_emb.norm(2).pow(2) + 
                       pos_i_emb.norm(2).pow(2) + 
                       neg_i_emb.norm(2).pow(2)) / u_emb.size(0)
            
            return reg_loss


    class LightGCNDataset(Dataset):
        """Dataset for LightGCN training with BPR."""
        
        def __init__(
            self,
            user_item_pairs: List[Tuple[int, int]],
            n_items: int,
            user_positive_items: Dict[int, Set[int]],
            n_negatives: int = 1
        ):
            self.user_item_pairs = user_item_pairs
            self.n_items = n_items
            self.user_positive_items = user_positive_items
            self.n_negatives = n_negatives
        
        def __len__(self):
            return len(self.user_item_pairs)
        
        def __getitem__(self, idx):
            user_idx, pos_item_idx = self.user_item_pairs[idx]
            
            # Sample negative items
            neg_items = []
            user_positives = self.user_positive_items.get(user_idx, set())
            
            for _ in range(self.n_negatives):
                # Sample until we get a negative item
                while True:
                    neg_item = np.random.randint(0, self.n_items)
                    if neg_item not in user_positives:
                        neg_items.append(neg_item)
                        break
            
            return user_idx, pos_item_idx, neg_items[0]


class LightGCNRecommender(ImplicitRecommender):
    """
    LightGCN: Graph Neural Network for Collaborative Filtering.
    
    Key features:
    - Simplified GCN architecture (no feature transformation, no activation)
    - Multi-layer neighborhood aggregation
    - BPR loss for implicit feedback
    - State-of-the-art performance on many benchmarks
    """
    
    def __init__(
        self,
        embedding_dim: int = 64,
        n_layers: int = 3,
        dropout: float = 0.0,
        learning_rate: float = 0.001,
        reg_weight: float = 1e-4,
        batch_size: int = 1024,
        epochs: int = 50,
        device: str = 'auto'
    ):
        """
        Initialize LightGCN recommender.
        
        Args:
            embedding_dim: Dimension of embeddings
            n_layers: Number of graph convolution layers
            dropout: Dropout rate
            learning_rate: Learning rate
            reg_weight: Regularization weight
            batch_size: Batch size for training
            epochs: Number of training epochs
            device: Device to use ('auto', 'cpu', 'cuda')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for LightGCN. Install with: pip install torch")
        
        super().__init__()
        
        self.embedding_dim = embedding_dim
        self.n_layers = n_layers
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.reg_weight = reg_weight
        self.batch_size = batch_size
        self.epochs = epochs
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model = None
        self.edge_index = None
        self.edge_weight = None
    
    def _build_graph(self, interactions: pd.DataFrame):
        """
        Build user-item bipartite graph.
        
        Graph structure:
        - Nodes: users (0 to n_users-1) + items (n_users to n_users+n_items-1)
        - Edges: user-item interactions (bidirectional)
        """
        # Build edge list
        edges = []
        for _, row in interactions.iterrows():
            user_idx = self.user_mapping[row['user_id']]
            item_idx = self.item_mapping[row['item_id']]
            
            # User -> Item edge
            edges.append([user_idx, self.n_users + item_idx])
            # Item -> User edge (for undirected graph)
            edges.append([self.n_users + item_idx, user_idx])
        
        edge_index = torch.LongTensor(edges).t().contiguous()
        
        # Compute edge weights (normalization)
        # For each edge, weight = 1 / sqrt(degree_u * degree_i)
        user_degrees = interactions.groupby('user_id').size()
        item_degrees = interactions.groupby('item_id').size()
        
        edge_weights = []
        for _, row in interactions.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']
            
            deg_u = user_degrees[user_id]
            deg_i = item_degrees[item_id]
            
            weight = 1.0 / np.sqrt(deg_u * deg_i)
            
            # Add weight for both directions
            edge_weights.append(weight)
            edge_weights.append(weight)
        
        edge_weight = torch.FloatTensor(edge_weights)
        
        return edge_index, edge_weight
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'LightGCNRecommender':
        """
        Train LightGCN model.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id']
            
        Returns:
            self
        """
        print(f"Training LightGCN model on {self.device}...")
        
        # Create mappings
        self._create_mappings(interactions)
        self._build_seen_items(interactions)
        
        # Build graph
        print("Building user-item graph...")
        self.edge_index, self.edge_weight = self._build_graph(interactions)
        self.edge_index = self.edge_index.to(self.device)
        self.edge_weight = self.edge_weight.to(self.device)
        
        # Create model
        self.model = LightGCNModel(
            n_users=self.n_users,
            n_items=self.n_items,
            embedding_dim=self.embedding_dim,
            n_layers=self.n_layers,
            dropout=self.dropout
        ).to(self.device)
        
        # Prepare training data
        user_item_pairs = []
        for _, row in interactions.iterrows():
            user_idx = self.user_mapping[row['user_id']]
            item_idx = self.item_mapping[row['item_id']]
            user_item_pairs.append((user_idx, item_idx))
        
        dataset = LightGCNDataset(
            user_item_pairs=user_item_pairs,
            n_items=self.n_items,
            user_positive_items=self.seen_items,
            n_negatives=1
        )
        
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0
        )
        
        # Setup optimizer
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Training loop
        print(f"Training for {self.epochs} epochs...")
        self.model.train()
        
        for epoch in range(self.epochs):
            total_loss = 0.0
            n_batches = 0
            
            for batch in dataloader:
                user_indices, pos_item_indices, neg_item_indices = batch
                user_indices = user_indices.to(self.device)
                pos_item_indices = pos_item_indices.to(self.device)
                neg_item_indices = neg_item_indices.to(self.device)
                
                # Forward pass: get embeddings
                user_emb, item_emb = self.model(self.edge_index, self.edge_weight)
                
                # Compute BPR loss
                bpr_loss = self.model.bpr_loss(
                    user_indices, pos_item_indices, neg_item_indices,
                    user_emb, item_emb
                )
                
                # Regularization
                reg_loss = self.model.regularization_loss(
                    user_indices, pos_item_indices, neg_item_indices
                )
                
                # Total loss
                loss = bpr_loss + self.reg_weight * reg_loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                n_batches += 1
            
            avg_loss = total_loss / n_batches
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"  Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}")
        
        self.is_fitted = True
        print("LightGCN training complete!")
        
        return self
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict scores for user-item pairs."""
        self._check_fitted()
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            # Get final embeddings
            user_emb, item_emb = self.model(self.edge_index, self.edge_weight)
            
            for user_id, item_id in zip(user_ids, item_ids):
                if user_id not in self.user_mapping or item_id not in self.item_mapping:
                    predictions.append(0.0)
                    continue
                
                user_idx = self.user_mapping[user_id]
                item_idx = self.item_mapping[item_id]
                
                user_tensor = torch.LongTensor([user_idx]).to(self.device)
                item_tensor = torch.LongTensor([item_idx]).to(self.device)
                
                score = self.model.predict(user_tensor, item_tensor, user_emb, item_emb).item()
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
            # Get final embeddings
            user_emb, item_emb = self.model(self.edge_index, self.edge_weight)
            user_emb = user_emb.cpu().numpy()
            item_emb = item_emb.cpu().numpy()
            
            for user_id in user_ids:
                if user_id not in self.user_mapping:
                    recommendations[user_id] = []
                    continue
                
                user_idx = self.user_mapping[user_id]
                
                # Compute scores for all items
                scores = user_emb[user_idx] @ item_emb.T
                
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
            'edge_index': self.edge_index,
            'edge_weight': self.edge_weight,
            'seen_items': self.seen_items,
            'embedding_dim': self.embedding_dim,
            'n_layers': self.n_layers,
            'dropout': self.dropout
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.seen_items = state['seen_items']
        self.embedding_dim = state['embedding_dim']
        self.n_layers = state['n_layers']
        self.dropout = state['dropout']
        self.edge_index = state['edge_index']
        self.edge_weight = state['edge_weight']
        
        if state['model_state_dict'] is not None:
            self.model = LightGCNModel(
                n_users=self.n_users,
                n_items=self.n_items,
                embedding_dim=self.embedding_dim,
                n_layers=self.n_layers,
                dropout=self.dropout
            ).to(self.device)
            self.model.load_state_dict(state['model_state_dict'])

