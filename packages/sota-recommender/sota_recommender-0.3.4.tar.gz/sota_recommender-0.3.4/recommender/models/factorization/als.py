"""
ALS: Alternating Least Squares for Implicit Feedback

Reference:
Yifan Hu, Yehuda Koren, and Chris Volinsky. 2008. Collaborative Filtering 
for Implicit Feedback Datasets. In ICDM '08.

ALS is particularly well-suited for implicit feedback datasets.
"""
import numpy as np
from scipy import sparse
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from ...core.base import ImplicitRecommender


class ALSRecommender(ImplicitRecommender):
    """
    Alternating Least Squares for Implicit Feedback.
    
    Optimizes user and item factors alternately, treating implicit feedback
    with confidence weighting.
    
    Key features:
    - Efficient for large-scale implicit feedback
    - Parallelizable
    - No hyperparameter tuning needed for learning rate
    """
    
    def __init__(
        self,
        n_factors: int = 20,
        n_iterations: int = 15,
        reg: float = 0.01,
        alpha: float = 40.0,
        random_state: int = 42
    ):
        """
        Initialize ALS model.
        
        Args:
            n_factors: Number of latent factors
            n_iterations: Number of alternating iterations
            reg: Regularization strength (lambda)
            alpha: Confidence scaling parameter
            random_state: Random seed
        """
        super().__init__()
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.reg = reg
        self.alpha = alpha
        self.random_state = random_state
        
        self.user_factors = None
        self.item_factors = None
        self.interaction_matrix = None
        
        np.random.seed(random_state)
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'ALSRecommender':
        """
        Train ALS model.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id']
                         Optional 'rating' column for interaction strength
            
        Returns:
            self
        """
        print("Training ALS model...")
        
        # Create mappings
        self._create_mappings(interactions)
        self._build_seen_items(interactions)
        
        # Build interaction matrix
        self.interaction_matrix = self._build_interaction_matrix(interactions)
        
        # Compute confidence matrix: C = 1 + alpha * R
        # where R is the interaction matrix
        self.confidence_matrix = 1 + self.alpha * self.interaction_matrix
        
        # Preference matrix: P (binary - did user interact with item?)
        self.preference_matrix = (self.interaction_matrix > 0).astype(np.float32)
        
        # Initialize factors
        self.user_factors = np.random.normal(0, 0.01, (self.n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.01, (self.n_items, self.n_factors))
        
        # Alternating optimization
        print(f"Running {self.n_iterations} ALS iterations...")
        for iteration in range(self.n_iterations):
            # Fix items, solve for users
            self.user_factors = self._solve_factors(
                self.item_factors,
                self.preference_matrix,
                self.confidence_matrix
            )
            
            # Fix users, solve for items
            self.item_factors = self._solve_factors(
                self.user_factors,
                self.preference_matrix.T,
                self.confidence_matrix.T
            )
            
            if (iteration + 1) % 5 == 0:
                loss = self._compute_loss()
                print(f"  Iteration {iteration + 1}/{self.n_iterations}, Loss: {loss:.4f}")
        
        self.is_fitted = True
        print("ALS training complete!")
        
        return self
    
    def _build_interaction_matrix(self, interactions: pd.DataFrame) -> np.ndarray:
        """Build interaction matrix."""
        user_indices = interactions['user_id'].map(self.user_mapping).values
        item_indices = interactions['item_id'].map(self.item_mapping).values
        
        # Use rating if available, otherwise use 1
        if 'rating' in interactions.columns:
            values = interactions['rating'].values
        else:
            values = np.ones(len(interactions))
        
        # Create sparse matrix
        interaction_sparse = sparse.csr_matrix(
            (values, (user_indices, item_indices)),
            shape=(self.n_users, self.n_items)
        )
        
        # Convert to dense for ALS
        # Note: For very large datasets, use sparse ALS implementation
        return interaction_sparse.toarray()
    
    def _solve_factors(
        self,
        fixed_factors: np.ndarray,
        preference: np.ndarray,
        confidence: np.ndarray
    ) -> np.ndarray:
        """
        Solve for factors given fixed factors.
        
        For each user u (or item i), solve:
        x_u = (Y^T C^u Y + λI)^{-1} Y^T C^u p^u
        
        where:
        - Y is the fixed factor matrix
        - C^u is diagonal confidence matrix for user u
        - p^u is preference vector for user u
        - λ is regularization
        """
        n_entities = preference.shape[0]
        n_factors = fixed_factors.shape[1]
        
        new_factors = np.zeros((n_entities, n_factors))
        
        # Precompute Y^T Y (same for all entities)
        YtY = fixed_factors.T @ fixed_factors
        
        for u in range(n_entities):
            # Get confidence and preference for this entity
            Cu = confidence[u]
            pu = preference[u]
            
            # Compute Y^T C^u Y
            # C^u is diagonal, so C^u Y is just element-wise multiplication
            YtCuY = YtY.copy()
            for i in range(self.n_items):
                if Cu[i] > 1:  # Only update for non-zero confidence
                    yi = fixed_factors[i]
                    YtCuY += (Cu[i] - 1) * np.outer(yi, yi)
            
            # Add regularization
            YtCuY += self.reg * np.eye(n_factors)
            
            # Compute Y^T C^u p^u
            YtCupu = fixed_factors.T @ (Cu * pu)
            
            # Solve linear system
            new_factors[u] = np.linalg.solve(YtCuY, YtCupu)
        
        return new_factors
    
    def _compute_loss(self) -> float:
        """Compute training loss."""
        # Reconstruction loss
        pred = self.user_factors @ self.item_factors.T
        diff = self.preference_matrix - pred
        weighted_diff = self.confidence_matrix * (diff ** 2)
        loss = weighted_diff.sum()
        
        # Regularization
        loss += self.reg * (np.sum(self.user_factors ** 2) + np.sum(self.item_factors ** 2))
        
        return loss
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict scores for user-item pairs."""
        self._check_fitted()
        
        predictions = []
        for user_id, item_id in zip(user_ids, item_ids):
            if user_id not in self.user_mapping or item_id not in self.item_mapping:
                predictions.append(0.0)
                continue
            
            user_idx = self.user_mapping[user_id]
            item_idx = self.item_mapping[item_id]
            
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
        """Generate top-K recommendations."""
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
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'interaction_matrix': self.interaction_matrix,
            'seen_items': self.seen_items
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.user_factors = state['user_factors']
        self.item_factors = state['item_factors']
        self.interaction_matrix = state['interaction_matrix']
        self.seen_items = state['seen_items']
    
    def get_similar_items(self, item_id: Any, k: int = 10) -> List[Tuple[Any, float]]:
        """Get similar items based on item factors."""
        self._check_fitted()
        
        if item_id not in self.item_mapping:
            return []
        
        item_idx = self.item_mapping[item_id]
        item_vec = self.item_factors[item_idx]
        
        # Compute cosine similarity
        norms = np.linalg.norm(self.item_factors, axis=1)
        similarities = (self.item_factors @ item_vec) / (norms * np.linalg.norm(item_vec) + 1e-8)
        
        # Get top-k
        top_indices = np.argsort(similarities)[-k-1:][::-1]
        
        similar_items = []
        for idx in top_indices:
            if idx != item_idx:
                similar_item_id = self.reverse_item_mapping[idx]
                sim_score = similarities[idx]
                similar_items.append((similar_item_id, float(sim_score)))
        
        return similar_items[:k]

