"""
SVD-based Collaborative Filtering using Truncated SVD.
"""
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD as SklearnTruncatedSVD
from typing import Dict, List, Set, Tuple, Any
from ...core.base import ExplicitRecommender


class SVDRecommender(ExplicitRecommender):
    """
    SVD-based Collaborative Filtering Recommender.
    
    Uses Truncated SVD (also known as LSA) to factorize the user-item matrix
    into lower-dimensional latent factors.
    
    Good for:
    - Explicit feedback (ratings)
    - Dense matrices
    - Fast training
    """
    
    def __init__(
        self,
        n_components: int = 20,
        n_iter: int = 10,
        random_state: int = 42
    ):
        """
        Initialize SVD recommender.
        
        Args:
            n_components: Number of latent factors
            n_iter: Number of iterations for randomized SVD
            random_state: Random seed
        """
        super().__init__()
        self.n_components = n_components
        self.n_iter = n_iter
        self.random_state = random_state
        
        self.svd = SklearnTruncatedSVD(
            n_components=n_components,
            n_iter=n_iter,
            random_state=random_state
        )
        
        self.user_factors = None
        self.item_factors = None
        self.user_item_matrix = None
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'SVDRecommender':
        """
        Train SVD model.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'rating']
            
        Returns:
            self
        """
        print("Training SVD model...")
        
        # Create mappings
        self._create_mappings(interactions)
        
        # Compute global mean
        self._compute_global_mean(interactions)
        
        # Build user-item matrix
        self.user_item_matrix = self._build_user_item_matrix(interactions)
        
        # Apply SVD
        print(f"Decomposing matrix with {self.n_components} components...")
        self.user_factors = self.svd.fit_transform(self.user_item_matrix)
        self.item_factors = self.svd.components_.T
        
        self.is_fitted = True
        
        explained_variance = self.svd.explained_variance_ratio_.sum()
        print(f"SVD training complete! Explained variance: {explained_variance:.2%}")
        
        return self
    
    def _build_user_item_matrix(self, interactions: pd.DataFrame) -> np.ndarray:
        """Build user-item rating matrix."""
        # Create pivot table
        pivot = interactions.pivot_table(
            index='user_id',
            columns='item_id',
            values='rating',
            fill_value=0
        )
        
        # Reindex to ensure all users/items are present
        all_users = [self.reverse_user_mapping[i] for i in range(self.n_users)]
        all_items = [self.reverse_item_mapping[i] for i in range(self.n_items)]
        
        pivot = pivot.reindex(index=all_users, columns=all_items, fill_value=0)
        
        return pivot.values
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """
        Predict ratings for user-item pairs.
        
        Args:
            user_ids: Array of user IDs
            item_ids: Array of item IDs
            
        Returns:
            Predicted ratings
        """
        self._check_fitted()
        
        predictions = []
        
        for user_id, item_id in zip(user_ids, item_ids):
            if user_id not in self.user_mapping or item_id not in self.item_mapping:
                predictions.append(self.global_mean)
                continue
            
            user_idx = self.user_mapping[user_id]
            item_idx = self.item_mapping[item_id]
            
            # Prediction: user_factors @ item_factors^T
            pred = np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
            
            predictions.append(pred)
        
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
            k: Number of recommendations
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
            
            # Compute scores for all items
            scores = self.user_factors[user_idx] @ self.item_factors.T
            
            # Exclude seen items
            if exclude_seen:
                seen_items = np.where(self.user_item_matrix[user_idx] > 0)[0]
                scores[seen_items] = -np.inf
            
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
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'user_item_matrix': self.user_item_matrix,
            'n_components': self.n_components,
            'n_iter': self.n_iter,
            'random_state': self.random_state,
            'global_mean': self.global_mean
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.user_factors = state['user_factors']
        self.item_factors = state['item_factors']
        self.user_item_matrix = state['user_item_matrix']
        self.n_components = state['n_components']
        self.n_iter = state['n_iter']
        self.random_state = state['random_state']
        self.global_mean = state['global_mean']

