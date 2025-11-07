"""
SVD++ for Implicit Feedback

Reference:
Yehuda Koren. 2008. Factorization meets the neighborhood: a multifaceted 
collaborative filtering model. In KDD '08.

SVD++ extends SVD by incorporating implicit feedback.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from ...core.base import ExplicitRecommender


class SVDPlusPlusRecommender(ExplicitRecommender):
    """
    SVD++ Recommender with Implicit Feedback.
    
    Extends basic SVD by modeling:
    - User latent factors
    - Item latent factors
    - User biases
    - Item biases
    - Implicit feedback from user's interaction history
    
    Prediction: r̂_ui = μ + b_u + b_i + q_i^T (p_u + |N(u)|^{-1/2} Σ_{j∈N(u)} y_j)
    """
    
    def __init__(
        self,
        n_factors: int = 20,
        n_epochs: int = 20,
        lr: float = 0.005,
        reg: float = 0.02,
        random_state: int = 42
    ):
        """
        Initialize SVD++ model.
        
        Args:
            n_factors: Number of latent factors
            n_epochs: Number of training epochs
            lr: Learning rate
            reg: Regularization strength
            random_state: Random seed
        """
        super().__init__()
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg
        self.random_state = random_state
        
        # Model parameters
        self.user_factors = None  # p_u
        self.item_factors = None  # q_i
        self.item_implicit_factors = None  # y_j (for implicit feedback)
        self.user_biases = None  # b_u
        self.item_biases = None  # b_i
        self.user_item_matrix = None
        
        np.random.seed(random_state)
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'SVDPlusPlusRecommender':
        """
        Train SVD++ model using SGD.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'rating']
            
        Returns:
            self
        """
        print("Training SVD++ model...")
        
        # Create mappings
        self._create_mappings(interactions)
        self._compute_global_mean(interactions)
        
        # Build user-item matrix
        self.user_item_matrix = self._build_user_item_matrix(interactions)
        
        # Build implicit feedback sets (items rated by each user)
        self.user_implicit_items = {}
        for user_id, group in interactions.groupby('user_id'):
            user_idx = self.user_mapping[user_id]
            item_indices = [self.item_mapping[iid] for iid in group['item_id'].values]
            self.user_implicit_items[user_idx] = set(item_indices)
        
        # Initialize parameters
        self._initialize_parameters()
        
        # Prepare training data
        train_data = []
        for _, row in interactions.iterrows():
            user_idx = self.user_mapping[row['user_id']]
            item_idx = self.item_mapping[row['item_id']]
            rating = row['rating']
            train_data.append((user_idx, item_idx, rating))
        
        # SGD training
        print(f"Training for {self.n_epochs} epochs...")
        for epoch in range(self.n_epochs):
            np.random.shuffle(train_data)
            
            total_loss = 0.0
            for user_idx, item_idx, rating in train_data:
                # Prediction
                pred = self._predict_pair(user_idx, item_idx)
                
                # Error
                error = rating - pred
                total_loss += error ** 2
                
                # Get implicit feedback sum
                implicit_items = self.user_implicit_items.get(user_idx, set())
                sqrt_n = np.sqrt(len(implicit_items)) if implicit_items else 1.0
                
                implicit_sum = np.zeros(self.n_factors)
                for j in implicit_items:
                    implicit_sum += self.item_implicit_factors[j]
                implicit_sum /= sqrt_n
                
                # Update parameters
                # User bias
                self.user_biases[user_idx] += self.lr * (error - self.reg * self.user_biases[user_idx])
                
                # Item bias
                self.item_biases[item_idx] += self.lr * (error - self.reg * self.item_biases[item_idx])
                
                # User factors
                user_factors_old = self.user_factors[user_idx].copy()
                self.user_factors[user_idx] += self.lr * (
                    error * self.item_factors[item_idx] - 
                    self.reg * self.user_factors[user_idx]
                )
                
                # Item factors
                self.item_factors[item_idx] += self.lr * (
                    error * (user_factors_old + implicit_sum) - 
                    self.reg * self.item_factors[item_idx]
                )
                
                # Implicit factors
                for j in implicit_items:
                    self.item_implicit_factors[j] += self.lr * (
                        error * self.item_factors[item_idx] / sqrt_n - 
                        self.reg * self.item_implicit_factors[j]
                    )
            
            rmse = np.sqrt(total_loss / len(train_data))
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"  Epoch {epoch + 1}/{self.n_epochs}, RMSE: {rmse:.4f}")
        
        self.is_fitted = True
        print("SVD++ training complete!")
        
        return self
    
    def _initialize_parameters(self):
        """Initialize model parameters."""
        # Initialize with small random values
        scale = 0.1
        self.user_factors = np.random.normal(0, scale, (self.n_users, self.n_factors))
        self.item_factors = np.random.normal(0, scale, (self.n_items, self.n_factors))
        self.item_implicit_factors = np.random.normal(0, scale, (self.n_items, self.n_factors))
        
        self.user_biases = np.zeros(self.n_users)
        self.item_biases = np.zeros(self.n_items)
    
    def _build_user_item_matrix(self, interactions: pd.DataFrame) -> np.ndarray:
        """Build user-item rating matrix."""
        pivot = interactions.pivot_table(
            index='user_id',
            columns='item_id',
            values='rating',
            fill_value=0
        )
        
        all_users = [self.reverse_user_mapping[i] for i in range(self.n_users)]
        all_items = [self.reverse_item_mapping[i] for i in range(self.n_items)]
        
        pivot = pivot.reindex(index=all_users, columns=all_items, fill_value=0)
        
        return pivot.values
    
    def _predict_pair(self, user_idx: int, item_idx: int) -> float:
        """Predict rating for a single user-item pair."""
        # Base prediction
        pred = self.global_mean + self.user_biases[user_idx] + self.item_biases[item_idx]
        
        # Get implicit feedback
        implicit_items = self.user_implicit_items.get(user_idx, set())
        sqrt_n = np.sqrt(len(implicit_items)) if implicit_items else 1.0
        
        implicit_sum = np.zeros(self.n_factors)
        for j in implicit_items:
            implicit_sum += self.item_implicit_factors[j]
        implicit_sum /= sqrt_n
        
        # Add factor interaction
        pred += np.dot(self.item_factors[item_idx], self.user_factors[user_idx] + implicit_sum)
        
        return pred
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict ratings for user-item pairs."""
        self._check_fitted()
        
        predictions = []
        for user_id, item_id in zip(user_ids, item_ids):
            if user_id not in self.user_mapping or item_id not in self.item_mapping:
                predictions.append(self.global_mean)
                continue
            
            user_idx = self.user_mapping[user_id]
            item_idx = self.item_mapping[item_id]
            
            pred = self._predict_pair(user_idx, item_idx)
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
            scores = np.zeros(self.n_items)
            for item_idx in range(self.n_items):
                scores[item_idx] = self._predict_pair(user_idx, item_idx)
            
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
            'item_implicit_factors': self.item_implicit_factors,
            'user_biases': self.user_biases,
            'item_biases': self.item_biases,
            'user_implicit_items': self.user_implicit_items,
            'user_item_matrix': self.user_item_matrix,
            'global_mean': self.global_mean
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.user_factors = state['user_factors']
        self.item_factors = state['item_factors']
        self.item_implicit_factors = state['item_implicit_factors']
        self.user_biases = state['user_biases']
        self.item_biases = state['item_biases']
        self.user_implicit_items = state['user_implicit_items']
        self.user_item_matrix = state['user_item_matrix']
        self.global_mean = state['global_mean']

