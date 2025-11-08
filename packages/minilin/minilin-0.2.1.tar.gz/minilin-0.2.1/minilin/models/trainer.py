"""Model training module"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader as TorchDataLoader
from tqdm import tqdm

from minilin.data import DataLoader, DataAugmenter
from minilin.utils import setup_logger

logger = setup_logger(__name__)


class SimpleDataset(Dataset):
    """Simple PyTorch dataset wrapper."""
    
    def __init__(self, samples: List[Dict[str, Any]], tokenizer=None, max_length: int = 128, label_map: dict = None):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.label_map = label_map or {}
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        if self.tokenizer:
            # Text task
            text = sample.get('text', sample.get('sentence', ''))
            label = sample.get('label', 0)
            
            # Convert label using label_map
            if self.label_map:
                if label in self.label_map:
                    label = self.label_map[label]
                else:
                    # Unknown label - use first label in map
                    label = 0
                    logger.warning(f"Unknown label '{sample.get('label')}' at index {idx}, using 0")
            elif not isinstance(label, int):
                label = 0
            
            # Ensure label is within valid range
            label = max(0, min(label, len(self.label_map) - 1))
            
            encoding = self.tokenizer(
                text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'labels': torch.tensor(label, dtype=torch.long)
            }
        else:
            # Return raw sample for other tasks
            return sample


class Trainer:
    """
    Model trainer with automatic strategy selection.
    
    Args:
        model: PyTorch model
        task: Task type
        strategy: Training strategy
    """
    
    def __init__(self, model: nn.Module, task: str, strategy: str):
        self.model = model
        self.task = task
        self.strategy = strategy
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.tokenizer = None
        self.label_map = {}
        
        logger.info(f"Trainer initialized on device: {self.device}")
    
    def train(
        self,
        data_path: Union[str, Path],
        augmenter: Optional[DataAugmenter] = None,
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        max_samples: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            data_path: Path to training data
            augmenter: Data augmenter instance
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            max_samples: Maximum samples to use
            
        Returns:
            Training metrics
        """
        logger.info("Starting training...")
        
        # Load data
        data_loader = DataLoader(
            data_path=data_path,
            task=self.task,
            max_samples=max_samples
        )
        train_data, val_data, _ = data_loader.load()
        
        # Apply augmentation
        if augmenter and self.strategy != "standard_training":
            logger.info("Applying data augmentation...")
            train_data = augmenter.augment(train_data)
        
        # Build label map from all data (train + val) to ensure consistency
        all_data = train_data + val_data
        self._build_label_map(all_data)
        
        # Update model output size
        self._update_model_output_size(len(self.label_map))
        
        # Load tokenizer for text tasks
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            self._load_tokenizer()
        
        # Create datasets with label mapping
        train_dataset = SimpleDataset(train_data, self.tokenizer, label_map=self.label_map)
        val_dataset = SimpleDataset(val_data, self.tokenizer, label_map=self.label_map)
        
        train_loader = TorchDataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        val_loader = TorchDataLoader(
            val_dataset,
            batch_size=batch_size
        )
        
        # Setup optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        best_val_loss = float('inf')
        metrics = {'train_losses': [], 'val_losses': []}
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Train
            train_loss = self._train_epoch(train_loader, optimizer)
            metrics['train_losses'].append(train_loss)
            
            # Validate
            val_loss = self._validate_epoch(val_loader)
            metrics['val_losses'].append(val_loss)
            
            logger.info(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                logger.info("New best model!")
        
        metrics['best_val_loss'] = best_val_loss
        logger.info("Training completed!")
        
        return metrics
    
    def evaluate(self, test_data_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Evaluate the model.
        
        Args:
            test_data_path: Path to test data
            
        Returns:
            Evaluation metrics
        """
        logger.info("Evaluating model...")
        
        if test_data_path is None:
            logger.warning("No test data path provided, skipping evaluation")
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
        
        # Load test data
        data_loader = DataLoader(
            data_path=test_data_path,
            task=self.task
        )
        _, _, test_data = data_loader.load()
        
        if not test_data:
            logger.warning("No test data available")
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
        
        # Create test dataset
        test_dataset = SimpleDataset(test_data, self.tokenizer, label_map=self.label_map)
        test_loader = TorchDataLoader(test_dataset, batch_size=16, shuffle=False)
        
        # Evaluate
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc="Evaluating"):
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask']
                )
                
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(batch['labels'].cpu().numpy())
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        accuracy = accuracy_score(all_labels, all_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted', zero_division=0
        )
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1)
        }
        
        logger.info(f"Evaluation complete: {metrics}")
        return metrics
    
    def _train_epoch(self, train_loader: TorchDataLoader, optimizer) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        
        for batch_idx, batch in enumerate(tqdm(train_loader, desc="Training")):
            # Move batch to device
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                    for k, v in batch.items()}
            
            # Debug first batch
            if batch_idx == 0:
                logger.info(f"First batch shapes:")
                logger.info(f"  input_ids: {batch['input_ids'].shape}")
                logger.info(f"  attention_mask: {batch['attention_mask'].shape}")
                logger.info(f"  labels: {batch['labels'].shape}")
            
            # Forward pass WITHOUT labels, then compute loss manually
            # This avoids the bug in DistilBERT's internal loss computation
            outputs = self.model(
                input_ids=batch['input_ids'],
                attention_mask=batch['attention_mask']
            )
            
            # Debug first batch
            if batch_idx == 0:
                logger.info(f"  logits: {outputs.logits.shape}")
            
            # Manually compute cross entropy loss
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(outputs.logits, batch['labels'])
            
            if batch_idx == 0:
                logger.info(f"  loss: {loss.item()}")
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def _validate_epoch(self, val_loader: TorchDataLoader) -> float:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0
        loss_fct = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating"):
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                # Forward without labels, compute loss manually
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask']
                )
                loss = loss_fct(outputs.logits, batch['labels'])
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def _load_tokenizer(self):
        """Load tokenizer for text tasks."""
        try:
            from transformers import AutoTokenizer
            
            # Use model's config to get tokenizer
            model_name = 'distilbert-base-uncased'  # Default
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Loaded tokenizer: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
            raise
    
    def _build_label_map(self, samples: List[Dict[str, Any]]):
        """Build label to index mapping."""
        labels = set()
        for sample in samples:
            label = sample.get('label', sample.get('labels'))
            if label is not None:
                labels.add(label)
        
        # Sort labels to ensure consistent mapping
        sorted_labels = sorted(labels)
        
        # If labels are already integers starting from 0, use them directly
        if all(isinstance(l, int) for l in sorted_labels):
            if sorted_labels == list(range(len(sorted_labels))):
                self.label_map = {label: label for label in sorted_labels}
            else:
                self.label_map = {label: idx for idx, label in enumerate(sorted_labels)}
        else:
            # For string labels, create mapping
            self.label_map = {label: idx for idx, label in enumerate(sorted_labels)}
        
        logger.info(f"Built label map with {len(self.label_map)} classes: {self.label_map}")
    
    def _update_model_output_size(self, num_labels: int):
        """Update model output layer size."""
        try:
            # Debug: Print model structure before update
            logger.info(f"Model structure before update:")
            if hasattr(self.model, 'classifier'):
                logger.info(f"  classifier: {self.model.classifier}")
            if hasattr(self.model, 'pre_classifier'):
                logger.info(f"  pre_classifier: {self.model.pre_classifier}")
            if hasattr(self.model, 'config'):
                logger.info(f"  config.num_labels: {self.model.config.num_labels}")
            
            # Update config first
            if hasattr(self.model, 'config'):
                self.model.config.num_labels = num_labels
                self.model.config.problem_type = "single_label_classification"
            
            # CRITICAL FIX: Don't recreate layers, just update the classifier
            # The pre_classifier should stay as-is from pretrained model
            if hasattr(self.model, 'classifier'):
                in_features = self.model.classifier.in_features
                
                # Only replace the classifier layer
                new_classifier = nn.Linear(in_features, num_labels)
                nn.init.xavier_uniform_(new_classifier.weight)
                nn.init.zeros_(new_classifier.bias)
                
                # Replace and move to device
                self.model.classifier = new_classifier.to(self.device)
            
            # Debug: Print model structure after update
            logger.info(f"Model structure after update:")
            if hasattr(self.model, 'classifier'):
                logger.info(f"  classifier: {self.model.classifier}")
            if hasattr(self.model, 'config'):
                logger.info(f"  config.num_labels: {self.model.config.num_labels}")
            
            logger.info(f"Updated model for {num_labels} classes")
            
        except Exception as e:
            logger.warning(f"Could not update model output size: {e}")
            import traceback
            logger.warning(traceback.format_exc())
