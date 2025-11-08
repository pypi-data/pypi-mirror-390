"""
Auto Pipeline - Main entry point for MiniLin framework
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

from minilin.data import DataAnalyzer, DataAugmenter
from minilin.models import ModelZoo, Trainer
from minilin.optimization import ModelCompressor
from minilin.deployment import ModelExporter
from minilin.utils import setup_logger, load_config

logger = setup_logger(__name__)


class AutoPipeline:
    """
    Automated end-to-end pipeline for low-resource deep learning.
    
    Args:
        task: Task type ('text_classification', 'ner', 'image_classification', etc.)
        data_path: Path to training data
        target_device: Target deployment device ('mobile', 'edge', 'cloud')
        max_samples: Maximum number of training samples to use
        compression_level: Model compression level ('low', 'medium', 'high')
        config: Optional custom configuration dictionary
    """
    
    def __init__(
        self,
        task: str,
        data_path: Union[str, Path],
        target_device: str = "cloud",
        max_samples: Optional[int] = None,
        compression_level: str = "medium",
        config: Optional[Dict[str, Any]] = None
    ):
        self.task = task
        self.data_path = Path(data_path)
        self.target_device = target_device
        self.max_samples = max_samples
        self.compression_level = compression_level
        self.config = config or {}
        
        # Initialize components
        self.data_analyzer = None
        self.data_augmenter = None
        self.model = None
        self.trainer = None
        self.compressor = None
        self.exporter = None
        
        # Analysis results
        self.data_analysis = None
        self.training_strategy = None
        
        logger.info(f"Initialized AutoPipeline for task: {task}")
        logger.info(f"Target device: {target_device}, Compression: {compression_level}")
    
    def analyze_data(self) -> Dict[str, Any]:
        """
        Analyze input data and recommend optimal strategy.
        
        Returns:
            Dictionary containing data analysis results and recommendations
        """
        logger.info("Analyzing data...")
        
        self.data_analyzer = DataAnalyzer(task=self.task)
        self.data_analysis = self.data_analyzer.analyze(self.data_path)
        
        # Determine training strategy based on data size
        num_samples = self.data_analysis.get('num_samples', 0)
        
        if num_samples < 100:
            strategy = "few_shot_learning"
            logger.info("Recommended: Few-shot Learning (Prompt Tuning)")
        elif num_samples < 1000:
            strategy = "data_augmentation_transfer"
            logger.info("Recommended: Data Augmentation + Transfer Learning")
        else:
            strategy = "standard_training"
            logger.info("Recommended: Standard Training with Lightweight Model")
        
        self.training_strategy = strategy
        self.data_analysis['recommended_strategy'] = strategy
        
        return self.data_analysis
    
    def train(
        self,
        epochs: Optional[int] = None,
        batch_size: Optional[int] = None,
        learning_rate: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the model with automatic strategy selection.
        
        Args:
            epochs: Number of training epochs (auto-selected if None)
            batch_size: Batch size (auto-selected if None)
            learning_rate: Learning rate (auto-selected if None)
            **kwargs: Additional training arguments
            
        Returns:
            Dictionary containing training metrics
        """
        # Analyze data if not done yet
        if self.data_analysis is None:
            self.analyze_data()
        
        logger.info("Starting training...")
        
        # Select model and trainer based on task
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            # Text tasks
            model_zoo = ModelZoo(task=self.task)
            self.model = model_zoo.get_model(
                strategy=self.training_strategy,
                target_device=self.target_device
            )
            
            # Setup data augmentation
            self.data_augmenter = DataAugmenter(
                task=self.task,
                strategy=self.training_strategy
            )
            
            # Initialize trainer
            from minilin.models import Trainer
            self.trainer = Trainer(
                model=self.model,
                task=self.task,
                strategy=self.training_strategy
            )
        
        elif self.task == 'image_classification':
            # Image tasks
            model_zoo = ModelZoo(task=self.task)
            self.model = model_zoo.get_model(
                strategy=self.training_strategy,
                target_device=self.target_device
            )
            
            # Initialize image trainer
            from minilin.models import ImageTrainer
            from minilin.data import ImageDataLoader
            
            # Get number of classes
            temp_loader = ImageDataLoader(data_path=data_path)
            _, _, _ = temp_loader.load()
            num_classes = temp_loader.get_num_classes()
            
            self.trainer = ImageTrainer(
                model=self.model,
                num_classes=num_classes
            )
        
        elif self.task in ['audio_classification', 'speech_recognition']:
            # Audio tasks
            model_zoo = ModelZoo(task=self.task)
            self.model = model_zoo.get_model(
                strategy=self.training_strategy,
                target_device=self.target_device
            )
            
            # Initialize audio trainer
            from minilin.models import AudioTrainer
            from minilin.data import AudioDataLoader
            
            # Get number of classes
            temp_loader = AudioDataLoader(data_path=data_path)
            _, _, _ = temp_loader.load()
            num_classes = temp_loader.get_num_classes()
            
            self.trainer = AudioTrainer(
                model=self.model,
                num_classes=num_classes
            )
        
        else:
            raise ValueError(f"Unsupported task: {self.task}")
        
        # Auto-select hyperparameters if not provided
        if epochs is None:
            epochs = self._auto_select_epochs()
        if batch_size is None:
            batch_size = self._auto_select_batch_size()
        if learning_rate is None:
            learning_rate = self._auto_select_learning_rate()
        
        logger.info(f"Training config: epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        
        # Train model
        metrics = self.trainer.train(
            data_path=self.data_path,
            augmenter=self.data_augmenter,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            max_samples=self.max_samples,
            **kwargs
        )
        
        logger.info(f"Training completed. Metrics: {metrics}")
        return metrics
    
    def evaluate(self, test_data_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Evaluate the trained model.
        
        Args:
            test_data_path: Path to test data (uses validation split if None)
            
        Returns:
            Dictionary containing evaluation metrics
        """
        if self.trainer is None:
            raise RuntimeError("Model not trained yet. Call train() first.")
        
        logger.info("Evaluating model...")
        metrics = self.trainer.evaluate(test_data_path)
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def deploy(
        self,
        output_path: Union[str, Path],
        quantization: Optional[str] = None,
        optimize: bool = True
    ) -> str:
        """
        Deploy the model for inference.
        
        Args:
            output_path: Path to save the exported model
            quantization: Quantization type ('int8', 'fp16', None)
            optimize: Whether to apply optimization
            
        Returns:
            Path to the exported model
        """
        if self.model is None:
            raise RuntimeError("Model not trained yet. Call train() first.")
        
        logger.info("Preparing model for deployment...")
        
        # Apply compression if needed
        if self.compression_level != "low" or quantization:
            self.compressor = ModelCompressor(
                model=self.model,
                compression_level=self.compression_level
            )
            self.model = self.compressor.compress(quantization=quantization)
        
        # Export model
        self.exporter = ModelExporter(
            model=self.model,
            task=self.task,
            target_device=self.target_device
        )
        
        output_path = Path(output_path)
        exported_path = self.exporter.export(
            output_path=output_path,
            optimize=optimize
        )
        
        logger.info(f"Model deployed successfully to: {exported_path}")
        return str(exported_path)
    
    def _auto_select_epochs(self) -> int:
        """Auto-select number of epochs based on data size."""
        num_samples = self.data_analysis.get('num_samples', 1000)
        
        if num_samples < 100:
            return 20
        elif num_samples < 1000:
            return 10
        else:
            return 5
    
    def _auto_select_batch_size(self) -> int:
        """Auto-select batch size based on data size and device."""
        num_samples = self.data_analysis.get('num_samples', 1000)
        
        if self.target_device == "mobile":
            return 8
        elif self.target_device == "edge":
            return 16
        else:  # cloud
            return 32 if num_samples > 1000 else 16
    
    def _auto_select_learning_rate(self) -> float:
        """Auto-select learning rate based on strategy."""
        if self.training_strategy == "few_shot_learning":
            return 1e-4
        elif self.training_strategy == "data_augmentation_transfer":
            return 2e-5
        else:
            return 3e-5
