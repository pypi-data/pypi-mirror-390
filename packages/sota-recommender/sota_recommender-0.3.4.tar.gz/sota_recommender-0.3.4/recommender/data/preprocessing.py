"""
Data preprocessing utilities.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional, List
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def filter_by_interaction_count(
    df: pd.DataFrame,
    min_user_interactions: int = 5,
    min_item_interactions: int = 5,
    max_iterations: int = 10
) -> pd.DataFrame:
    """
    Filter users and items by minimum interaction count.
    
    Iteratively removes users/items until convergence or max iterations.
    
    Args:
        df: DataFrame with 'user_id' and 'item_id' columns
        min_user_interactions: Minimum interactions per user
        min_item_interactions: Minimum interactions per item
        max_iterations: Maximum number of filtering iterations
        
    Returns:
        Filtered DataFrame
    """
    df_filtered = df.copy()
    
    for iteration in range(max_iterations):
        prev_len = len(df_filtered)
        
        # Filter users
        if min_user_interactions > 0:
            user_counts = df_filtered['user_id'].value_counts()
            valid_users = user_counts[user_counts >= min_user_interactions].index
            df_filtered = df_filtered[df_filtered['user_id'].isin(valid_users)]
        
        # Filter items
        if min_item_interactions > 0:
            item_counts = df_filtered['item_id'].value_counts()
            valid_items = item_counts[item_counts >= min_item_interactions].index
            df_filtered = df_filtered[df_filtered['item_id'].isin(valid_items)]
        
        # Check convergence
        if len(df_filtered) == prev_len:
            break
    
    print(f"Filtered from {len(df)} to {len(df_filtered)} interactions "
          f"({100 * len(df_filtered) / len(df):.1f}% retained)")
    
    return df_filtered


def normalize_ratings(
    df: pd.DataFrame,
    method: str = 'minmax',
    rating_col: str = 'rating'
) -> pd.DataFrame:
    """
    Normalize rating values.
    
    Args:
        df: DataFrame with rating column
        method: Normalization method ('minmax', 'standard', 'none')
        rating_col: Name of rating column
        
    Returns:
        DataFrame with normalized ratings
    """
    df_norm = df.copy()
    
    if method == 'none':
        return df_norm
    elif method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'standard':
        scaler = StandardScaler()
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    if rating_col in df_norm.columns:
        df_norm[rating_col] = scaler.fit_transform(df_norm[[rating_col]])
    
    return df_norm


def binarize_implicit_feedback(
    df: pd.DataFrame,
    threshold: Optional[float] = None,
    rating_col: str = 'rating'
) -> pd.DataFrame:
    """
    Convert explicit ratings to binary implicit feedback.
    
    Args:
        df: DataFrame with rating column
        threshold: Rating threshold for positive feedback. If None, all ratings are positive.
        rating_col: Name of rating column
        
    Returns:
        DataFrame with binary feedback (1 for positive, 0 removed)
    """
    df_binary = df.copy()
    
    if threshold is not None and rating_col in df_binary.columns:
        df_binary = df_binary[df_binary[rating_col] >= threshold]
    
    if rating_col in df_binary.columns:
        df_binary[rating_col] = 1
    else:
        df_binary[rating_col] = 1
    
    return df_binary


def temporal_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    val_size: Optional[float] = None,
    timestamp_col: str = 'timestamp'
) -> Tuple[pd.DataFrame, ...]:
    """
    Split data temporally based on timestamp.
    
    Args:
        df: DataFrame with timestamp column
        test_size: Proportion of test set
        val_size: Proportion of validation set (optional)
        timestamp_col: Name of timestamp column
        
    Returns:
        Tuple of (train, test) or (train, val, test) DataFrames
    """
    if timestamp_col not in df.columns:
        raise ValueError(f"DataFrame must have '{timestamp_col}' column")
    
    df_sorted = df.sort_values(timestamp_col)
    n = len(df_sorted)
    
    if val_size is None:
        split_idx = int(n * (1 - test_size))
        train = df_sorted.iloc[:split_idx]
        test = df_sorted.iloc[split_idx:]
        return train, test
    else:
        val_split_idx = int(n * (1 - test_size - val_size))
        test_split_idx = int(n * (1 - test_size))
        
        train = df_sorted.iloc[:val_split_idx]
        val = df_sorted.iloc[val_split_idx:test_split_idx]
        test = df_sorted.iloc[test_split_idx:]
        
        return train, val, test


def leave_n_out_split(
    df: pd.DataFrame,
    n: int = 1,
    user_col: str = 'user_id',
    timestamp_col: Optional[str] = 'timestamp'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Leave-N-out split: last N interactions per user for testing.
    
    Args:
        df: DataFrame with user interactions
        n: Number of interactions to leave out per user
        user_col: Name of user ID column
        timestamp_col: Name of timestamp column (optional, for ordering)
        
    Returns:
        Tuple of (train, test) DataFrames
    """
    if timestamp_col and timestamp_col in df.columns:
        df_sorted = df.sort_values([user_col, timestamp_col])
    else:
        df_sorted = df.copy()
    
    test_dfs = []
    train_dfs = []
    
    for user_id, user_df in df_sorted.groupby(user_col):
        if len(user_df) <= n:
            # Not enough interactions, put all in training
            train_dfs.append(user_df)
        else:
            train_dfs.append(user_df.iloc[:-n])
            test_dfs.append(user_df.iloc[-n:])
    
    train = pd.concat(train_dfs, ignore_index=True)
    test = pd.concat(test_dfs, ignore_index=True) if test_dfs else pd.DataFrame()
    
    return train, test


def create_sequences(
    df: pd.DataFrame,
    user_col: str = 'user_id',
    item_col: str = 'item_id',
    timestamp_col: Optional[str] = 'timestamp',
    max_seq_length: Optional[int] = None
) -> Tuple[List[List[int]], List[int]]:
    """
    Create sequential data for sequence-based models.
    
    Args:
        df: DataFrame with user-item interactions
        user_col: Name of user ID column
        item_col: Name of item ID column
        timestamp_col: Name of timestamp column (for ordering)
        max_seq_length: Maximum sequence length (older items truncated)
        
    Returns:
        Tuple of (sequences, target_items) where sequences[i] predicts target_items[i]
    """
    if timestamp_col and timestamp_col in df.columns:
        df_sorted = df.sort_values([user_col, timestamp_col])
    else:
        df_sorted = df.copy()
    
    sequences = []
    targets = []
    
    for user_id, user_df in df_sorted.groupby(user_col):
        items = user_df[item_col].tolist()
        
        # Create sequences: [1,2,3,4,5] -> [1,2,3,4] predicts 5, [1,2,3] predicts 4, etc.
        for i in range(1, len(items)):
            seq = items[:i]
            target = items[i]
            
            # Truncate if needed
            if max_seq_length and len(seq) > max_seq_length:
                seq = seq[-max_seq_length:]
            
            sequences.append(seq)
            targets.append(target)
    
    return sequences, targets


def remove_duplicates(
    df: pd.DataFrame,
    user_col: str = 'user_id',
    item_col: str = 'item_id',
    keep: str = 'last'
) -> pd.DataFrame:
    """
    Remove duplicate user-item interactions.
    
    Args:
        df: DataFrame with user-item interactions
        user_col: Name of user ID column
        item_col: Name of item ID column
        keep: Which duplicate to keep ('first', 'last', or False to remove all)
        
    Returns:
        DataFrame without duplicates
    """
    n_before = len(df)
    df_dedup = df.drop_duplicates(subset=[user_col, item_col], keep=keep)
    n_after = len(df_dedup)
    
    if n_before != n_after:
        print(f"Removed {n_before - n_after} duplicate interactions")
    
    return df_dedup


def add_time_features(
    df: pd.DataFrame,
    timestamp_col: str = 'timestamp',
    timestamp_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Extract time-based features from timestamp.
    
    Args:
        df: DataFrame with timestamp column
        timestamp_col: Name of timestamp column
        timestamp_format: Format of timestamp (if string)
        
    Returns:
        DataFrame with additional time features
    """
    df_time = df.copy()
    
    if timestamp_col not in df_time.columns:
        return df_time
    
    # Convert to datetime if needed
    if timestamp_format:
        df_time[timestamp_col] = pd.to_datetime(df_time[timestamp_col], format=timestamp_format)
    elif df_time[timestamp_col].dtype == 'int64':
        # Assume Unix timestamp
        df_time[timestamp_col] = pd.to_datetime(df_time[timestamp_col], unit='s')
    
    # Extract features
    df_time['hour'] = df_time[timestamp_col].dt.hour
    df_time['day_of_week'] = df_time[timestamp_col].dt.dayofweek
    df_time['day_of_month'] = df_time[timestamp_col].dt.day
    df_time['month'] = df_time[timestamp_col].dt.month
    df_time['year'] = df_time[timestamp_col].dt.year
    
    return df_time


def compute_item_popularity(
    df: pd.DataFrame,
    item_col: str = 'item_id'
) -> pd.Series:
    """
    Compute item popularity (interaction count).
    
    Args:
        df: DataFrame with item interactions
        item_col: Name of item ID column
        
    Returns:
        Series mapping item_id to popularity count
    """
    return df[item_col].value_counts()


def compute_user_activity(
    df: pd.DataFrame,
    user_col: str = 'user_id'
) -> pd.Series:
    """
    Compute user activity (interaction count).
    
    Args:
        df: DataFrame with user interactions
        user_col: Name of user ID column
        
    Returns:
        Series mapping user_id to activity count
    """
    return df[user_col].value_counts()

