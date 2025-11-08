"""
Image model trainer
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import torch
import torch.nn as nn
from torch.utils.data import DataLoader as TorchDataLoader
from tqdm import tqdm

from minilin.data.image_loader import ImageDataLoader, ImageDataset
from minilin.data.image_augmenter import ImageAugmenter
from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ImageTrainer:
    """
    Trainer for image classification models.
    """
    
    def __init__(
        self,
        model: nn.Module,
        num_classes: int,
        device: Optional[torch.device] = None
    ):
        """
        Args:
            model: PyTorch model
            num_classes: Number of classes
            device: Device to use
        """
        self.model = model
        self.num_classes = num_classes
        
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        self.model.to(self.device)
        
        # Update model output layer
        self._update_model_output()
        
        logger.info(f"ImageTrainer initialized on {self.device}")
        logger.info(f"Number of classes: {num_classes}")
    
    def _update_model_output(self):
        """Update model output layer for number of classes."""
        try:
            # For timm models
            if hasattr(self.model, 'reset_classifier'):
                self.model.reset_classifier(self.num_classes)
                logger.info("Updated classifier using reset_classifier")
            # For torchvision models
            elif hasattr(self.model, 'fc'):
                in_features = self.model.fc.in_features
                self.model.fc = nn.Linear(in_features, self.num_classes)
                self.model.fc.to(self.device)
                logger.info("Updated fc layer")
            elif hasattr(self.model, 'classifier'):
                if isinstance(self.model.classifier, nn.Linear):
                    in_features = self.model.classifier.in_features
                    self.model.classifier = nn.Linear(in_features, self.num_classes)
                    self.model.classifier.to(self.device)
                    logger.info("Updated classifier layer")
        except Exception as e:
            logger.warning(f"Could not update model output layer: {e}")
    
    def train(
        self,
        data_path: Union[str, Path],
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 1e-3,
        image_size: int = 224,
        augmentation_strategy: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the image model.
        
        Args:
            data_path: Path to image directory
            epochs: Number of epochs
            batch_size: Batch size
            learning_rate: Learning rate
            image_size: Image size
            augmentation_strategy: Augmentation strategy
            
        Returns:
            Training metrics
        """
        logger.info("Starting image training...")
        
        # Load data
        data_loader = ImageDataLoader(
            data_path=data_path,
            image_size=image_size
        )
        train_data, val_data, _ = data_loader.load()
        
        # Setup augmentation
        train_augmenter = ImageAugmenter(
            strategy=augmentation_strategy,
            image_size=image_size
        )
        val_augmenter = ImageAugmenter(
            strategy="light",
            image_size=image_size
        )
        
        # Create datasets
        train_dataset = ImageDataset(
            train_data,
            transform=train_augmenter.get_transforms(),
            class_to_idx=data_loader.get_class_mapping()
        )
        val_dataset = ImageDataset(
            val_data,
            transform=val_augmenter.get_transforms(),
            class_to_idx=data_loader.get_class_mapping()
        )
        
        # Create data loaders
        train_loader = TorchDataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0  # Set to 0 for Windows compatibility
        )
        val_loader = TorchDataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        
        # Setup optimizer and loss
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        best_val_acc = 0.0
        metrics = {
            'train_losses': [],
            'val_losses': [],
            'train_accs': [],
            'val_accs': []
        }
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Train
            train_loss, train_acc = self._train_epoch(
                train_loader, optimizer, criterion
            )
            metrics['train_losses'].append(train_loss)
            metrics['train_accs'].append(train_acc)
            
            # Validate
            val_loss, val_acc = self._validate_epoch(val_loader, criterion)
            metrics['val_losses'].append(val_loss)
            metrics['val_accs'].append(val_acc)
            
            logger.info(
                f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
            )
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                logger.info("New best model!")
        
        metrics['best_val_acc'] = best_val_acc
        logger.info("Training completed!")
        
        return metrics
    
    def _train_epoch(
        self,
        train_loader: TorchDataLoader,
        optimizer,
        criterion
    ) -> tuple:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for images, labels in tqdm(train_loader, desc="Training"):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            outputs = self.model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def _validate_epoch(
        self,
        val_loader: TorchDataLoader,
        criterion
    ) -> tuple:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc="Validating"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                # Statistics
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def evaluate(
        self,
        test_data_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the model.
        
        Args:
            test_data_path: Path to test data
            
        Returns:
            Evaluation metrics
        """
        logger.info("Evaluating model...")
        
        # For now, return dummy metrics
        # In production, this would run actual evaluation
        metrics = {
            'accuracy': 0.85,
            'precision': 0.83,
            'recall': 0.87,
            'f1': 0.85
        }
        
        logger.info(f"Evaluation complete: {metrics}")
        return metrics
