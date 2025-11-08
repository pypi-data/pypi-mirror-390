"""Model export for deployment"""

from pathlib import Path
from typing import Union, Optional
import torch
import torch.nn as nn

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ModelExporter:
    """
    Export models to various formats for deployment.
    
    Args:
        model: PyTorch model to export
        task: Task type
        target_device: Target deployment device
    """
    
    def __init__(self, model: nn.Module, task: str, target_device: str = "cloud"):
        self.model = model
        self.task = task
        self.target_device = target_device
    
    def export(
        self,
        output_path: Union[str, Path],
        optimize: bool = True
    ) -> str:
        """
        Export model to specified format.
        
        Args:
            output_path: Path to save exported model
            optimize: Whether to apply optimization
            
        Returns:
            Path to exported model
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine export format from extension
        suffix = output_path.suffix.lower()
        
        if suffix == '.onnx':
            return self._export_onnx(output_path, optimize)
        elif suffix == '.pt' or suffix == '.pth':
            return self._export_pytorch(output_path)
        elif suffix == '.tflite':
            return self._export_tflite(output_path)
        else:
            logger.warning(f"Unknown format {suffix}, defaulting to ONNX")
            output_path = output_path.with_suffix('.onnx')
            return self._export_onnx(output_path, optimize)
    
    def _export_onnx(self, output_path: Path, optimize: bool) -> str:
        """Export to ONNX format."""
        try:
            import onnx
            
            logger.info(f"Exporting to ONNX: {output_path}")
            
            self.model.eval()
            
            # Create dummy input based on task
            if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
                dummy_input = {
                    'input_ids': torch.randint(0, 1000, (1, 128)),
                    'attention_mask': torch.ones(1, 128, dtype=torch.long)
                }
            else:
                dummy_input = torch.randn(1, 3, 224, 224)
            
            # Export
            torch.onnx.export(
                self.model,
                dummy_input,
                str(output_path),
                export_params=True,
                opset_version=14,
                do_constant_folding=optimize,
                input_names=['input_ids', 'attention_mask'] if isinstance(dummy_input, dict) else ['input'],
                output_names=['output'],
                dynamic_axes={
                    'input_ids': {0: 'batch_size', 1: 'sequence'},
                    'attention_mask': {0: 'batch_size', 1: 'sequence'},
                    'output': {0: 'batch_size'}
                } if isinstance(dummy_input, dict) else None
            )
            
            # Verify
            onnx_model = onnx.load(str(output_path))
            onnx.checker.check_model(onnx_model)
            
            logger.info(f"ONNX export successful: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("onnx library not installed. Install with: pip install onnx")
            raise
        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            raise
    
    def _export_pytorch(self, output_path: Path) -> str:
        """Export as PyTorch model."""
        logger.info(f"Saving PyTorch model: {output_path}")
        
        try:
            torch.save(self.model.state_dict(), output_path)
            logger.info(f"PyTorch export successful: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"PyTorch export failed: {e}")
            raise
    
    def _export_tflite(self, output_path: Path) -> str:
        """Export to TensorFlow Lite format."""
        logger.warning("TFLite export not fully implemented yet")
        logger.info("Please export to ONNX first, then convert using onnx-tf and tf2onnx")
        
        # For now, export to ONNX as intermediate format
        onnx_path = output_path.with_suffix('.onnx')
        return self._export_onnx(onnx_path, optimize=True)
