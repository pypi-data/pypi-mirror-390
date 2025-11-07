"""
Evaluation metrics for recommender systems.
"""
import numpy as np
from typing import List, Dict, Set, Union, Optional
import warnings


def precision_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute Precision@K.
    
    Precision@K = (# of recommended items @k that are relevant) / k
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        Average Precision@K across all users
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    precisions = []
    for rec, rel in zip(recommended, relevant):
        rec_k = rec[:k]
        n_relevant_and_recommended = len(set(rec_k) & rel)
        precisions.append(n_relevant_and_recommended / k if k > 0 else 0.0)
    
    return np.mean(precisions) if precisions else 0.0


def recall_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute Recall@K.
    
    Recall@K = (# of recommended items @k that are relevant) / (# of relevant items)
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        Average Recall@K across all users
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    recalls = []
    for rec, rel in zip(recommended, relevant):
        if len(rel) == 0:
            continue
        
        rec_k = rec[:k]
        n_relevant_and_recommended = len(set(rec_k) & rel)
        recalls.append(n_relevant_and_recommended / len(rel))
    
    return np.mean(recalls) if recalls else 0.0


def f1_score_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute F1-score@K.
    
    F1@K = 2 * (Precision@K * Recall@K) / (Precision@K + Recall@K)
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        Average F1@K across all users
    """
    precision = precision_at_k(recommended, relevant, k)
    recall = recall_at_k(recommended, relevant, k)
    
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)


def hit_rate_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute Hit Rate@K (also known as Recall in some contexts).
    
    Hit Rate@K = (# of users with at least one relevant item in top-k) / (# of users)
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        Hit Rate@K
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    hits = 0
    for rec, rel in zip(recommended, relevant):
        rec_k = rec[:k]
        if len(set(rec_k) & rel) > 0:
            hits += 1
    
    return hits / len(recommended) if len(recommended) > 0 else 0.0


def ndcg_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int,
    relevance_scores: Optional[List[Dict[int, float]]] = None
) -> float:
    """
    Compute Normalized Discounted Cumulative Gain (NDCG)@K.
    
    DCG@K = sum(rel_i / log2(i + 2)) for i in [0, k)
    NDCG@K = DCG@K / IDCG@K
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        relevance_scores: Optional list of dicts mapping item_id to relevance score
                         If not provided, binary relevance (0 or 1) is assumed
        
    Returns:
        Average NDCG@K across all users
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    ndcgs = []
    for i, (rec, rel) in enumerate(zip(recommended, relevant)):
        rec_k = rec[:k]
        
        # Compute DCG
        dcg = 0.0
        for j, item_id in enumerate(rec_k):
            if relevance_scores is not None:
                rel_score = relevance_scores[i].get(item_id, 0.0)
            else:
                rel_score = 1.0 if item_id in rel else 0.0
            
            dcg += rel_score / np.log2(j + 2)
        
        # Compute IDCG (ideal DCG)
        if relevance_scores is not None:
            ideal_scores = sorted(relevance_scores[i].values(), reverse=True)[:k]
        else:
            ideal_scores = [1.0] * min(len(rel), k)
        
        idcg = sum(score / np.log2(j + 2) for j, score in enumerate(ideal_scores))
        
        # NDCG
        if idcg > 0:
            ndcgs.append(dcg / idcg)
        elif dcg == 0:
            ndcgs.append(1.0)  # Perfect score if no relevant items
        else:
            ndcgs.append(0.0)
    
    return np.mean(ndcgs) if ndcgs else 0.0


def map_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute Mean Average Precision (MAP)@K.
    
    AP@K = sum(P(k) * rel(k)) / min(m, K)
    where m is the number of relevant items
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        MAP@K across all users
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    aps = []
    for rec, rel in zip(recommended, relevant):
        if len(rel) == 0:
            continue
        
        rec_k = rec[:k]
        
        # Compute AP
        score = 0.0
        num_hits = 0.0
        
        for i, item_id in enumerate(rec_k):
            if item_id in rel:
                num_hits += 1.0
                score += num_hits / (i + 1.0)
        
        aps.append(score / min(len(rel), k))
    
    return np.mean(aps) if aps else 0.0


def mrr_at_k(
    recommended: List[List[int]],
    relevant: List[Set[int]],
    k: int
) -> float:
    """
    Compute Mean Reciprocal Rank (MRR)@K.
    
    RR = 1 / rank of first relevant item
    MRR = mean(RR) across all users
    
    Args:
        recommended: List of lists of recommended item IDs for each user
        relevant: List of sets of relevant/ground-truth item IDs for each user
        k: Cutoff rank
        
    Returns:
        MRR@K across all users
    """
    if len(recommended) != len(relevant):
        raise ValueError("recommended and relevant must have same length")
    
    rrs = []
    for rec, rel in zip(recommended, relevant):
        rec_k = rec[:k]
        
        for i, item_id in enumerate(rec_k):
            if item_id in rel:
                rrs.append(1.0 / (i + 1.0))
                break
        else:
            rrs.append(0.0)
    
    return np.mean(rrs) if rrs else 0.0


def coverage(
    recommended: List[List[int]],
    n_items: int
) -> float:
    """
    Compute catalog coverage.
    
    Coverage = (# of unique items recommended) / (# of total items)
    
    Args:
        recommended: List of lists of recommended item IDs
        n_items: Total number of items in catalog
        
    Returns:
        Coverage ratio
    """
    unique_items = set()
    for rec in recommended:
        unique_items.update(rec)
    
    return len(unique_items) / n_items if n_items > 0 else 0.0


def diversity(
    recommended: List[List[int]],
    item_features: Optional[np.ndarray] = None
) -> float:
    """
    Compute average intra-list diversity.
    
    Diversity = average pairwise distance between items in recommendation lists
    
    Args:
        recommended: List of lists of recommended item IDs
        item_features: Optional item feature matrix (n_items x n_features)
                      If not provided, uses item IDs as indicator
        
    Returns:
        Average diversity score
    """
    diversities = []
    
    for rec in recommended:
        if len(rec) < 2:
            continue
        
        # Compute pairwise distances
        distances = []
        for i in range(len(rec)):
            for j in range(i + 1, len(rec)):
                if item_features is not None:
                    # Cosine distance
                    feat_i = item_features[rec[i]]
                    feat_j = item_features[rec[j]]
                    
                    norm_i = np.linalg.norm(feat_i)
                    norm_j = np.linalg.norm(feat_j)
                    
                    if norm_i > 0 and norm_j > 0:
                        similarity = np.dot(feat_i, feat_j) / (norm_i * norm_j)
                        distance = 1 - similarity
                    else:
                        distance = 1.0
                else:
                    # Binary distance (items are different)
                    distance = 1.0 if rec[i] != rec[j] else 0.0
                
                distances.append(distance)
        
        if distances:
            diversities.append(np.mean(distances))
    
    return np.mean(diversities) if diversities else 0.0


def novelty(
    recommended: List[List[int]],
    item_popularity: Dict[int, int],
    n_users: int
) -> float:
    """
    Compute average novelty of recommendations.
    
    Novelty = -log2(popularity) - penalizes popular items
    
    Args:
        recommended: List of lists of recommended item IDs
        item_popularity: Dict mapping item_id to number of interactions
        n_users: Total number of users
        
    Returns:
        Average novelty score
    """
    novelties = []
    
    for rec in recommended:
        rec_novelty = []
        for item_id in rec:
            pop = item_popularity.get(item_id, 0)
            prob = pop / n_users if n_users > 0 else 0.0
            
            if prob > 0:
                nov = -np.log2(prob)
            else:
                nov = 0.0
            
            rec_novelty.append(nov)
        
        if rec_novelty:
            novelties.append(np.mean(rec_novelty))
    
    return np.mean(novelties) if novelties else 0.0


# Rating prediction metrics

def rmse(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Compute Root Mean Squared Error.
    
    Args:
        predictions: Predicted ratings
        targets: True ratings
        
    Returns:
        RMSE
    """
    return np.sqrt(np.mean((predictions - targets) ** 2))


def mae(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Compute Mean Absolute Error.
    
    Args:
        predictions: Predicted ratings
        targets: True ratings
        
    Returns:
        MAE
    """
    return np.mean(np.abs(predictions - targets))


def mse(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Compute Mean Squared Error.
    
    Args:
        predictions: Predicted ratings
        targets: True ratings
        
    Returns:
        MSE
    """
    return np.mean((predictions - targets) ** 2)


def r_squared(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Compute R-squared (coefficient of determination).
    
    Args:
        predictions: Predicted ratings
        targets: True ratings
        
    Returns:
        R-squared score
    """
    ss_res = np.sum((targets - predictions) ** 2)
    ss_tot = np.sum((targets - np.mean(targets)) ** 2)
    
    if ss_tot == 0:
        return 0.0
    
    return 1 - (ss_res / ss_tot)

