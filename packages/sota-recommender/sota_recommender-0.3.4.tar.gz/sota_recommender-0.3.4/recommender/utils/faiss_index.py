"""
FAISS integration for fast similarity search.

FAISS (Facebook AI Similarity Search) enables efficient similarity search
for large-scale recommendation systems.
"""
import numpy as np
from typing import List, Tuple, Optional
import pickle

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class FAISSIndex:
    """
    FAISS index wrapper for fast similarity search in recommendations.
    
    Supports:
    - Exact search (IndexFlatIP for inner product)
    - Approximate search (IndexIVFFlat, IndexHNSW)
    - GPU acceleration
    """
    
    def __init__(
        self,
        embedding_dim: int,
        index_type: str = 'flat',
        metric: str = 'inner_product',
        n_clusters: int = 100,
        use_gpu: bool = False
    ):
        """
        Initialize FAISS index.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of index ('flat', 'ivf', 'hnsw')
            metric: Distance metric ('inner_product', 'l2')
            n_clusters: Number of clusters for IVF index
            use_gpu: Whether to use GPU acceleration
        """
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is required. Install with: pip install faiss-cpu or faiss-gpu")
        
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        self.n_clusters = n_clusters
        self.use_gpu = use_gpu
        
        self.index = None
        self.item_ids = None
        self._build_index()
    
    def _build_index(self):
        """Build FAISS index based on configuration."""
        if self.metric == 'inner_product':
            # Inner product (for cosine similarity with normalized vectors)
            if self.index_type == 'flat':
                self.index = faiss.IndexFlatIP(self.embedding_dim)
            elif self.index_type == 'ivf':
                quantizer = faiss.IndexFlatIP(self.embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.n_clusters)
            elif self.index_type == 'hnsw':
                self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
        
        elif self.metric == 'l2':
            # L2 distance
            if self.index_type == 'flat':
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            elif self.index_type == 'ivf':
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.n_clusters)
            elif self.index_type == 'hnsw':
                self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
        
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        # Move to GPU if requested
        if self.use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
    
    def add_items(self, item_embeddings: np.ndarray, item_ids: np.ndarray):
        """
        Add items to the index.
        
        Args:
            item_embeddings: Item embeddings [n_items, embedding_dim]
            item_ids: Item IDs [n_items]
        """
        # Ensure float32
        item_embeddings = item_embeddings.astype(np.float32)
        
        # Normalize if using inner product (for cosine similarity)
        if self.metric == 'inner_product':
            norms = np.linalg.norm(item_embeddings, axis=1, keepdims=True)
            item_embeddings = item_embeddings / (norms + 1e-10)
        
        # Train index if needed (for IVF)
        if self.index_type == 'ivf' and not self.index.is_trained:
            print(f"Training IVF index with {len(item_embeddings)} items...")
            self.index.train(item_embeddings)
        
        # Add to index
        self.index.add(item_embeddings)
        self.item_ids = item_ids
        
        print(f"Added {len(item_ids)} items to FAISS index")
    
    def search(
        self,
        query_embeddings: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors.
        
        Args:
            query_embeddings: Query embeddings [n_queries, embedding_dim]
            k: Number of neighbors to return
            
        Returns:
            Tuple of (distances, item_ids)
            - distances: [n_queries, k]
            - item_ids: [n_queries, k]
        """
        # Ensure float32
        query_embeddings = query_embeddings.astype(np.float32)
        
        # Normalize if using inner product
        if self.metric == 'inner_product':
            norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
            query_embeddings = query_embeddings / (norms + 1e-10)
        
        # Set nprobe for IVF
        if self.index_type == 'ivf':
            self.index.nprobe = min(10, self.n_clusters)
        
        # Search
        distances, indices = self.index.search(query_embeddings, k)
        
        # Map indices to item IDs
        item_ids = self.item_ids[indices]
        
        return distances, item_ids
    
    def batch_search(
        self,
        query_embeddings: np.ndarray,
        k: int = 10,
        batch_size: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search in batches for memory efficiency.
        
        Args:
            query_embeddings: Query embeddings [n_queries, embedding_dim]
            k: Number of neighbors
            batch_size: Batch size
            
        Returns:
            Tuple of (distances, item_ids)
        """
        n_queries = len(query_embeddings)
        all_distances = []
        all_item_ids = []
        
        for i in range(0, n_queries, batch_size):
            batch = query_embeddings[i:i + batch_size]
            distances, item_ids = self.search(batch, k)
            all_distances.append(distances)
            all_item_ids.append(item_ids)
        
        return np.vstack(all_distances), np.vstack(all_item_ids)
    
    def save(self, path: str):
        """Save index to disk."""
        if self.use_gpu:
            # Move to CPU before saving
            cpu_index = faiss.index_gpu_to_cpu(self.index)
            faiss.write_index(cpu_index, path)
        else:
            faiss.write_index(self.index, path)
        
        # Save item IDs separately
        with open(path + '.items.pkl', 'wb') as f:
            pickle.dump(self.item_ids, f)
        
        print(f"FAISS index saved to {path}")
    
    def load(self, path: str):
        """Load index from disk."""
        self.index = faiss.read_index(path)
        
        # Move to GPU if requested
        if self.use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        
        # Load item IDs
        with open(path + '.items.pkl', 'rb') as f:
            self.item_ids = pickle.load(f)
        
        print(f"FAISS index loaded from {path}")


def create_faiss_index_from_model(
    model,
    index_type: str = 'flat',
    use_gpu: bool = False
) -> FAISSIndex:
    """
    Create FAISS index from a trained recommender model.
    
    Args:
        model: Trained recommender with item embeddings
        index_type: FAISS index type
        use_gpu: Use GPU acceleration
        
    Returns:
        Configured FAISS index
    """
    # Extract item embeddings
    if hasattr(model, 'item_factors'):
        # Matrix factorization models (ALS, SVD)
        item_embeddings = model.item_factors
        embedding_dim = item_embeddings.shape[1]
    elif hasattr(model, 'model') and hasattr(model.model, 'item_embedding'):
        # Neural models (NCF, LightGCN, SASRec)
        import torch
        with torch.no_grad():
            item_embeddings = model.model.item_embedding.weight.cpu().numpy()
        embedding_dim = item_embeddings.shape[1]
    else:
        raise ValueError("Model does not have extractable item embeddings")
    
    # Create index
    faiss_index = FAISSIndex(
        embedding_dim=embedding_dim,
        index_type=index_type,
        metric='inner_product',
        use_gpu=use_gpu
    )
    
    # Add items
    item_ids = np.array([model.reverse_item_mapping[i] for i in range(model.n_items)])
    faiss_index.add_items(item_embeddings, item_ids)
    
    return faiss_index

