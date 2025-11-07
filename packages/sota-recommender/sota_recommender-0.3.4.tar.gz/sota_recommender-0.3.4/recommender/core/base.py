"""
Base classes for all recommender models.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import pickle
import json
from pathlib import Path


class BaseRecommender(ABC):
    """
    Abstract base class for all recommender systems.
    
    All recommender models should inherit from this class and implement
    the abstract methods: fit(), predict(), and recommend().
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the recommender.
        
        Args:
            **kwargs: Model-specific hyperparameters
        """
        self.is_fitted = False
        self.user_mapping = {}  # Maps original user IDs to internal indices
        self.item_mapping = {}  # Maps original item IDs to internal indices
        self.reverse_user_mapping = {}
        self.reverse_item_mapping = {}
        self.n_users = 0
        self.n_items = 0
        self.config = kwargs
        
    @abstractmethod
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'BaseRecommender':
        """
        Train the recommender model on the provided interactions.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'rating'] (optional)
            **kwargs: Additional training parameters
            
        Returns:
            self: The fitted recommender
        """
        pass
    
    @abstractmethod
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """
        Predict ratings/scores for given user-item pairs.
        
        Args:
            user_ids: Array of user IDs
            item_ids: Array of item IDs
            
        Returns:
            predictions: Array of predicted scores
        """
        pass
    
    @abstractmethod
    def recommend(
        self, 
        user_ids: np.ndarray, 
        k: int = 10,
        exclude_seen: bool = True,
        **kwargs
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """
        Generate top-K recommendations for given users.
        
        Args:
            user_ids: Array of user IDs to generate recommendations for
            k: Number of recommendations per user
            exclude_seen: Whether to exclude items the user has already interacted with
            **kwargs: Additional parameters
            
        Returns:
            recommendations: Dict mapping user_id to list of (item_id, score) tuples
        """
        pass
    
    def _create_mappings(self, interactions: pd.DataFrame):
        """
        Create mappings from original IDs to internal indices.
        
        Args:
            interactions: DataFrame with 'user_id' and 'item_id' columns
        """
        unique_users = interactions['user_id'].unique()
        unique_items = interactions['item_id'].unique()
        
        self.user_mapping = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_mapping = {iid: idx for idx, iid in enumerate(unique_items)}
        
        self.reverse_user_mapping = {idx: uid for uid, idx in self.user_mapping.items()}
        self.reverse_item_mapping = {idx: iid for iid, idx in self.item_mapping.items()}
        
        self.n_users = len(unique_users)
        self.n_items = len(unique_items)
    
    def _check_fitted(self):
        """Check if the model has been fitted."""
        if not self.is_fitted:
            raise ValueError(
                "This model instance is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this method."
            )
    
    def save(self, path: str):
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'config': self.config,
            'user_mapping': self.user_mapping,
            'item_mapping': self.item_mapping,
            'reverse_user_mapping': self.reverse_user_mapping,
            'reverse_item_mapping': self.reverse_item_mapping,
            'n_users': self.n_users,
            'n_items': self.n_items,
            'is_fitted': self.is_fitted,
            'model_state': self._get_model_state()
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, path: str):
        """
        Load the model from disk.
        
        Args:
            path: Path to load the model from
        """
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.config = state['config']
        self.user_mapping = state['user_mapping']
        self.item_mapping = state['item_mapping']
        self.reverse_user_mapping = state['reverse_user_mapping']
        self.reverse_item_mapping = state['reverse_item_mapping']
        self.n_users = state['n_users']
        self.n_items = state['n_items']
        self.is_fitted = state['is_fitted']
        self._set_model_state(state['model_state'])
        
        return self
    
    def _get_model_state(self) -> Dict[str, Any]:
        """
        Get model-specific state for serialization.
        Override this method in subclasses to save model-specific attributes.
        
        Returns:
            state: Dictionary with model state
        """
        return {}
    
    def _set_model_state(self, state: Dict[str, Any]):
        """
        Set model-specific state after deserialization.
        Override this method in subclasses to load model-specific attributes.
        
        Args:
            state: Dictionary with model state
        """
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """Get model hyperparameters."""
        return self.config.copy()
    
    def set_params(self, **params):
        """Set model hyperparameters."""
        self.config.update(params)
        return self


class ImplicitRecommender(BaseRecommender):
    """
    Base class for implicit feedback recommenders.
    
    Implicit feedback: binary interactions (clicked, viewed, purchased)
    without explicit ratings.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seen_items = {}  # Maps user_idx to set of seen item_idx
    
    def _build_seen_items(self, interactions: pd.DataFrame):
        """Build dictionary of items seen by each user."""
        self.seen_items = {}
        for _, row in interactions.iterrows():
            user_idx = self.user_mapping[row['user_id']]
            item_idx = self.item_mapping[row['item_id']]
            
            if user_idx not in self.seen_items:
                self.seen_items[user_idx] = set()
            self.seen_items[user_idx].add(item_idx)


class ExplicitRecommender(BaseRecommender):
    """
    Base class for explicit feedback recommenders.
    
    Explicit feedback: numerical ratings (1-5 stars, thumbs up/down, etc.)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.global_mean = 0.0
    
    def _compute_global_mean(self, interactions: pd.DataFrame):
        """Compute global mean rating."""
        if 'rating' in interactions.columns:
            self.global_mean = interactions['rating'].mean()

