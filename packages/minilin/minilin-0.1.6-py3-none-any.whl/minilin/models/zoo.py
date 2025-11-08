"""Model zoo with pre-integrated lightweight models"""

from typing import Optional, Dict, Any
import torch
import torch.nn as nn

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ModelZoo:
    """
    Collection of lightweight pre-trained models.
    
    Args:
        task: Task type
    """
    
    # Model registry
    TEXT_MODELS = {
        'distilbert': 'distilbert-base-uncased',
        'tinybert': 'huawei-noah/TinyBERT_General_4L_312D',
        'mobilebert': 'google/mobilebert-uncased',
    }
    
    IMAGE_MODELS = {
        'mobilenetv3': 'mobilenetv3_small_100',
        'efficientnet': 'efficientnet_lite0',
    }
    
    def __init__(self, task: str):
        self.task = task
        self.model_cache = {}
    
    def get_model(
        self,
        strategy: str = "standard_training",
        target_device: str = "cloud",
        model_name: Optional[str] = None
    ) -> nn.Module:
        """
        Get appropriate model based on task and strategy.
        
        Args:
            strategy: Training strategy
            target_device: Target deployment device
            model_name: Specific model name (auto-select if None)
            
        Returns:
            PyTorch model
        """
        if model_name is None:
            model_name = self._auto_select_model(strategy, target_device)
        
        logger.info(f"Loading model: {model_name}")
        
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            return self._load_text_model(model_name)
        elif self.task == 'image_classification':
            return self._load_image_model(model_name)
        else:
            raise ValueError(f"Unsupported task: {self.task}")
    
    def _auto_select_model(self, strategy: str, target_device: str) -> str:
        """Auto-select best model for given constraints."""
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            if target_device == "mobile":
                return 'tinybert'
            elif target_device == "edge":
                return 'mobilebert'
            else:
                return 'distilbert'
        
        elif self.task == 'image_classification':
            if target_device in ["mobile", "edge"]:
                return 'mobilenetv3'
            else:
                return 'efficientnet'
        
        return 'distilbert'  # Default
    
    def _load_text_model(self, model_name: str) -> nn.Module:
        """Load text classification model."""
        try:
            from transformers import AutoModelForSequenceClassification, AutoConfig
            
            # Get model identifier
            model_id = self.TEXT_MODELS.get(model_name, model_name)
            
            # Load config and model
            config = AutoConfig.from_pretrained(model_id)
            config.num_labels = 2  # Default binary classification
            
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id,
                config=config,
                ignore_mismatched_sizes=True
            )
            
            logger.info(f"Loaded text model: {model_id}")
            return model
            
        except ImportError:
            logger.error("transformers library not installed. Install with: pip install transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def _load_image_model(self, model_name: str) -> nn.Module:
        """Load image classification model."""
        try:
            import timm
            
            model_id = self.IMAGE_MODELS.get(model_name, model_name)
            model = timm.create_model(model_id, pretrained=True, num_classes=10)
            
            logger.info(f"Loaded image model: {model_id}")
            return model
            
        except ImportError:
            logger.error("timm library not installed. Install with: pip install timm")
            raise
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def list_models(self, task: Optional[str] = None) -> Dict[str, Any]:
        """
        List available models.
        
        Args:
            task: Filter by task type (None = all)
            
        Returns:
            Dictionary of available models
        """
        models = {}
        
        if task is None or task in ['text_classification', 'sentiment_analysis', 'ner']:
            models['text'] = self.TEXT_MODELS
        
        if task is None or task == 'image_classification':
            models['image'] = self.IMAGE_MODELS
        
        return models
