"""
Inference optimization utilities.

Provides tools for:
- Batch inference
- Caching
- Approximate methods
- Performance profiling
"""
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable
import time
from functools import wraps
import pickle
from pathlib import Path


class InferenceCache:
    """
    Cache for inference results.
    
    Useful for serving scenarios where same users/items are queried repeatedly.
    """
    
    def __init__(self, max_size: int = 10000, ttl: Optional[float] = None):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached entries
            ttl: Time-to-live in seconds (None for no expiration)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_times = {}
        self.insert_times = {}
    
    def get(self, key: Tuple) -> Optional[Any]:
        """
        Get cached result.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            return None
        
        # Check TTL
        if self.ttl is not None:
            if time.time() - self.insert_times[key] > self.ttl:
                del self.cache[key]
                del self.insert_times[key]
                del self.access_times[key]
                return None
        
        # Update access time
        self.access_times[key] = time.time()
        
        return self.cache[key]
    
    def put(self, key: Tuple, value: Any):
        """
        Put result in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            # Evict least recently accessed
            lru_key = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]
            del self.insert_times[lru_key]
        
        current_time = time.time()
        self.cache[key] = value
        self.access_times[key] = current_time
        self.insert_times[key] = current_time
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.access_times.clear()
        self.insert_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl': self.ttl
        }


class BatchInference:
    """
    Batch inference wrapper for efficient processing.
    
    Batches individual requests together for better throughput.
    """
    
    def __init__(
        self,
        model,
        batch_size: int = 128,
        timeout: float = 0.1
    ):
        """
        Initialize batch inference.
        
        Args:
            model: Recommender model
            batch_size: Maximum batch size
            timeout: Maximum time to wait for batch (seconds)
        """
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        
        self.pending_requests = []
        self.last_batch_time = time.time()
    
    def recommend(
        self,
        user_ids: np.ndarray,
        k: int = 10,
        **kwargs
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """
        Generate recommendations with batching.
        
        Args:
            user_ids: User IDs
            k: Number of recommendations
            
        Returns:
            Recommendations
        """
        # Split into batches
        results = {}
        
        for i in range(0, len(user_ids), self.batch_size):
            batch = user_ids[i:i + self.batch_size]
            batch_results = self.model.recommend(batch, k=k, **kwargs)
            results.update(batch_results)
        
        return results
    
    def predict(
        self,
        user_ids: np.ndarray,
        item_ids: np.ndarray
    ) -> np.ndarray:
        """
        Predict scores with batching.
        
        Args:
            user_ids: User IDs
            item_ids: Item IDs
            
        Returns:
            Predicted scores
        """
        # Process in batches
        all_predictions = []
        
        for i in range(0, len(user_ids), self.batch_size):
            batch_users = user_ids[i:i + self.batch_size]
            batch_items = item_ids[i:i + self.batch_size]
            
            batch_preds = self.model.predict(batch_users, batch_items)
            all_predictions.append(batch_preds)
        
        return np.concatenate(all_predictions)


def profile_inference(func: Callable) -> Callable:
    """
    Decorator to profile inference performance.
    
    Tracks:
    - Execution time
    - Number of calls
    - Average latency
    
    Example:
    ```python
    @profile_inference
    def recommend(self, user_ids, k=10):
        return self.model.recommend(user_ids, k)
    ```
    """
    stats = {
        'n_calls': 0,
        'total_time': 0.0,
        'min_time': float('inf'),
        'max_time': 0.0
    }
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        stats['n_calls'] += 1
        stats['total_time'] += elapsed
        stats['min_time'] = min(stats['min_time'], elapsed)
        stats['max_time'] = max(stats['max_time'], elapsed)
        
        return result
    
    def print_stats():
        """Print profiling statistics."""
        if stats['n_calls'] > 0:
            avg_time = stats['total_time'] / stats['n_calls']
            print(f"\n{func.__name__} Statistics:")
            print(f"  Calls: {stats['n_calls']}")
            print(f"  Total time: {stats['total_time']:.3f}s")
            print(f"  Avg time: {avg_time:.3f}s")
            print(f"  Min time: {stats['min_time']:.3f}s")
            print(f"  Max time: {stats['max_time']:.3f}s")
    
    wrapper.stats = stats
    wrapper.print_stats = print_stats
    
    return wrapper


class ModelEnsemble:
    """
    Ensemble of multiple recommender models.
    
    Combines predictions from multiple models using various strategies.
    """
    
    def __init__(
        self,
        models: List[Any],
        weights: Optional[List[float]] = None,
        strategy: str = 'weighted_average'
    ):
        """
        Initialize ensemble.
        
        Args:
            models: List of trained models
            weights: Model weights (default: equal weights)
            strategy: Combination strategy ('weighted_average', 'rank_fusion')
        """
        self.models = models
        
        if weights is None:
            self.weights = [1.0 / len(models)] * len(models)
        else:
            # Normalize weights
            total = sum(weights)
            self.weights = [w / total for w in weights]
        
        self.strategy = strategy
    
    def recommend(
        self,
        user_ids: np.ndarray,
        k: int = 10,
        **kwargs
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """
        Generate ensemble recommendations.
        
        Args:
            user_ids: User IDs
            k: Number of recommendations
            
        Returns:
            Recommendations
        """
        # Get recommendations from each model
        all_recommendations = []
        for model in self.models:
            recs = model.recommend(user_ids, k=k, **kwargs)
            all_recommendations.append(recs)
        
        # Combine using strategy
        if self.strategy == 'weighted_average':
            return self._weighted_average(all_recommendations, user_ids, k)
        elif self.strategy == 'rank_fusion':
            return self._rank_fusion(all_recommendations, user_ids, k)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _weighted_average(
        self,
        all_recommendations: List[Dict],
        user_ids: np.ndarray,
        k: int
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """Weighted average of scores."""
        combined = {}
        
        for user_id in user_ids:
            item_scores = {}
            
            # Aggregate scores from all models
            for weight, recs in zip(self.weights, all_recommendations):
                user_recs = recs.get(user_id, [])
                for item_id, score in user_recs:
                    if item_id not in item_scores:
                        item_scores[item_id] = 0.0
                    item_scores[item_id] += weight * score
            
            # Sort by score and take top-k
            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
            combined[user_id] = sorted_items[:k]
        
        return combined
    
    def _rank_fusion(
        self,
        all_recommendations: List[Dict],
        user_ids: np.ndarray,
        k: int
    ) -> Dict[Any, List[Tuple[Any, float]]]:
        """Borda count rank fusion."""
        combined = {}
        
        for user_id in user_ids:
            item_scores = {}
            
            # Aggregate ranks from all models
            for weight, recs in zip(self.weights, all_recommendations):
                user_recs = recs.get(user_id, [])
                for rank, (item_id, _) in enumerate(user_recs):
                    score = weight * (len(user_recs) - rank)  # Higher rank = higher score
                    if item_id not in item_scores:
                        item_scores[item_id] = 0.0
                    item_scores[item_id] += score
            
            # Sort by fused score and take top-k
            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
            combined[user_id] = sorted_items[:k]
        
        return combined


def optimize_model_for_inference(model, optimization: str = 'quantization'):
    """
    Optimize model for faster inference.
    
    Args:
        model: Trained model
        optimization: Optimization type ('quantization', 'pruning')
        
    Returns:
        Optimized model
    """
    # TODO: Implement model-specific optimizations
    # - Quantization (convert float32 to int8)
    # - Pruning (remove less important connections)
    # - Distillation (train smaller model)
    
    print(f"Optimizing model with {optimization}...")
    
    if optimization == 'quantization':
        # Quantize embeddings/weights
        if hasattr(model, 'item_factors'):
            # Quantize matrix factorization
            model.item_factors = model.item_factors.astype(np.float16)
            if hasattr(model, 'user_factors'):
                model.user_factors = model.user_factors.astype(np.float16)
    
    return model

