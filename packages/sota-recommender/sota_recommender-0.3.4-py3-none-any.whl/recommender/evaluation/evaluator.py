"""
Model evaluator for recommender systems.
"""
from typing import Dict, List, Set, Optional, Callable, Any
import numpy as np
import pandas as pd
from ..core.base import BaseRecommender
from ..core.data import InteractionDataset


class Evaluator:
    """
    Comprehensive evaluator for recommender systems.
    
    Supports both ranking and rating prediction metrics.
    """
    
    def __init__(
        self,
        metrics: Optional[List[str]] = None,
        k_values: Optional[List[int]] = None
    ):
        """
        Initialize evaluator.
        
        Args:
            metrics: List of metric names to compute. If None, uses default set.
            k_values: List of k values for top-k metrics. Default: [5, 10, 20]
        """
        if metrics is None:
            self.metric_names = [
                'precision', 'recall', 'ndcg', 'map', 'mrr', 'hit_rate'
            ]
        else:
            self.metric_names = metrics
        
        self.k_values = k_values or [5, 10, 20]
        
        # Map metric names to functions
        # Import metrics module to avoid name conflict with parameter
        from . import metrics as metrics_module
        self.metric_funcs = {
            'precision': metrics_module.precision_at_k,
            'recall': metrics_module.recall_at_k,
            'f1': metrics_module.f1_score_at_k,
            'ndcg': metrics_module.ndcg_at_k,
            'map': metrics_module.map_at_k,
            'mrr': metrics_module.mrr_at_k,
            'hit_rate': metrics_module.hit_rate_at_k,
            'coverage': metrics_module.coverage,
            'diversity': metrics_module.diversity,
            'novelty': metrics_module.novelty,
            'rmse': metrics_module.rmse,
            'mae': metrics_module.mae,
            'mse': metrics_module.mse,
            'r_squared': metrics_module.r_squared
        }
    
    def evaluate_ranking(
        self,
        model: BaseRecommender,
        test_data: InteractionDataset,
        exclude_train: bool = True,
        train_data: Optional[InteractionDataset] = None
    ) -> Dict[str, float]:
        """
        Evaluate ranking performance.
        
        Args:
            model: Trained recommender model
            test_data: Test dataset
            exclude_train: Whether to exclude training items from recommendations
            train_data: Training dataset (required if exclude_train=True)
            
        Returns:
            Dictionary of metric_name@k -> score
        """
        if exclude_train and train_data is None:
            raise ValueError("train_data must be provided if exclude_train=True")
        
        # Get unique test users
        test_users = test_data.data['user_id'].unique()
        
        # Build ground truth
        relevant_items = []
        for user_id in test_users:
            user_test_items = set(test_data.get_user_items(user_id))
            relevant_items.append(user_test_items)
        
        # Generate recommendations for all k values
        max_k = max(self.k_values)
        
        # Get recommendations
        recommendations_dict = model.recommend(
            user_ids=test_users,
            k=max_k,
            exclude_seen=exclude_train
        )
        
        # Convert to list format
        recommended_items = []
        for user_id in test_users:
            rec_list = recommendations_dict.get(user_id, [])
            # Extract just item IDs (ignore scores)
            if rec_list and isinstance(rec_list[0], tuple):
                rec_list = [item_id for item_id, _ in rec_list]
            recommended_items.append(rec_list)
        
        # Compute metrics for each k
        results = {}
        
        for k in self.k_values:
            for metric_name in self.metric_names:
                if metric_name in ['coverage', 'diversity', 'novelty']:
                    continue  # These are computed separately
                
                metric_func = self.metric_funcs.get(metric_name)
                if metric_func is None:
                    continue
                
                try:
                    score = metric_func(recommended_items, relevant_items, k)
                    results[f'{metric_name}@{k}'] = score
                except Exception as e:
                    print(f"Warning: Could not compute {metric_name}@{k}: {e}")
        
        # Import metrics module
        from . import metrics as metrics_module
        
        # Compute coverage
        if 'coverage' in self.metric_names:
            cov = metrics_module.coverage(recommended_items, test_data.n_items)
            results['coverage'] = cov
        
        # Compute diversity
        if 'diversity' in self.metric_names:
            div = metrics_module.diversity(recommended_items)
            results['diversity'] = div
        
        # Compute novelty
        if 'novelty' in self.metric_names and train_data is not None:
            item_popularity = train_data.data['item_id'].value_counts().to_dict()
            nov = metrics_module.novelty(recommended_items, item_popularity, train_data.n_users)
            results['novelty'] = nov
        
        return results
    
    def evaluate_rating_prediction(
        self,
        model: BaseRecommender,
        test_data: InteractionDataset
    ) -> Dict[str, float]:
        """
        Evaluate rating prediction performance.
        
        Args:
            model: Trained recommender model
            test_data: Test dataset with ratings
            
        Returns:
            Dictionary of metric_name -> score
        """
        if 'rating' not in test_data.data.columns:
            raise ValueError("Test data must have 'rating' column for rating prediction")
        
        # Get predictions
        user_ids = test_data.data['user_id'].values
        item_ids = test_data.data['item_id'].values
        true_ratings = test_data.data['rating'].values
        
        pred_ratings = model.predict(user_ids, item_ids)
        
        # Compute metrics
        results = {}
        
        for metric_name in self.metric_names:
            if metric_name in ['rmse', 'mae', 'mse', 'r_squared']:
                metric_func = self.metric_funcs.get(metric_name)
                if metric_func is not None:
                    score = metric_func(pred_ratings, true_ratings)
                    results[metric_name] = score
        
        return results
    
    def evaluate(
        self,
        model: BaseRecommender,
        test_data: InteractionDataset,
        task: str = 'ranking',
        exclude_train: bool = True,
        train_data: Optional[InteractionDataset] = None
    ) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            model: Trained recommender model
            test_data: Test dataset
            task: 'ranking' or 'rating_prediction'
            exclude_train: Whether to exclude training items (for ranking)
            train_data: Training dataset (required for exclude_train=True)
            
        Returns:
            Dictionary of metric scores
        """
        if task == 'ranking':
            return self.evaluate_ranking(model, test_data, exclude_train, train_data)
        elif task == 'rating_prediction':
            return self.evaluate_rating_prediction(model, test_data)
        else:
            raise ValueError(f"Unknown task: {task}. Choose 'ranking' or 'rating_prediction'")
    
    def print_results(self, results: Dict[str, float]):
        """
        Pretty print evaluation results.
        
        Args:
            results: Dictionary of metric scores
        """
        print("\n" + "=" * 50)
        print("Evaluation Results")
        print("=" * 50)
        
        # Group by k values for ranking metrics
        ranking_metrics = {}
        other_metrics = {}
        
        for metric_name, score in results.items():
            if '@' in metric_name:
                base_metric, k = metric_name.split('@')
                k = int(k)
                if k not in ranking_metrics:
                    ranking_metrics[k] = {}
                ranking_metrics[k][base_metric] = score
            else:
                other_metrics[metric_name] = score
        
        # Print ranking metrics by k
        if ranking_metrics:
            for k in sorted(ranking_metrics.keys()):
                print(f"\nTop-{k} Metrics:")
                for metric_name in sorted(ranking_metrics[k].keys()):
                    score = ranking_metrics[k][metric_name]
                    print(f"  {metric_name:15s}: {score:.4f}")
        
        # Print other metrics
        if other_metrics:
            print("\nOther Metrics:")
            for metric_name, score in sorted(other_metrics.items()):
                print(f"  {metric_name:15s}: {score:.4f}")
        
        print("=" * 50 + "\n")


def cross_validate(
    model_class: type,
    dataset: InteractionDataset,
    n_folds: int = 5,
    metrics: Optional[List[str]] = None,
    k_values: Optional[List[int]] = None,
    **model_kwargs
) -> Dict[str, List[float]]:
    """
    Perform k-fold cross-validation.
    
    Args:
        model_class: Recommender model class
        dataset: Full dataset
        n_folds: Number of folds
        metrics: List of metric names
        k_values: List of k values for top-k metrics
        **model_kwargs: Arguments to pass to model constructor
        
    Returns:
        Dictionary mapping metric names to lists of scores across folds
    """
    from sklearn.model_selection import KFold
    
    evaluator = Evaluator(metrics=metrics, k_values=k_values)
    
    # Get all interactions
    interactions = dataset.data
    
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    all_results = {}
    
    for fold, (train_idx, test_idx) in enumerate(kf.split(interactions)):
        print(f"\nFold {fold + 1}/{n_folds}")
        
        # Split data
        train_df = interactions.iloc[train_idx]
        test_df = interactions.iloc[test_idx]
        
        # Create datasets
        train_data = InteractionDataset(train_df, implicit=dataset.implicit)
        test_data = InteractionDataset(test_df, implicit=dataset.implicit)
        
        # Train model
        model = model_class(**model_kwargs)
        model.fit(train_data.data)
        
        # Evaluate
        results = evaluator.evaluate(
            model,
            test_data,
            task='ranking',
            exclude_train=True,
            train_data=train_data
        )
        
        # Store results
        for metric_name, score in results.items():
            if metric_name not in all_results:
                all_results[metric_name] = []
            all_results[metric_name].append(score)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Cross-Validation Summary")
    print("=" * 50)
    
    for metric_name, scores in sorted(all_results.items()):
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        print(f"{metric_name:20s}: {mean_score:.4f} ± {std_score:.4f}")
    
    print("=" * 50 + "\n")
    
    return all_results

