"""
Data handling utilities for recommender systems.
"""
from typing import Optional, Tuple, List, Dict
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.model_selection import train_test_split
import warnings


class InteractionDataset:
    """
    Dataset class for user-item interactions.
    
    Supports both implicit (binary) and explicit (rating) feedback.
    """
    
    def __init__(
        self,
        interactions: pd.DataFrame,
        implicit: bool = False,
        min_user_interactions: int = 0,
        min_item_interactions: int = 0
    ):
        """
        Initialize the dataset.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'rating'] (optional)
            implicit: Whether this is implicit feedback (binary)
            min_user_interactions: Minimum number of interactions per user
            min_item_interactions: Minimum number of interactions per item
        """
        self.implicit = implicit
        
        # Validate columns
        required_cols = ['user_id', 'item_id']
        if not implicit and 'rating' not in interactions.columns:
            raise ValueError("Explicit feedback requires 'rating' column")
        
        for col in required_cols:
            if col not in interactions.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Filter by minimum interactions
        self.data = self._filter_interactions(
            interactions.copy(),
            min_user_interactions,
            min_item_interactions
        )
        
        # Create mappings
        self.user_ids = self.data['user_id'].unique()
        self.item_ids = self.data['item_id'].unique()
        
        self.user_to_idx = {uid: idx for idx, uid in enumerate(self.user_ids)}
        self.item_to_idx = {iid: idx for idx, iid in enumerate(self.item_ids)}
        
        self.idx_to_user = {idx: uid for uid, idx in self.user_to_idx.items()}
        self.idx_to_item = {idx: iid for iid, idx in self.item_to_idx.items()}
        
        self.n_users = len(self.user_ids)
        self.n_items = len(self.item_ids)
        
        # Add internal indices to dataframe
        self.data['user_idx'] = self.data['user_id'].map(self.user_to_idx)
        self.data['item_idx'] = self.data['item_id'].map(self.item_to_idx)
        
        if self.implicit and 'rating' not in self.data.columns:
            self.data['rating'] = 1.0
    
    def _filter_interactions(
        self,
        df: pd.DataFrame,
        min_user: int,
        min_item: int
    ) -> pd.DataFrame:
        """
        Filter out users/items with too few interactions.
        
        Args:
            df: Interactions DataFrame
            min_user: Minimum interactions per user
            min_item: Minimum interactions per item
            
        Returns:
            Filtered DataFrame
        """
        if min_user <= 0 and min_item <= 0:
            return df
        
        # Iteratively filter until convergence
        prev_size = -1
        while len(df) != prev_size:
            prev_size = len(df)
            
            if min_user > 0:
                user_counts = df['user_id'].value_counts()
                valid_users = user_counts[user_counts >= min_user].index
                df = df[df['user_id'].isin(valid_users)]
            
            if min_item > 0:
                item_counts = df['item_id'].value_counts()
                valid_items = item_counts[item_counts >= min_item].index
                df = df[df['item_id'].isin(valid_items)]
        
        return df
    
    def to_csr_matrix(self) -> sparse.csr_matrix:
        """
        Convert interactions to sparse CSR matrix.
        
        Returns:
            Sparse user-item interaction matrix (n_users x n_items)
        """
        values = self.data['rating'].values if 'rating' in self.data.columns else np.ones(len(self.data))
        
        matrix = sparse.csr_matrix(
            (values, (self.data['user_idx'], self.data['item_idx'])),
            shape=(self.n_users, self.n_items)
        )
        
        return matrix
    
    def to_dense_matrix(self) -> np.ndarray:
        """
        Convert interactions to dense matrix.
        Warning: Can be memory-intensive for large datasets.
        
        Returns:
            Dense user-item interaction matrix (n_users x n_items)
        """
        return self.to_csr_matrix().toarray()
    
    def get_user_items(self, user_id) -> List[int]:
        """
        Get all items interacted with by a user.
        
        Args:
            user_id: Original user ID
            
        Returns:
            List of item indices
        """
        if user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        user_data = self.data[self.data['user_idx'] == user_idx]
        return user_data['item_idx'].tolist()
    
    def get_item_users(self, item_id) -> List[int]:
        """
        Get all users who interacted with an item.
        
        Args:
            item_id: Original item ID
            
        Returns:
            List of user indices
        """
        if item_id not in self.item_to_idx:
            return []
        
        item_idx = self.item_to_idx[item_id]
        item_data = self.data[self.data['item_idx'] == item_idx]
        return item_data['user_idx'].tolist()
    
    def split(
        self,
        test_size: float = 0.2,
        val_size: Optional[float] = None,
        random_state: int = 42,
        strategy: str = 'random'
    ) -> Tuple['InteractionDataset', ...]:
        """
        Split dataset into train/val/test sets.
        
        Args:
            test_size: Proportion of test set
            val_size: Proportion of validation set (optional)
            random_state: Random seed
            strategy: Split strategy ('random', 'temporal', 'leave_one_out')
            
        Returns:
            Tuple of (train, test) or (train, val, test) datasets
        """
        if strategy == 'random':
            return self._random_split(test_size, val_size, random_state)
        elif strategy == 'temporal':
            return self._temporal_split(test_size, val_size)
        elif strategy == 'leave_one_out':
            return self._leave_one_out_split(val_size)
        else:
            raise ValueError(f"Unknown split strategy: {strategy}")
    
    def _random_split(
        self,
        test_size: float,
        val_size: Optional[float],
        random_state: int
    ) -> Tuple['InteractionDataset', ...]:
        """Random split of interactions."""
        if val_size is None:
            train_df, test_df = train_test_split(
                self.data,
                test_size=test_size,
                random_state=random_state
            )
            
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, test_ds
        else:
            train_df, temp_df = train_test_split(
                self.data,
                test_size=(test_size + val_size),
                random_state=random_state
            )
            
            val_df, test_df = train_test_split(
                temp_df,
                test_size=test_size / (test_size + val_size),
                random_state=random_state
            )
            
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            val_ds = InteractionDataset.__new__(InteractionDataset)
            val_ds.__dict__.update(self.__dict__)
            val_ds.data = val_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, val_ds, test_ds
    
    def _temporal_split(
        self,
        test_size: float,
        val_size: Optional[float]
    ) -> Tuple['InteractionDataset', ...]:
        """Temporal split based on timestamp."""
        if 'timestamp' not in self.data.columns:
            warnings.warn("No 'timestamp' column found, falling back to random split")
            return self._random_split(test_size, val_size, 42)
        
        sorted_data = self.data.sort_values('timestamp')
        
        n = len(sorted_data)
        test_start = int(n * (1 - test_size))
        
        if val_size is None:
            train_df = sorted_data.iloc[:test_start]
            test_df = sorted_data.iloc[test_start:]
            
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, test_ds
        else:
            val_start = int(n * (1 - test_size - val_size))
            
            train_df = sorted_data.iloc[:val_start]
            val_df = sorted_data.iloc[val_start:test_start]
            test_df = sorted_data.iloc[test_start:]
            
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            val_ds = InteractionDataset.__new__(InteractionDataset)
            val_ds.__dict__.update(self.__dict__)
            val_ds.data = val_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, val_ds, test_ds
    
    def _leave_one_out_split(
        self,
        val_size: Optional[float]
    ) -> Tuple['InteractionDataset', ...]:
        """
        Leave-one-out split: last interaction per user for test.
        Used commonly for sequential/session-based recommendations.
        """
        if 'timestamp' in self.data.columns:
            sorted_data = self.data.sort_values(['user_id', 'timestamp'])
        else:
            sorted_data = self.data
        
        # Last item per user goes to test
        test_df = sorted_data.groupby('user_id').tail(1)
        train_df = sorted_data.drop(test_df.index)
        
        if val_size is None:
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, test_ds
        else:
            # Second-to-last item per user goes to validation
            val_df = train_df.groupby('user_id').tail(1)
            train_df = train_df.drop(val_df.index)
            
            train_ds = InteractionDataset.__new__(InteractionDataset)
            train_ds.__dict__.update(self.__dict__)
            train_ds.data = train_df
            
            val_ds = InteractionDataset.__new__(InteractionDataset)
            val_ds.__dict__.update(self.__dict__)
            val_ds.data = val_df
            
            test_ds = InteractionDataset.__new__(InteractionDataset)
            test_ds.__dict__.update(self.__dict__)
            test_ds.data = test_df
            
            return train_ds, val_ds, test_ds
    
    def __len__(self) -> int:
        """Return number of interactions."""
        return len(self.data)
    
    def __repr__(self) -> str:
        """String representation."""
        feedback_type = "implicit" if self.implicit else "explicit"
        return (
            f"InteractionDataset({feedback_type}, "
            f"n_users={self.n_users}, n_items={self.n_items}, "
            f"n_interactions={len(self.data)})"
        )

