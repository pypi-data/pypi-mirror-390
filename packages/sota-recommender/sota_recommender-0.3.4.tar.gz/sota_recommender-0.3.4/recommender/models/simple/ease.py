"""
EASE: Embarrassingly Shallow Autoencoders for Sparse Data

Reference:
Harald Steck. 2019. Embarrassingly Shallow Autoencoders for Sparse Data.
In WWW '19. ACM, 3251–3257.

EASE is a linear model with a closed-form solution that achieves surprisingly
good performance on implicit feedback datasets.
"""
import numpy as np
from scipy import sparse
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from ...core.base import ImplicitRecommender


class EASERecommender(ImplicitRecommender):
    """
    EASE (Embarrassingly Shallow Autoencoders) Recommender.
    
    EASE learns a linear item-item similarity matrix with a closed-form solution.
    It's extremely simple yet highly effective for implicit feedback.
    
    Key features:
    - Closed-form solution (no iterative training)
    - Very fast training and inference
    - State-of-the-art results on many benchmarks
    - Works well with sparse data
    """
    
    def __init__(self, l2_reg: float = 500.0):
        """
        Initialize EASE recommender.
        
        Args:
            l2_reg: L2 regularization strength (lambda parameter)
        """
        super().__init__()
        self.l2_reg = l2_reg
        self.item_sim_matrix = None  # Item-item similarity matrix
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'EASERecommender':
        """
        Train EASE model.
        
        The closed-form solution:
        B = (X^T X + λI)^{-1} - (1/λ)I
        where X is the user-item interaction matrix.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id']
            
        Returns:
            self
        """
        print("Training EASE model...")
        
        # Create mappings
        self._create_mappings(interactions)
        
        # Build interaction matrix
        self._build_seen_items(interactions)
        
        # Convert to user-item matrix (binary)
        X = self._build_interaction_matrix(interactions)
        
        # Compute Gram matrix: G = X^T X
        print("Computing Gram matrix...")
        G = X.T @ X
        
        # Add L2 regularization: G + λI
        diag_indices = np.diag_indices(G.shape[0])
        G[diag_indices] += self.l2_reg
        
        # Inverse: P = (G + λI)^{-1}
        print("Computing matrix inverse...")
        P = np.linalg.inv(G)
        
        # Item-item similarity: B = P - diag(P)
        # Set diagonal to zero (item doesn't predict itself)
        self.item_sim_matrix = P / (-np.diag(P))
        self.item_sim_matrix[diag_indices] = 0.0
        
        self.is_fitted = True
        print("EASE training complete!")
        
        return self
    
    def _build_interaction_matrix(self, interactions: pd.DataFrame) -> np.ndarray:
        """Build binary user-item interaction matrix."""
        # Map to internal indices
        user_indices = interactions['user_id'].map(self.user_mapping).values
        item_indices = interactions['item_id'].map(self.item_mapping).values
        
        # Create sparse matrix
        data = np.ones(len(interactions))
        X_sparse = sparse.csr_matrix(
            (data, (user_indices, item_indices)),
            shape=(self.n_users, self.n_items)
        )
        
        # Convert to dense for matrix operations
        # Note: For very large datasets, consider keeping sparse and using sparse operations
        X = X_sparse.toarray()
        
        return X
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """
        Predict scores for user-item pairs.
        
        Args:
            user_ids: Array of user IDs
            item_ids: Array of item IDs
            
        Returns:
            Predicted scores
        """
        self._check_fitted()
        
        predictions = []
        for user_id, item_id in zip(user_ids, item_ids):
            # Map to internal indices
            if user_id not in self.user_mapping or item_id not in self.item_mapping:
                predictions.append(0.0)
                continue
            
            user_idx = self.user_mapping[user_id]
            item_idx = self.item_mapping[item_id]
            
            # Get user's interaction vector
            user_items = self.seen_items.get(user_idx, set())
            
            # Score = sum of similarities to items user has interacted with
            score = 0.0
            for interacted_item_idx in user_items:
                score += self.item_sim_matrix[item_idx, interacted_item_idx]
            
            predictions.append(score)
        
        return np.array(predictions)
    
    def recommend(
        self,
        user_ids: np.ndarray,
        k: int = 10,
        exclude_seen: bool = True,
        **kwargs
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """
        Generate top-K recommendations for users.
        
        Args:
            user_ids: Array of user IDs
            k: Number of recommendations per user
            exclude_seen: Whether to exclude seen items
            
        Returns:
            Dict mapping user_id to list of (item_id, score) tuples
        """
        self._check_fitted()
        
        recommendations = {}
        
        for user_id in user_ids:
            if user_id not in self.user_mapping:
                recommendations[user_id] = []
                continue
            
            user_idx = self.user_mapping[user_id]
            
            # Get user's interaction vector
            user_items = self.seen_items.get(user_idx, set())
            
            if not user_items:
                recommendations[user_id] = []
                continue
            
            # Compute scores: X_user @ B^T
            # Score for each item = sum of similarities to interacted items
            scores = np.zeros(self.n_items)
            for item_idx in user_items:
                scores += self.item_sim_matrix[:, item_idx]
            
            # Exclude seen items if requested
            if exclude_seen:
                for item_idx in user_items:
                    scores[item_idx] = -np.inf
            
            # Get top-k items
            top_indices = np.argsort(scores)[-k:][::-1]
            
            # Convert to original item IDs
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
            'item_sim_matrix': self.item_sim_matrix,
            'seen_items': self.seen_items,
            'l2_reg': self.l2_reg
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.item_sim_matrix = state['item_sim_matrix']
        self.seen_items = state['seen_items']
        self.l2_reg = state['l2_reg']
    
    def get_similar_items(self, item_id: Any, k: int = 10) -> List[Tuple[Any, float]]:
        """
        Get most similar items to a given item.
        
        Args:
            item_id: Item ID
            k: Number of similar items to return
            
        Returns:
            List of (item_id, similarity) tuples
        """
        self._check_fitted()
        
        if item_id not in self.item_mapping:
            return []
        
        item_idx = self.item_mapping[item_id]
        
        # Get similarity scores
        similarities = self.item_sim_matrix[:, item_idx]
        
        # Get top-k (excluding the item itself)
        top_indices = np.argsort(similarities)[-k-1:][::-1]
        
        similar_items = []
        for idx in top_indices:
            if idx != item_idx:
                similar_item_id = self.reverse_item_mapping[idx]
                sim_score = similarities[idx]
                similar_items.append((similar_item_id, float(sim_score)))
        
        return similar_items[:k]

