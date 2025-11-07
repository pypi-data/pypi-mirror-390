"""
Negative sampling strategies for implicit feedback.
"""
import numpy as np
from typing import Set, List, Dict, Optional
import random


class NegativeSampler:
    """
    Base class for negative samplers.
    """
    
    def __init__(
        self,
        n_items: int,
        seed: int = 42
    ):
        """
        Initialize sampler.
        
        Args:
            n_items: Total number of items
            seed: Random seed
        """
        self.n_items = n_items
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
    
    def sample(
        self,
        user_idx: int,
        positive_items: Set[int],
        n_negatives: int = 1
    ) -> List[int]:
        """
        Sample negative items for a user.
        
        Args:
            user_idx: User index
            positive_items: Set of positive item indices for this user
            n_negatives: Number of negative samples to generate
            
        Returns:
            List of negative item indices
        """
        raise NotImplementedError


class UniformSampler(NegativeSampler):
    """
    Uniform random negative sampling.
    
    Samples negative items uniformly at random from all items
    not in the user's positive set.
    """
    
    def sample(
        self,
        user_idx: int,
        positive_items: Set[int],
        n_negatives: int = 1
    ) -> List[int]:
        """Sample negatives uniformly at random."""
        negatives = []
        
        # Create candidate pool (all items except positives)
        candidates = list(set(range(self.n_items)) - positive_items)
        
        if len(candidates) < n_negatives:
            # Not enough candidates, sample with replacement
            negatives = np.random.choice(candidates, size=n_negatives, replace=True).tolist()
        else:
            # Sample without replacement
            negatives = np.random.choice(candidates, size=n_negatives, replace=False).tolist()
        
        return negatives


class PopularitySampler(NegativeSampler):
    """
    Popularity-based negative sampling.
    
    Samples negative items with probability proportional to their popularity.
    More popular items are more likely to be sampled.
    """
    
    def __init__(
        self,
        n_items: int,
        item_popularity: Dict[int, int],
        seed: int = 42
    ):
        """
        Initialize sampler.
        
        Args:
            n_items: Total number of items
            item_popularity: Dict mapping item_idx to popularity count
            seed: Random seed
        """
        super().__init__(n_items, seed)
        
        # Create probability distribution
        self.popularity = np.zeros(n_items)
        for item_idx, count in item_popularity.items():
            if item_idx < n_items:
                self.popularity[item_idx] = count
        
        # Normalize to probabilities
        total = self.popularity.sum()
        if total > 0:
            self.popularity = self.popularity / total
        else:
            # Fallback to uniform if no popularity info
            self.popularity = np.ones(n_items) / n_items
    
    def sample(
        self,
        user_idx: int,
        positive_items: Set[int],
        n_negatives: int = 1
    ) -> List[int]:
        """Sample negatives based on popularity."""
        # Create modified probability distribution (zero out positives)
        probs = self.popularity.copy()
        for item_idx in positive_items:
            if item_idx < len(probs):
                probs[item_idx] = 0.0
        
        # Renormalize
        total = probs.sum()
        if total > 0:
            probs = probs / total
        else:
            # Fallback to uniform over non-positive items
            candidates = list(set(range(self.n_items)) - positive_items)
            return np.random.choice(candidates, size=n_negatives, replace=True).tolist()
        
        negatives = np.random.choice(
            self.n_items,
            size=n_negatives,
            replace=True,
            p=probs
        ).tolist()
        
        return negatives


class InBatchSampler(NegativeSampler):
    """
    In-batch negative sampling.
    
    Uses other positive items in the batch as negatives.
    Efficient for batch training.
    """
    
    def sample_batch(
        self,
        user_indices: np.ndarray,
        positive_items: np.ndarray,
        user_positive_items: Dict[int, Set[int]]
    ) -> np.ndarray:
        """
        Sample negatives using in-batch sampling.
        
        Args:
            user_indices: Array of user indices in batch
            positive_items: Array of positive items for each user in batch
            user_positive_items: Dict mapping user_idx to their positive items
            
        Returns:
            Array of negative item indices (one per user)
        """
        batch_size = len(user_indices)
        negatives = np.zeros(batch_size, dtype=np.int32)
        
        # Get unique items in batch
        batch_items = set(positive_items)
        
        for i, user_idx in enumerate(user_indices):
            # Get user's positives
            user_positives = user_positive_items.get(user_idx, set())
            
            # Candidate negatives: batch items that user hasn't interacted with
            candidates = list(batch_items - user_positives)
            
            if candidates:
                negatives[i] = random.choice(candidates)
            else:
                # Fallback: sample from all items
                all_candidates = list(set(range(self.n_items)) - user_positives)
                negatives[i] = random.choice(all_candidates) if all_candidates else 0
        
        return negatives


class HardNegativeSampler(NegativeSampler):
    """
    Hard negative sampling.
    
    Samples negatives that the model currently ranks highly for the user
    (i.e., hard-to-distinguish negatives).
    """
    
    def __init__(
        self,
        n_items: int,
        seed: int = 42
    ):
        """Initialize sampler."""
        super().__init__(n_items, seed)
        self.item_scores = None  # Will be updated during training
    
    def update_scores(self, user_idx: int, scores: np.ndarray):
        """
        Update item scores for a user.
        
        Args:
            user_idx: User index
            scores: Score for each item
        """
        if self.item_scores is None:
            self.item_scores = {}
        self.item_scores[user_idx] = scores
    
    def sample(
        self,
        user_idx: int,
        positive_items: Set[int],
        n_negatives: int = 1,
        top_k: int = 100
    ) -> List[int]:
        """
        Sample hard negatives (high-scoring but not positive).
        
        Args:
            user_idx: User index
            positive_items: Set of positive items
            n_negatives: Number of negatives to sample
            top_k: Consider top-k scored items as hard negative candidates
            
        Returns:
            List of negative item indices
        """
        if self.item_scores is None or user_idx not in self.item_scores:
            # Fallback to uniform sampling
            candidates = list(set(range(self.n_items)) - positive_items)
            if len(candidates) < n_negatives:
                return np.random.choice(candidates, size=n_negatives, replace=True).tolist()
            else:
                return np.random.choice(candidates, size=n_negatives, replace=False).tolist()
        
        scores = self.item_scores[user_idx]
        
        # Get top-k items (excluding positives)
        mask = np.ones(len(scores), dtype=bool)
        for item_idx in positive_items:
            if item_idx < len(mask):
                mask[item_idx] = False
        
        masked_scores = scores.copy()
        masked_scores[~mask] = -np.inf
        
        # Get top-k indices
        top_indices = np.argsort(masked_scores)[-top_k:]
        
        # Sample from top-k
        if len(top_indices) < n_negatives:
            negatives = top_indices.tolist()
        else:
            negatives = np.random.choice(top_indices, size=n_negatives, replace=False).tolist()
        
        return negatives


class MixedSampler(NegativeSampler):
    """
    Mixed negative sampling strategy.
    
    Combines multiple sampling strategies with specified probabilities.
    """
    
    def __init__(
        self,
        samplers: List[NegativeSampler],
        weights: Optional[List[float]] = None,
        seed: int = 42
    ):
        """
        Initialize mixed sampler.
        
        Args:
            samplers: List of negative samplers
            weights: Probability weights for each sampler (default: uniform)
            seed: Random seed
        """
        if not samplers:
            raise ValueError("At least one sampler must be provided")
        
        super().__init__(samplers[0].n_items, seed)
        self.samplers = samplers
        
        if weights is None:
            self.weights = [1.0 / len(samplers)] * len(samplers)
        else:
            if len(weights) != len(samplers):
                raise ValueError("Number of weights must match number of samplers")
            total = sum(weights)
            self.weights = [w / total for w in weights]
    
    def sample(
        self,
        user_idx: int,
        positive_items: Set[int],
        n_negatives: int = 1
    ) -> List[int]:
        """Sample negatives using mixed strategy."""
        negatives = []
        
        for _ in range(n_negatives):
            # Select sampler based on weights
            sampler = np.random.choice(self.samplers, p=self.weights)
            
            # Sample one negative
            neg = sampler.sample(user_idx, positive_items, n_negatives=1)
            negatives.extend(neg)
        
        return negatives


def create_negative_samples(
    interactions_df,
    sampler: NegativeSampler,
    n_negatives_per_positive: int = 1,
    user_col: str = 'user_id',
    item_col: str = 'item_id'
):
    """
    Create negative samples for a dataset.
    
    Args:
        interactions_df: DataFrame with positive interactions
        sampler: NegativeSampler instance
        n_negatives_per_positive: Number of negative samples per positive
        user_col: Name of user ID column
        item_col: Name of item ID column
        
    Returns:
        DataFrame with positive and negative samples (with 'label' column)
    """
    import pandas as pd
    
    # Add label to positives
    positives = interactions_df.copy()
    positives['label'] = 1
    
    # Build user positive items
    user_positive_items = {}
    for user_id, group in interactions_df.groupby(user_col):
        user_positive_items[user_id] = set(group[item_col].values)
    
    # Generate negatives
    negative_samples = []
    
    for user_id, positive_items in user_positive_items.items():
        n_negatives = len(positive_items) * n_negatives_per_positive
        
        neg_items = sampler.sample(
            user_idx=user_id,
            positive_items=positive_items,
            n_negatives=n_negatives
        )
        
        for neg_item in neg_items:
            negative_samples.append({
                user_col: user_id,
                item_col: neg_item,
                'label': 0
            })
    
    negatives = pd.DataFrame(negative_samples)
    
    # Combine positives and negatives
    combined = pd.concat([positives, negatives], ignore_index=True)
    
    return combined

