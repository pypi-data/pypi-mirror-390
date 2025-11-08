"""
FastAPI server for model deployment
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ModelServer:
    """
    FastAPI server for serving models.
    """
    
    def __init__(
        self,
        model_path: str,
        task: str = "text_classification",
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        """
        Args:
            model_path: Path to model file (ONNX or PyTorch)
            task: Task type
            host: Server host
            port: Server port
        """
        self.model_path = Path(model_path)
        self.task = task
        self.host = host
        self.port = port
        self.model = None
        self.tokenizer = None
        self.app = None
        
        self._load_model()
        self._create_app()
    
    def _load_model(self):
        """Load model for inference."""
        logger.info(f"Loading model from {self.model_path}")
        
        if self.model_path.suffix == '.onnx':
            self._load_onnx_model()
        elif self.model_path.suffix in ['.pt', '.pth']:
            self._load_pytorch_model()
        else:
            raise ValueError(f"Unsupported model format: {self.model_path.suffix}")
    
    def _load_onnx_model(self):
        """Load ONNX model."""
        try:
            import onnxruntime as ort
            
            self.model = ort.InferenceSession(str(self.model_path))
            logger.info("ONNX model loaded successfully")
            
            # Load tokenizer if available
            self._load_tokenizer()
            
        except ImportError:
            logger.error("onnxruntime not installed. Install with: pip install onnxruntime")
            raise
    
    def _load_pytorch_model(self):
        """Load PyTorch model."""
        try:
            import torch
            
            self.model = torch.load(self.model_path)
            self.model.eval()
            logger.info("PyTorch model loaded successfully")
            
            # Load tokenizer if available
            self._load_tokenizer()
            
        except ImportError:
            logger.error("torch not installed")
            raise
    
    def _load_tokenizer(self):
        """Load tokenizer if available."""
        try:
            from transformers import AutoTokenizer
            
            # Try to find tokenizer config
            tokenizer_path = self.model_path.parent / "tokenizer"
            if tokenizer_path.exists():
                self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))
            else:
                # Use default tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
            
            logger.info("Tokenizer loaded")
            
        except Exception as e:
            logger.warning(f"Could not load tokenizer: {e}")
    
    def _create_app(self):
        """Create FastAPI application."""
        try:
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            
            app = FastAPI(
                title="MiniLin Model Server",
                description="Serve MiniLin models via REST API",
                version="0.1.0"
            )
            
            # Request/Response models
            class PredictRequest(BaseModel):
                text: str
                
            class PredictResponse(BaseModel):
                prediction: str
                confidence: float
                probabilities: Optional[Dict[str, float]] = None
            
            class BatchPredictRequest(BaseModel):
                texts: List[str]
            
            class BatchPredictResponse(BaseModel):
                predictions: List[Dict[str, Any]]
            
            # Health check endpoint
            @app.get("/health")
            async def health():
                return {"status": "healthy", "model": str(self.model_path)}
            
            # Single prediction endpoint
            @app.post("/predict", response_model=PredictResponse)
            async def predict(request: PredictRequest):
                try:
                    result = self._predict_single(request.text)
                    return result
                except Exception as e:
                    logger.error(f"Prediction failed: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
            
            # Batch prediction endpoint
            @app.post("/predict/batch", response_model=BatchPredictResponse)
            async def predict_batch(request: BatchPredictRequest):
                try:
                    results = [self._predict_single(text) for text in request.texts]
                    return {"predictions": results}
                except Exception as e:
                    logger.error(f"Batch prediction failed: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
            
            # Model info endpoint
            @app.get("/info")
            async def info():
                return {
                    "model_path": str(self.model_path),
                    "task": self.task,
                    "format": self.model_path.suffix
                }
            
            self.app = app
            logger.info("FastAPI app created")
            
        except ImportError:
            logger.error("fastapi not installed. Install with: pip install fastapi uvicorn")
            raise
    
    def _predict_single(self, text: str) -> Dict[str, Any]:
        """Make prediction for single text."""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not loaded")
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='np'
        )
        
        # Predict
        if self.model_path.suffix == '.onnx':
            outputs = self.model.run(
                None,
                {
                    'input_ids': inputs['input_ids'],
                    'attention_mask': inputs['attention_mask']
                }
            )
            logits = outputs[0][0]
        else:
            import torch
            with torch.no_grad():
                inputs = {k: torch.tensor(v) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                logits = outputs.logits[0].numpy()
        
        # Process results
        import numpy as np
        probs = np.exp(logits) / np.sum(np.exp(logits))
        pred_idx = np.argmax(probs)
        
        return {
            "prediction": str(pred_idx),
            "confidence": float(probs[pred_idx]),
            "probabilities": {str(i): float(p) for i, p in enumerate(probs)}
        }
    
    def run(self):
        """Run the server."""
        try:
            import uvicorn
            
            logger.info(f"Starting server on {self.host}:{self.port}")
            uvicorn.run(self.app, host=self.host, port=self.port)
            
        except ImportError:
            logger.error("uvicorn not installed. Install with: pip install uvicorn")
            raise


def create_api_server(
    model_path: str,
    task: str = "text_classification",
    host: str = "0.0.0.0",
    port: int = 8000
) -> ModelServer:
    """
    Create and return API server.
    
    Args:
        model_path: Path to model
        task: Task type
        host: Server host
        port: Server port
        
    Returns:
        ModelServer instance
    """
    return ModelServer(model_path, task, host, port)


def serve_model(model_path: str, **kwargs):
    """
    Convenience function to serve a model.
    
    Args:
        model_path: Path to model
        **kwargs: Additional server arguments
    """
    server = create_api_server(model_path, **kwargs)
    server.run()
