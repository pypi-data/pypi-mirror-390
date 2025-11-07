"""
SASRec: Self-Attentive Sequential Recommendation

Reference:
Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential 
Recommendation. In ICDM '18.

SASRec uses self-attention mechanism to model user behavior sequences
and predict next items.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple, Any, Optional
from ...core.base import ImplicitRecommender

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class PointWiseFeedForward(nn.Module):
        """Position-wise Feed-Forward Network."""
        
        def __init__(self, hidden_units: int, dropout_rate: float):
            super(PointWiseFeedForward, self).__init__()
            
            self.conv1 = nn.Conv1d(hidden_units, hidden_units, kernel_size=1)
            self.dropout1 = nn.Dropout(p=dropout_rate)
            self.relu = nn.ReLU()
            self.conv2 = nn.Conv1d(hidden_units, hidden_units, kernel_size=1)
            self.dropout2 = nn.Dropout(p=dropout_rate)
        
        def forward(self, inputs):
            # inputs: [batch_size, seq_len, hidden_units]
            outputs = self.dropout2(self.conv2(self.relu(self.dropout1(self.conv1(inputs.transpose(-1, -2))))))
            outputs = outputs.transpose(-1, -2)  # [batch_size, seq_len, hidden_units]
            outputs += inputs
            return outputs


    class SASRecModel(nn.Module):
        """
        Self-Attentive Sequential Recommendation model.
        
        Uses multi-head self-attention to capture sequential patterns.
        """
        
        def __init__(
            self,
            n_items: int,
            hidden_units: int = 50,
            n_blocks: int = 2,
            n_heads: int = 1,
            dropout_rate: float = 0.2,
            max_seq_length: int = 50
        ):
            super(SASRecModel, self).__init__()
            
            self.n_items = n_items
            self.hidden_units = hidden_units
            self.n_blocks = n_blocks
            self.n_heads = n_heads
            self.dropout_rate = dropout_rate
            self.max_seq_length = max_seq_length
            
            # Item embedding (add 1 for padding token at index 0)
            self.item_emb = nn.Embedding(n_items + 1, hidden_units, padding_idx=0)
            
            # Positional embedding
            self.pos_emb = nn.Embedding(max_seq_length, hidden_units)
            
            # Dropout
            self.emb_dropout = nn.Dropout(p=dropout_rate)
            
            # Self-attention blocks
            self.attention_layernorms = nn.ModuleList()
            self.attention_layers = nn.ModuleList()
            self.forward_layernorms = nn.ModuleList()
            self.forward_layers = nn.ModuleList()
            
            for _ in range(n_blocks):
                self.attention_layernorms.append(nn.LayerNorm(hidden_units))
                self.attention_layers.append(
                    nn.MultiheadAttention(
                        hidden_units,
                        n_heads,
                        dropout=dropout_rate,
                        batch_first=True
                    )
                )
                self.forward_layernorms.append(nn.LayerNorm(hidden_units))
                self.forward_layers.append(PointWiseFeedForward(hidden_units, dropout_rate))
            
            # Final layer norm
            self.last_layernorm = nn.LayerNorm(hidden_units)
            
            # Initialize weights
            self._init_weights()
        
        def _init_weights(self):
            """Initialize model weights."""
            for module in self.modules():
                if isinstance(module, nn.Embedding):
                    nn.init.normal_(module.weight, mean=0.0, std=0.01)
                elif isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        
        def forward(self, seq_items, positions):
            """
            Forward pass.
            
            Args:
                seq_items: Item sequences [batch_size, seq_len]
                positions: Position indices [batch_size, seq_len]
                
            Returns:
                Sequence representations [batch_size, seq_len, hidden_units]
            """
            # Get embeddings
            seq_emb = self.item_emb(seq_items)  # [batch_size, seq_len, hidden_units]
            pos_emb = self.pos_emb(positions)   # [batch_size, seq_len, hidden_units]
            
            # Add positional encoding
            seq_emb += pos_emb
            seq_emb = self.emb_dropout(seq_emb)
            
            # Create attention mask (causal mask for autoregressive)
            seq_len = seq_items.size(1)
            attention_mask = ~torch.tril(torch.ones((seq_len, seq_len), dtype=torch.bool, device=seq_items.device))
            
            # Apply self-attention blocks
            for i in range(self.n_blocks):
                # Multi-head self-attention
                Q = self.attention_layernorms[i](seq_emb)
                seq_emb_attn, _ = self.attention_layers[i](
                    Q, Q, Q,
                    attn_mask=attention_mask,
                    need_weights=False
                )
                seq_emb = seq_emb + seq_emb_attn
                
                # Feed-forward
                seq_emb = self.forward_layernorms[i](seq_emb)
                seq_emb = self.forward_layers[i](seq_emb)
            
            # Final layer norm
            seq_emb = self.last_layernorm(seq_emb)
            
            return seq_emb
        
        def predict(self, seq_emb, item_indices):
            """
            Predict scores for items.
            
            Args:
                seq_emb: Sequence embeddings [batch_size, hidden_units]
                item_indices: Item indices [batch_size, n_items] or [batch_size]
                
            Returns:
                Scores [batch_size, n_items] or [batch_size]
            """
            item_embs = self.item_emb(item_indices)  # [..., hidden_units]
            
            if item_indices.dim() == 1:
                # Single item per sequence
                scores = (seq_emb * item_embs).sum(dim=-1)
            else:
                # Multiple items
                scores = torch.matmul(seq_emb.unsqueeze(1), item_embs.transpose(-1, -2)).squeeze(1)
            
            return scores


    class SASRecDataset(Dataset):
        """Dataset for SASRec training."""
        
        def __init__(
            self,
            sequences: List[List[int]],
            max_seq_length: int,
            n_items: int,
            n_negatives: int = 1
        ):
            self.sequences = sequences
            self.max_seq_length = max_seq_length
            self.n_items = n_items
            self.n_negatives = n_negatives
        
        def __len__(self):
            return len(self.sequences)
        
        def __getitem__(self, idx):
            seq = self.sequences[idx]
            
            # Pad or truncate sequence
            if len(seq) > self.max_seq_length:
                seq = seq[-self.max_seq_length:]
            else:
                seq = [0] * (self.max_seq_length - len(seq)) + seq
            
            # Input: all but last
            # Target: all but first
            input_seq = seq[:-1]
            target_seq = seq[1:]
            
            # Sample negatives for each position
            negatives = []
            for target in target_seq:
                neg_items = []
                for _ in range(self.n_negatives):
                    neg_item = np.random.randint(1, self.n_items + 1)
                    while neg_item == target:
                        neg_item = np.random.randint(1, self.n_items + 1)
                    neg_items.append(neg_item)
                negatives.append(neg_items)
            
            return (
                torch.LongTensor(input_seq),
                torch.LongTensor(target_seq),
                torch.LongTensor(negatives)
            )


class SASRecRecommender(ImplicitRecommender):
    """
    SASRec: Self-Attentive Sequential Recommendation.
    
    Key features:
    - Self-attention mechanism for sequence modeling
    - Captures both short-term and long-term dependencies
    - Autoregressive training (predict next item)
    - State-of-the-art for sequential recommendations
    """
    
    def __init__(
        self,
        hidden_units: int = 50,
        n_blocks: int = 2,
        n_heads: int = 1,
        dropout_rate: float = 0.2,
        max_seq_length: int = 50,
        learning_rate: float = 0.001,
        batch_size: int = 128,
        epochs: int = 50,
        n_negatives: int = 1,
        device: str = 'auto'
    ):
        """
        Initialize SASRec recommender.
        
        Args:
            hidden_units: Hidden dimension
            n_blocks: Number of self-attention blocks
            n_heads: Number of attention heads
            dropout_rate: Dropout rate
            max_seq_length: Maximum sequence length
            learning_rate: Learning rate
            batch_size: Batch size
            epochs: Number of epochs
            n_negatives: Number of negative samples
            device: Device ('auto', 'cpu', 'cuda')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for SASRec. Install with: pip install torch")
        
        super().__init__()
        
        self.hidden_units = hidden_units
        self.n_blocks = n_blocks
        self.n_heads = n_heads
        self.dropout_rate = dropout_rate
        self.max_seq_length = max_seq_length
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.n_negatives = n_negatives
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model = None
        self.user_sequences = {}
    
    def fit(self, interactions: pd.DataFrame, **kwargs) -> 'SASRecRecommender':
        """
        Train SASRec model.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'timestamp'] (optional)
            
        Returns:
            self
        """
        print(f"Training SASRec model on {self.device}...")
        
        # Create mappings (item IDs start from 1, 0 is reserved for padding)
        self._create_mappings(interactions)
        self._build_seen_items(interactions)
        
        # Remap items to start from 1
        self.item_mapping_offset = {item_id: idx + 1 for item_id, idx in self.item_mapping.items()}
        self.reverse_item_mapping_offset = {idx + 1: item_id for item_id, idx in self.item_mapping.items()}
        
        # Build sequences per user
        print("Building user sequences...")
        sequences = []
        
        if 'timestamp' in interactions.columns:
            interactions_sorted = interactions.sort_values(['user_id', 'timestamp'])
        else:
            interactions_sorted = interactions
        
        for user_id, group in interactions_sorted.groupby('user_id'):
            # Map items to 1-indexed
            item_sequence = [self.item_mapping_offset[item_id] for item_id in group['item_id'].values]
            
            # Need at least 2 items for training
            if len(item_sequence) >= 2:
                sequences.append(item_sequence)
                user_idx = self.user_mapping[user_id]
                self.user_sequences[user_idx] = item_sequence
        
        print(f"Created {len(sequences)} sequences")
        
        # Create model
        self.model = SASRecModel(
            n_items=self.n_items,
            hidden_units=self.hidden_units,
            n_blocks=self.n_blocks,
            n_heads=self.n_heads,
            dropout_rate=self.dropout_rate,
            max_seq_length=self.max_seq_length
        ).to(self.device)
        
        # Create dataset
        dataset = SASRecDataset(
            sequences=sequences,
            max_seq_length=self.max_seq_length,
            n_items=self.n_items,
            n_negatives=self.n_negatives
        )
        
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0
        )
        
        # Setup optimizer
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Training loop
        print(f"Training for {self.epochs} epochs...")
        self.model.train()
        
        for epoch in range(self.epochs):
            total_loss = 0.0
            n_batches = 0
            
            for batch in dataloader:
                input_seq, target_seq, neg_samples = batch
                input_seq = input_seq.to(self.device)
                target_seq = target_seq.to(self.device)
                neg_samples = neg_samples.to(self.device)
                
                # Create position indices
                positions = torch.arange(input_seq.size(1), device=self.device).unsqueeze(0).expand_as(input_seq)
                
                # Forward pass
                seq_emb = self.model(input_seq, positions)  # [batch, seq_len, hidden]
                
                # Get last non-padding position embeddings
                mask = (input_seq != 0).float()
                seq_lengths = mask.sum(dim=1).long() - 1
                batch_indices = torch.arange(input_seq.size(0), device=self.device)
                last_emb = seq_emb[batch_indices, seq_lengths]  # [batch, hidden]
                
                # Positive scores
                pos_emb = self.model.item_emb(target_seq[batch_indices, seq_lengths])
                pos_scores = (last_emb * pos_emb).sum(dim=-1)
                
                # Negative scores
                neg_emb = self.model.item_emb(neg_samples[batch_indices, seq_lengths, :])
                neg_scores = (last_emb.unsqueeze(1) * neg_emb).sum(dim=-1)
                
                # Binary cross-entropy loss
                pos_loss = -torch.log(torch.sigmoid(pos_scores) + 1e-10).mean()
                neg_loss = -torch.log(1 - torch.sigmoid(neg_scores) + 1e-10).mean()
                
                loss = pos_loss + neg_loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                n_batches += 1
            
            avg_loss = total_loss / n_batches
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"  Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}")
        
        self.is_fitted = True
        print("SASRec training complete!")
        
        return self
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict scores for user-item pairs."""
        self._check_fitted()
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for user_id, item_id in zip(user_ids, item_ids):
                if user_id not in self.user_mapping or item_id not in self.item_mapping:
                    predictions.append(0.0)
                    continue
                
                user_idx = self.user_mapping[user_id]
                
                # Get user sequence
                if user_idx not in self.user_sequences:
                    predictions.append(0.0)
                    continue
                
                seq = self.user_sequences[user_idx]
                
                # Prepare sequence
                if len(seq) > self.max_seq_length:
                    seq = seq[-self.max_seq_length:]
                else:
                    seq = [0] * (self.max_seq_length - len(seq)) + seq
                
                seq_tensor = torch.LongTensor([seq]).to(self.device)
                positions = torch.arange(len(seq), device=self.device).unsqueeze(0)
                
                # Get sequence embedding
                seq_emb = self.model(seq_tensor, positions)
                
                # Get last position
                mask = (seq_tensor != 0).float()
                seq_len = int(mask.sum().item()) - 1
                last_emb = seq_emb[0, seq_len]
                
                # Predict for item
                item_idx = self.item_mapping_offset[item_id]
                item_tensor = torch.LongTensor([item_idx]).to(self.device)
                
                score = self.model.predict(last_emb, item_tensor).item()
                predictions.append(score)
        
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
        
        self.model.eval()
        recommendations = {}
        
        with torch.no_grad():
            for user_id in user_ids:
                if user_id not in self.user_mapping:
                    recommendations[user_id] = []
                    continue
                
                user_idx = self.user_mapping[user_id]
                
                if user_idx not in self.user_sequences:
                    recommendations[user_id] = []
                    continue
                
                seq = self.user_sequences[user_idx]
                
                # Prepare sequence
                if len(seq) > self.max_seq_length:
                    seq = seq[-self.max_seq_length:]
                else:
                    seq = [0] * (self.max_seq_length - len(seq)) + seq
                
                seq_tensor = torch.LongTensor([seq]).to(self.device)
                positions = torch.arange(len(seq), device=self.device).unsqueeze(0)
                
                # Get sequence embedding
                seq_emb = self.model(seq_tensor, positions)
                
                # Get last position
                mask = (seq_tensor != 0).float()
                seq_len = int(mask.sum().item()) - 1
                last_emb = seq_emb[0, seq_len]
                
                # Score all items
                all_item_indices = torch.arange(1, self.n_items + 1, device=self.device)
                scores = self.model.predict(last_emb, all_item_indices).cpu().numpy()
                
                # Exclude seen items
                if exclude_seen:
                    seen_items = self.seen_items.get(user_idx, set())
                    for item_idx in seen_items:
                        mapped_idx = item_idx  # 0-indexed
                        scores[mapped_idx] = -np.inf
                
                # Get top-k
                top_indices = np.argsort(scores)[-k:][::-1]
                
                rec_list = []
                for idx in top_indices:
                    if scores[idx] > -np.inf:
                        # Map back to original item ID
                        item_id = self.reverse_item_mapping_offset[idx + 1]
                        score = scores[idx]
                        rec_list.append((item_id, float(score)))
                
                recommendations[user_id] = rec_list
        
        return recommendations
    
    def _get_model_state(self) -> Dict[str, Any]:
        """Get model state for serialization."""
        return {
            'model_state_dict': self.model.state_dict() if self.model else None,
            'user_sequences': self.user_sequences,
            'seen_items': self.seen_items,
            'item_mapping_offset': self.item_mapping_offset,
            'reverse_item_mapping_offset': self.reverse_item_mapping_offset
        }
    
    def _set_model_state(self, state: Dict[str, Any]):
        """Set model state from deserialization."""
        self.user_sequences = state['user_sequences']
        self.seen_items = state['seen_items']
        self.item_mapping_offset = state['item_mapping_offset']
        self.reverse_item_mapping_offset = state['reverse_item_mapping_offset']
        
        if state['model_state_dict'] is not None:
            self.model = SASRecModel(
                n_items=self.n_items,
                hidden_units=self.hidden_units,
                n_blocks=self.n_blocks,
                n_heads=self.n_heads,
                dropout_rate=self.dropout_rate,
                max_seq_length=self.max_seq_length
            ).to(self.device)
            self.model.load_state_dict(state['model_state_dict'])

