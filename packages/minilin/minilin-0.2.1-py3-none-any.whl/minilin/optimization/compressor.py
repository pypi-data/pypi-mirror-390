"""Model compression orchestrator"""

from typing import Optional
import torch
import torch.nn as nn

from minilin.optimization.quantizer import Quantizer
from minilin.optimization.pruner import Pruner
from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ModelCompressor:
    """
    Orchestrate model compression techniques.
    
    Args:
        model: PyTorch model to compress
        compression_level: Compression level ('low', 'medium', 'high')
    """
    
    def __init__(self, model: nn.Module, compression_level: str = "medium"):
        self.model = model
        self.compression_level = compression_level
        
        # Initialize compression modules
        self.quantizer = Quantizer()
        self.pruner = Pruner()
        
        logger.info(f"ModelCompressor initialized with level: {compression_level}")
    
    def compress(self, quantization: Optional[str] = None) -> nn.Module:
        """
        Apply compression to model.
        
        Args:
            quantization: Quantization type ('int8', 'fp16', None)
            
        Returns:
            Compressed model
        """
        logger.info("Starting model compression...")
        
        compressed_model = self.model
        
        # Apply pruning based on compression level
        if self.compression_level in ['medium', 'high']:
            prune_amount = 0.3 if self.compression_level == 'medium' else 0.5
            logger.info(f"Applying pruning with amount: {prune_amount}")
            compressed_model = self.pruner.prune(compressed_model, amount=prune_amount)
        
        # Apply quantization if specified
        if quantization:
            logger.info(f"Applying {quantization} quantization")
            compressed_model = self.quantizer.quantize(compressed_model, dtype=quantization)
        
        # Calculate compression ratio
        original_size = self._get_model_size(self.model)
        compressed_size = self._get_model_size(compressed_model)
        ratio = compressed_size / original_size
        
        logger.info(f"Compression complete. Size ratio: {ratio:.2%}")
        logger.info(f"Original: {original_size:.2f}MB, Compressed: {compressed_size:.2f}MB")
        
        return compressed_model
    
    def _get_model_size(self, model: nn.Module) -> float:
        """Get model size in MB."""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / (1024 ** 2)
        return size_mb
