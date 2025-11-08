"""Model quantization"""

import torch
import torch.nn as nn
from typing import Optional

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class Quantizer:
    """
    Model quantization for reduced precision inference.
    """
    
    def __init__(self):
        pass
    
    def quantize(
        self,
        model: nn.Module,
        dtype: str = "int8",
        backend: str = "fbgemm"
    ) -> nn.Module:
        """
        Quantize model to lower precision.
        
        Args:
            model: Model to quantize
            dtype: Target dtype ('int8', 'fp16')
            backend: Quantization backend ('fbgemm', 'qnnpack')
            
        Returns:
            Quantized model
        """
        logger.info(f"Quantizing model to {dtype}")
        
        if dtype == "int8":
            return self._quantize_int8(model, backend)
        elif dtype == "fp16":
            return self._quantize_fp16(model)
        else:
            logger.warning(f"Unsupported dtype: {dtype}, returning original model")
            return model
    
    def _quantize_int8(self, model: nn.Module, backend: str) -> nn.Module:
        """Quantize to INT8."""
        try:
            # Set quantization backend
            torch.backends.quantized.engine = backend
            
            # Prepare model for quantization
            model.eval()
            model.qconfig = torch.quantization.get_default_qconfig(backend)
            
            # Fuse modules if possible
            try:
                model = torch.quantization.fuse_modules(model, [['conv', 'bn', 'relu']])
            except:
                pass  # Fusion not applicable for all models
            
            # Prepare and convert
            model_prepared = torch.quantization.prepare(model)
            model_quantized = torch.quantization.convert(model_prepared)
            
            logger.info("INT8 quantization successful")
            return model_quantized
            
        except Exception as e:
            logger.warning(f"INT8 quantization failed: {e}, returning original model")
            return model
    
    def _quantize_fp16(self, model: nn.Module) -> nn.Module:
        """Quantize to FP16."""
        try:
            model = model.half()
            logger.info("FP16 quantization successful")
            return model
        except Exception as e:
            logger.warning(f"FP16 quantization failed: {e}, returning original model")
            return model
