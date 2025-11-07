"""
Training utilities for deep learning based recommenders.
"""
from typing import Optional, Dict, Any, Callable, List, TYPE_CHECKING
import time
import numpy as np
from pathlib import Path
import logging

if TYPE_CHECKING:
    from torch.utils.data import DataLoader

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Define a dummy DataLoader for type hints when PyTorch is not available
    DataLoader = Any  # type: ignore


class Trainer:
    """
    Generic trainer for PyTorch-based recommender models.
    
    Features:
    - Early stopping
    - Learning rate scheduling
    - Checkpointing
    - Progress logging
    """
    
    def __init__(
        self,
        model: Optional['nn.Module'] = None,
        optimizer: Optional['torch.optim.Optimizer'] = None,
        loss_fn: Optional[Callable] = None,
        device: str = 'auto',
        early_stopping_patience: int = 10,
        checkpoint_dir: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize trainer.
        
        Args:
            model: PyTorch model
            optimizer: Optimizer instance
            loss_fn: Loss function
            device: Device to train on ('auto', 'cpu', 'cuda')
            early_stopping_patience: Patience for early stopping
            checkpoint_dir: Directory to save checkpoints
            verbose: Whether to print training progress
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Trainer. Install with: pip install torch")
        
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        if self.model is not None:
            self.model = self.model.to(self.device)
        
        self.early_stopping_patience = early_stopping_patience
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self.verbose = verbose
        
        # Training state
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'epoch_times': []
        }
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.best_epoch = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def train_epoch(
        self,
        train_loader: 'DataLoader',
        epoch: int
    ) -> float:
        """
        Train for one epoch.
        
        Args:
            train_loader: DataLoader for training data
            epoch: Current epoch number
            
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        n_batches = 0
        
        for batch_idx, batch in enumerate(train_loader):
            # Move batch to device
            if isinstance(batch, (list, tuple)):
                batch = [b.to(self.device) if torch.is_tensor(b) else b for b in batch]
            elif isinstance(batch, dict):
                batch = {k: v.to(self.device) if torch.is_tensor(v) else v 
                        for k, v in batch.items()}
            else:
                batch = batch.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            
            if isinstance(batch, (list, tuple)):
                outputs = self.model(*batch[:-1])  # Last element is typically labels
                labels = batch[-1]
            elif isinstance(batch, dict):
                labels = batch.pop('labels', None)
                outputs = self.model(**batch)
            else:
                outputs = self.model(batch)
                labels = None
            
            # Compute loss
            if labels is not None:
                loss = self.loss_fn(outputs, labels)
            else:
                loss = self.loss_fn(outputs)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            n_batches += 1
        
        avg_loss = total_loss / n_batches if n_batches > 0 else 0.0
        return avg_loss
    
    def validate_epoch(
        self,
        val_loader: 'DataLoader'
    ) -> float:
        """
        Validate for one epoch.
        
        Args:
            val_loader: DataLoader for validation data
            
        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0.0
        n_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                # Move batch to device
                if isinstance(batch, (list, tuple)):
                    batch = [b.to(self.device) if torch.is_tensor(b) else b for b in batch]
                elif isinstance(batch, dict):
                    batch = {k: v.to(self.device) if torch.is_tensor(v) else v 
                            for k, v in batch.items()}
                else:
                    batch = batch.to(self.device)
                
                # Forward pass
                if isinstance(batch, (list, tuple)):
                    outputs = self.model(*batch[:-1])
                    labels = batch[-1]
                elif isinstance(batch, dict):
                    labels = batch.pop('labels', None)
                    outputs = self.model(**batch)
                else:
                    outputs = self.model(batch)
                    labels = None
                
                # Compute loss
                if labels is not None:
                    loss = self.loss_fn(outputs, labels)
                else:
                    loss = self.loss_fn(outputs)
                
                total_loss += loss.item()
                n_batches += 1
        
        avg_loss = total_loss / n_batches if n_batches > 0 else 0.0
        return avg_loss
    
    def fit(
        self,
        train_loader: 'DataLoader',
        val_loader: Optional['DataLoader'] = None,
        epochs: int = 100,
        callbacks: Optional[List[Callable]] = None
    ) -> Dict[str, List[float]]:
        """
        Train the model.
        
        Args:
            train_loader: DataLoader for training data
            val_loader: Optional DataLoader for validation data
            epochs: Number of epochs to train
            callbacks: List of callback functions
            
        Returns:
            Training history
        """
        if self.model is None or self.optimizer is None or self.loss_fn is None:
            raise ValueError("Model, optimizer, and loss_fn must be set before training")
        
        callbacks = callbacks or []
        
        for epoch in range(epochs):
            start_time = time.time()
            
            # Train
            train_loss = self.train_epoch(train_loader, epoch)
            self.history['train_loss'].append(train_loss)
            
            # Validate
            if val_loader is not None:
                val_loss = self.validate_epoch(val_loader)
                self.history['val_loss'].append(val_loss)
            else:
                val_loss = None
            
            epoch_time = time.time() - start_time
            self.history['epoch_times'].append(epoch_time)
            
            # Logging
            if self.verbose:
                log_msg = f"Epoch {epoch+1}/{epochs} - {epoch_time:.2f}s - train_loss: {train_loss:.4f}"
                if val_loss is not None:
                    log_msg += f" - val_loss: {val_loss:.4f}"
                self.logger.info(log_msg)
            
            # Early stopping and checkpointing
            if val_loader is not None and val_loss is not None:
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.patience_counter = 0
                    self.best_epoch = epoch
                    
                    # Save checkpoint
                    if self.checkpoint_dir is not None:
                        self.save_checkpoint(epoch)
                else:
                    self.patience_counter += 1
                    
                    if self.patience_counter >= self.early_stopping_patience:
                        if self.verbose:
                            self.logger.info(
                                f"Early stopping at epoch {epoch+1}. "
                                f"Best epoch: {self.best_epoch+1} with val_loss: {self.best_val_loss:.4f}"
                            )
                        break
            
            # Run callbacks
            for callback in callbacks:
                callback(self, epoch, train_loss, val_loss)
        
        return self.history
    
    def save_checkpoint(self, epoch: int, filename: Optional[str] = None):
        """
        Save model checkpoint.
        
        Args:
            epoch: Current epoch
            filename: Optional filename for checkpoint
        """
        if self.checkpoint_dir is None:
            return
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"checkpoint_epoch_{epoch}.pt"
        
        checkpoint_path = self.checkpoint_dir / filename
        
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_loss': self.history['train_loss'][-1] if self.history['train_loss'] else None,
            'val_loss': self.history['val_loss'][-1] if self.history['val_loss'] else None,
            'history': self.history
        }, checkpoint_path)
        
        if self.verbose:
            self.logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """
        Load model checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.history = checkpoint.get('history', self.history)
        
        if self.verbose:
            epoch = checkpoint.get('epoch', 'unknown')
            self.logger.info(f"Checkpoint loaded from epoch {epoch}")
    
    def predict(self, data_loader: 'DataLoader') -> np.ndarray:
        """
        Generate predictions using the trained model.
        
        Args:
            data_loader: DataLoader for prediction data
            
        Returns:
            Predictions as numpy array
        """
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for batch in data_loader:
                # Move batch to device
                if isinstance(batch, (list, tuple)):
                    batch = [b.to(self.device) if torch.is_tensor(b) else b for b in batch]
                    outputs = self.model(*batch)
                elif isinstance(batch, dict):
                    batch = {k: v.to(self.device) if torch.is_tensor(v) else v 
                            for k, v in batch.items()}
                    outputs = self.model(**batch)
                else:
                    batch = batch.to(self.device)
                    outputs = self.model(batch)
                
                predictions.append(outputs.cpu().numpy())
        
        return np.concatenate(predictions, axis=0)


class EarlyStopping:
    """
    Early stopping callback.
    """
    
    def __init__(self, patience: int = 10, min_delta: float = 0.0):
        """
        Args:
            patience: Number of epochs to wait before stopping
            min_delta: Minimum change to qualify as improvement
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.should_stop = False
    
    def __call__(self, trainer: Trainer, epoch: int, train_loss: float, val_loss: Optional[float]):
        """Check if training should stop."""
        if val_loss is None:
            return
        
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True

