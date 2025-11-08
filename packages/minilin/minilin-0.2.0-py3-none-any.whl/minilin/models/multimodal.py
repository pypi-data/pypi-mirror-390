"""
Multi-modal learning support
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, List

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class MultiModalFusion(nn.Module):
    """
    Multi-modal fusion module.
    
    Combines features from different modalities (text, image, audio).
    """
    
    def __init__(
        self,
        modalities: List[str],
        feature_dims: Dict[str, int],
        fusion_dim: int = 512,
        fusion_method: str = "concat"
    ):
        """
        Args:
            modalities: List of modality names (e.g., ['text', 'image'])
            feature_dims: Dictionary mapping modality to feature dimension
            fusion_dim: Dimension of fused features
            fusion_method: Fusion method ('concat', 'add', 'attention')
        """
        super().__init__()
        
        self.modalities = modalities
        self.feature_dims = feature_dims
        self.fusion_dim = fusion_dim
        self.fusion_method = fusion_method
        
        # Create projection layers for each modality
        self.projections = nn.ModuleDict()
        for modality in modalities:
            self.projections[modality] = nn.Linear(
                feature_dims[modality],
                fusion_dim
            )
        
        # Fusion layer
        if fusion_method == "concat":
            self.fusion_layer = nn.Linear(
                fusion_dim * len(modalities),
                fusion_dim
            )
        elif fusion_method == "attention":
            self.attention = nn.MultiheadAttention(
                embed_dim=fusion_dim,
                num_heads=8
            )
        
        logger.info(f"MultiModalFusion initialized: {modalities}, method={fusion_method}")
    
    def forward(self, features: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Fuse multi-modal features.
        
        Args:
            features: Dictionary mapping modality to feature tensor
            
        Returns:
            Fused feature tensor
        """
        # Project each modality to common dimension
        projected = []
        for modality in self.modalities:
            if modality in features:
                proj = self.projections[modality](features[modality])
                projected.append(proj)
        
        if not projected:
            raise ValueError("No valid modality features provided")
        
        # Fuse features
        if self.fusion_method == "concat":
            # Concatenate and project
            fused = torch.cat(projected, dim=-1)
            fused = self.fusion_layer(fused)
        elif self.fusion_method == "add":
            # Element-wise addition
            fused = torch.stack(projected, dim=0).sum(dim=0)
        elif self.fusion_method == "attention":
            # Attention-based fusion
            stacked = torch.stack(projected, dim=0)
            fused, _ = self.attention(stacked, stacked, stacked)
            fused = fused.mean(dim=0)
        else:
            raise ValueError(f"Unknown fusion method: {self.fusion_method}")
        
        return fused


class MultiModalModel(nn.Module):
    """
    Multi-modal classification model.
    
    Combines text, image, and audio encoders with fusion.
    """
    
    def __init__(
        self,
        text_encoder: Optional[nn.Module] = None,
        image_encoder: Optional[nn.Module] = None,
        audio_encoder: Optional[nn.Module] = None,
        num_classes: int = 10,
        fusion_dim: int = 512,
        fusion_method: str = "concat"
    ):
        """
        Args:
            text_encoder: Text encoder model
            image_encoder: Image encoder model
            audio_encoder: Audio encoder model
            num_classes: Number of output classes
            fusion_dim: Fusion dimension
            fusion_method: Fusion method
        """
        super().__init__()
        
        self.text_encoder = text_encoder
        self.image_encoder = image_encoder
        self.audio_encoder = audio_encoder
        
        # Determine available modalities and their dimensions
        modalities = []
        feature_dims = {}
        
        if text_encoder is not None:
            modalities.append('text')
            feature_dims['text'] = self._get_encoder_dim(text_encoder)
        
        if image_encoder is not None:
            modalities.append('image')
            feature_dims['image'] = self._get_encoder_dim(image_encoder)
        
        if audio_encoder is not None:
            modalities.append('audio')
            feature_dims['audio'] = self._get_encoder_dim(audio_encoder)
        
        if not modalities:
            raise ValueError("At least one encoder must be provided")
        
        # Fusion module
        self.fusion = MultiModalFusion(
            modalities=modalities,
            feature_dims=feature_dims,
            fusion_dim=fusion_dim,
            fusion_method=fusion_method
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, fusion_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(fusion_dim // 2, num_classes)
        )
        
        logger.info(f"MultiModalModel initialized with modalities: {modalities}")
    
    def forward(
        self,
        text: Optional[torch.Tensor] = None,
        image: Optional[torch.Tensor] = None,
        audio: Optional[torch.Tensor] = None,
        **kwargs
    ) -> torch.Tensor:
        """
        Forward pass through multi-modal model.
        
        Args:
            text: Text input
            image: Image input
            audio: Audio input
            
        Returns:
            Classification logits
        """
        features = {}
        
        # Extract features from each modality
        if text is not None and self.text_encoder is not None:
            text_features = self.text_encoder(text, **kwargs)
            if hasattr(text_features, 'last_hidden_state'):
                text_features = text_features.last_hidden_state[:, 0]  # CLS token
            elif hasattr(text_features, 'pooler_output'):
                text_features = text_features.pooler_output
            features['text'] = text_features
        
        if image is not None and self.image_encoder is not None:
            image_features = self.image_encoder(image)
            if isinstance(image_features, tuple):
                image_features = image_features[0]
            features['image'] = image_features
        
        if audio is not None and self.audio_encoder is not None:
            audio_features = self.audio_encoder(audio)
            if isinstance(audio_features, tuple):
                audio_features = audio_features[0]
            features['audio'] = audio_features
        
        # Fuse features
        fused = self.fusion(features)
        
        # Classify
        logits = self.classifier(fused)
        
        return logits
    
    def _get_encoder_dim(self, encoder: nn.Module) -> int:
        """Get output dimension of encoder."""
        # Try common attributes
        if hasattr(encoder, 'config') and hasattr(encoder.config, 'hidden_size'):
            return encoder.config.hidden_size
        elif hasattr(encoder, 'num_features'):
            return encoder.num_features
        elif hasattr(encoder, 'out_features'):
            return encoder.out_features
        else:
            # Default
            return 768


class CrossModalAttention(nn.Module):
    """
    Cross-modal attention mechanism.
    
    Allows one modality to attend to another.
    """
    
    def __init__(
        self,
        query_dim: int,
        key_dim: int,
        num_heads: int = 8,
        dropout: float = 0.1
    ):
        """
        Args:
            query_dim: Query dimension
            key_dim: Key/value dimension
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        
        self.attention = nn.MultiheadAttention(
            embed_dim=query_dim,
            num_heads=num_heads,
            kdim=key_dim,
            vdim=key_dim,
            dropout=dropout
        )
        
        self.norm = nn.LayerNorm(query_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply cross-modal attention.
        
        Args:
            query: Query tensor from one modality
            key: Key tensor from another modality
            value: Value tensor from another modality
            
        Returns:
            Attended features
        """
        # Apply attention
        attended, _ = self.attention(query, key, value)
        
        # Residual connection and normalization
        output = self.norm(query + self.dropout(attended))
        
        return output


def create_multimodal_model(
    text_model_name: Optional[str] = None,
    image_model_name: Optional[str] = None,
    audio_model_name: Optional[str] = None,
    num_classes: int = 10,
    **kwargs
) -> MultiModalModel:
    """
    Create a multi-modal model with specified encoders.
    
    Args:
        text_model_name: Name of text model
        image_model_name: Name of image model
        audio_model_name: Name of audio model
        num_classes: Number of classes
        **kwargs: Additional arguments
        
    Returns:
        MultiModalModel instance
    """
    text_encoder = None
    image_encoder = None
    audio_encoder = None
    
    # Load text encoder
    if text_model_name:
        try:
            from transformers import AutoModel
            text_encoder = AutoModel.from_pretrained(text_model_name)
            logger.info(f"Loaded text encoder: {text_model_name}")
        except Exception as e:
            logger.warning(f"Failed to load text encoder: {e}")
    
    # Load image encoder
    if image_model_name:
        try:
            import timm
            image_encoder = timm.create_model(image_model_name, pretrained=True, num_classes=0)
            logger.info(f"Loaded image encoder: {image_model_name}")
        except Exception as e:
            logger.warning(f"Failed to load image encoder: {e}")
    
    # Load audio encoder
    if audio_model_name:
        try:
            from transformers import AutoModel
            audio_encoder = AutoModel.from_pretrained(audio_model_name)
            logger.info(f"Loaded audio encoder: {audio_model_name}")
        except Exception as e:
            logger.warning(f"Failed to load audio encoder: {e}")
    
    # Create multi-modal model
    model = MultiModalModel(
        text_encoder=text_encoder,
        image_encoder=image_encoder,
        audio_encoder=audio_encoder,
        num_classes=num_classes,
        **kwargs
    )
    
    return model
