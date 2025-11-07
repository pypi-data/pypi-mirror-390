"""
SLIM: Sparse Linear Methods for Top-N Recommender Systems

Reference:
Xia Ning and George Karypis. 2011. SLIM: Sparse Linear Methods for Top-N 
Recommender Systems. In ICDM '11. IEEE, 497–506.

SLIM learns a sparse item-item similarity matrix using L1/L2 regularization.
"""
import numpy as np
from scipy import sparse
from sklearn.linear_model import ElasticNet
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from ...core.base import ImplicitRecommender
import warnings


class SLIMRecommender(ImplicitRecommender):
    """
    SLIM (Sparse Linear Methods) Recommender.
    
    SLIM learns a sparse item-item similarity matrix by solving item-wise
    regression problems with L1/L2 regularization (Elastic Net).
    
    Key features:
    - Sparse similarity matrix (better generalization)
    - Item-based collaborative filtering
    - Competitive performance with neural methods
    - Interpretable model
    """
    
    def __init__(
        self,
        l1_reg: float = 0.1,
        l2_reg: float = 0.1,
        max_iter: int = 100,
        tol: float = 1e-4,
        positive_only: bool = True
    ):
        """
        Initialize SLIM recommender.
        
        Args:
            l1_reg: L1 regularization strength (alpha * l1_ratio in ElasticNet)
            l2_reg: L2 regularization strength (alpha * (1 - l1_ratio) in ElasticNet)
            max_iter: Maximum iterations for optimization
            tol: Tolerance for optimization convergence
            positive_only: Whether to enforce non-negative similarity weights
        """
        super().__init__()
        self.l1_reg = l1_reg
        self.l2_reg = l2_reg
        self.max_iter = max_iter
        self.tol = tol
        self.positive_only = positive_only
        self.item_sim_matrix = None
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'SLIMRecommender':
        """
        Train SLIM model.
        
        For each item j, solve:
        minimize ||X_j - X @ w_j||^2 + λ1 ||w_j||_1 + λ2 ||w_j||^2
        subject to: w_j[j] = 0, w_j >= 0 (optional)
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id']
            
        Returns:
            self
        """
        print("Training SLIM model...")
        
        # Create mappings
        self._create_mappings(interactions)
        
        # Build interaction matrix
        self._build_seen_items(interactions)
        
        # Convert to user-item matrix
        X = self._build_interaction_matrix(interactions)
        
        # Initialize similarity matrix
        self.item_sim_matrix = np.zeros((self.n_items, self.n_items))
        
        # Convert ElasticNet parameters
        # ElasticNet uses: alpha * (l1_ratio * L1 + (1 - l1_ratio) * L2)
        total_reg = self.l1_reg + self.l2_reg
        if total_reg > 0:
            l1_ratio = self.l1_reg / total_reg
            alpha = total_reg
        else:
            l1_ratio = 0.5
            alpha = 0.01
        
        # Train item-wise models
        print(f"Training {self.n_items} item models...")
        for j in range(self.n_items):
            if (j + 1) % 100 == 0:
                print(f"  Item {j + 1}/{self.n_items}")
            
            # Target: X[:, j] (ratings for item j)
            y = X[:, j].copy()
            
            # Features: X with column j removed (set to zero)
            X_train = X.copy()
            X_train[:, j] = 0
            
            # Train ElasticNet
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                model = ElasticNet(
                    alpha=alpha,
                    l1_ratio=l1_ratio,
                    fit_intercept=False,
                    max_iter=self.max_iter,
                    tol=self.tol,
                    positive=self.positive_only,
                    selection='random'
                )
                
                model.fit(X_train, y)
            
            # Store weights
            self.item_sim_matrix[:, j] = model.coef_
        
        # Ensure diagonal is zero
        np.fill_diagonal(self.item_sim_matrix, 0.0)
        
        self.is_fitted = True
        sparsity = 100 * np.sum(self.item_sim_matrix == 0) / (self.n_items ** 2)
        print(f"SLIM training complete! Similarity matrix sparsity: {sparsity:.1f}%")
        
        return self
    
    def _build_interaction_matrix(self, interactions: pd.DataFrame) -> np.ndarray:
        """Build binary user-item interaction matrix."""
        user_indices = interactions['user_id'].map(self.user_mapping).values
        item_indices = interactions['item_id'].map(self.item_mapping).values
        
        data = np.ones(len(interactions))
        X_sparse = sparse.csr_matrix(
            (data, (user_indices, item_indices)),
            shape=(self.n_users, self.n_items)
        )
        
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
            if user_id not in self.user_mapping or item_id not in self.item_mapping:
                predictions.append(0.0)
                continue
            
            user_idx = self.user_mapping[user_id]
            item_idx = self.item_mapping[item_id]
            
            # Get user's interactions
            user_items = self.seen_items.get(user_idx, set())
            
            # Score = sum of similarities to interacted items
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
            user_items = self.seen_items.get(user_idx, set())
            
            if not user_items:
                recommendations[user_id] = []
                continue
            
            # Compute scores
            scores = np.zeros(self.n_items)
            for item_idx in user_items:
                scores += self.item_sim_matrix[:, item_idx]
            
            # Exclude seen items
            if exclude_seen:
                for item_idx in user_items:
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
            'item_sim_matrix': self.item_sim_matrix,
            'seen_items': self.seen_items,
            'l1_reg': self.l1_reg,
            'l2_reg': self.l2_reg,
            'max_iter': self.max_iter,
            'tol': self.tol,
            'positive_only': self.positive_only
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.item_sim_matrix = state['item_sim_matrix']
        self.seen_items = state['seen_items']
        self.l1_reg = state['l1_reg']
        self.l2_reg = state['l2_reg']
        self.max_iter = state['max_iter']
        self.tol = state['tol']
        self.positive_only = state['positive_only']
    
    def get_similar_items(self, item_id: Any, k: int = 10) -> List[Tuple[Any, float]]:
        """
        Get most similar items.
        
        Args:
            item_id: Item ID
            k: Number of similar items
            
        Returns:
            List of (item_id, similarity) tuples
        """
        self._check_fitted()
        
        if item_id not in self.item_mapping:
            return []
        
        item_idx = self.item_mapping[item_id]
        similarities = self.item_sim_matrix[:, item_idx]
        
        top_indices = np.argsort(similarities)[-k-1:][::-1]
        
        similar_items = []
        for idx in top_indices:
            if idx != item_idx:
                similar_item_id = self.reverse_item_mapping[idx]
                sim_score = similarities[idx]
                similar_items.append((similar_item_id, float(sim_score)))
        
        return similar_items[:k]

