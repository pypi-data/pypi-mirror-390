"""Model training module - Robust and universal implementation"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader as TorchDataLoader
from tqdm import tqdm
import numpy as np

from minilin.data import DataLoader, DataAugmenter
from minilin.utils import setup_logger

logger = setup_logger(__name__)


class SimpleDataset(Dataset):
    """Universal PyTorch dataset wrapper."""
    
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
            if isinstance(label, str) and self.label_map:
                label = self.label_map.get(label, 0)
            elif not isinstance(label, int):
                label = 0
            
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
    Universal model trainer - works for any classification task.
    
    Args:
        model: PyTorch model (will be configured automatically)
        task: Task type
        strategy: Training strategy
    """
    
    def __init__(self, model: nn.Module, task: str, strategy: str):
        self.model = model
        self.task = task
        self.strategy = strategy
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.tokenizer = None
        self.label_map = {}
        self.num_labels = 0
        
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
        """Train the model."""
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
        
        # Build label map from all data
        all_data = train_data + val_data
        self._build_label_map(all_data)
        
        # Configure model for the number of classes
        self._configure_model(self.num_labels)
        
        # Move model to device AFTER configuration
        self.model.to(self.device)
        
        # Load tokenizer for text tasks
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            self._load_tokenizer()
        
        # Create datasets
        train_dataset = SimpleDataset(train_data, self.tokenizer, label_map=self.label_map)
        val_dataset = SimpleDataset(val_data, self.tokenizer, label_map=self.label_map)
        
        train_loader = TorchDataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = TorchDataLoader(val_dataset, batch_size=batch_size)
        
        # Setup optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        best_val_loss = float('inf')
        metrics = {'train_losses': [], 'val_losses': []}
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            train_loss = self._train_epoch(train_loader, optimizer)
            val_loss = self._validate_epoch(val_loader)
            
            metrics['train_losses'].append(train_loss)
            metrics['val_losses'].append(val_loss)
            
            logger.info(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                logger.info("New best model!")
        
        metrics['best_val_loss'] = best_val_loss
        logger.info("Training completed!")
        
        return metrics
    
    def evaluate(self, test_data_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Evaluate the model."""
        logger.info("Evaluating model...")
        
        if test_data_path is None:
            logger.warning("No test data path provided")
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Load test data
        data_loader = DataLoader(data_path=test_data_path, task=self.task)
        _, _, test_data = data_loader.load()
        
        if not test_data:
            logger.warning("No test data available")
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Debug: Check test data labels
        test_labels = set()
        for sample in test_data:
            label = sample.get('label', sample.get('labels'))
            if label is not None:
                test_labels.add(label)
        
        logger.info(f"Test data labels: {test_labels}")
        logger.info(f"Training label_map: {self.label_map}")
        
        # Check if test labels are in training label_map
        missing_labels = test_labels - set(self.label_map.keys())
        if missing_labels:
            logger.warning(f"Test data contains labels not seen in training: {missing_labels}")
        
        # Create test dataset with SAME label_map as training
        test_dataset = SimpleDataset(test_data, self.tokenizer, label_map=self.label_map)
        test_loader = TorchDataLoader(test_dataset, batch_size=16, shuffle=False)
        
        # Evaluate
        self.model.eval()
        all_preds = []
        all_labels = []
        all_texts = []
        
        with torch.no_grad():
            for batch_idx, batch in enumerate(tqdm(test_loader, desc="Evaluating")):
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask']
                )
                
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(batch['labels'].cpu().numpy())
                
                # Debug first batch
                if batch_idx == 0:
                    logger.info(f"First batch predictions: {preds.cpu().numpy()}")
                    logger.info(f"First batch true labels: {batch['labels'].cpu().numpy()}")
                    logger.info(f"First batch logits: {outputs.logits[0].cpu().numpy()}")
        
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
        loss_fct = nn.CrossEntropyLoss()
        
        for batch in tqdm(train_loader, desc="Training"):
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                    for k, v in batch.items()}
            
            # Forward pass
            outputs = self.model(
                input_ids=batch['input_ids'],
                attention_mask=batch['attention_mask']
            )
            
            # Compute loss manually
            loss = loss_fct(outputs.logits, batch['labels'])
            
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
            model_name = 'distilbert-base-uncased'
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
        
        sorted_labels = sorted(labels)
        
        # Create mapping: label -> index
        if all(isinstance(l, int) for l in sorted_labels):
            # Integer labels
            self.label_map = {label: label for label in sorted_labels}
        else:
            # String labels
            self.label_map = {label: idx for idx, label in enumerate(sorted_labels)}
        
        self.num_labels = len(self.label_map)
        logger.info(f"Built label map with {self.num_labels} classes: {self.label_map}")
    
    def _configure_model(self, num_labels: int):
        """Configure model for the correct number of classes."""
        try:
            # Update config
            if hasattr(self.model, 'config'):
                self.model.config.num_labels = num_labels
                self.model.config.problem_type = "single_label_classification"
            
            # Replace classifier layer
            if hasattr(self.model, 'classifier'):
                in_features = self.model.classifier.in_features
                self.model.classifier = nn.Linear(in_features, num_labels)
                nn.init.xavier_uniform_(self.model.classifier.weight)
                nn.init.zeros_(self.model.classifier.bias)
            
            logger.info(f"Configured model for {num_labels} classes")
            
        except Exception as e:
            logger.error(f"Failed to configure model: {e}")
            raise
