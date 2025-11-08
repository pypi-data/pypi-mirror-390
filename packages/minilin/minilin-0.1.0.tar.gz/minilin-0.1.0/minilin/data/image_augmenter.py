"""
Image data augmentation
"""

from typing import Optional, Any
import random

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ImageAugmenter:
    """
    Image augmentation for computer vision tasks.
    """
    
    def __init__(self, strategy: str = "standard", image_size: int = 224):
        """
        Args:
            strategy: Augmentation strategy ('light', 'standard', 'aggressive')
            image_size: Target image size
        """
        self.strategy = strategy
        self.image_size = image_size
        self.transforms = None
        self._init_transforms()
    
    def _init_transforms(self):
        """Initialize augmentation transforms."""
        try:
            from torchvision import transforms
            
            # Base transforms
            base_transforms = [
                transforms.Resize((self.image_size, self.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ]
            
            # Augmentation based on strategy
            if self.strategy == "light":
                aug_transforms = [
                    transforms.RandomHorizontalFlip(p=0.3),
                ]
            elif self.strategy == "standard":
                aug_transforms = [
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.RandomRotation(15),
                    transforms.ColorJitter(
                        brightness=0.2,
                        contrast=0.2,
                        saturation=0.2
                    ),
                ]
            else:  # aggressive
                aug_transforms = [
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.RandomRotation(30),
                    transforms.ColorJitter(
                        brightness=0.3,
                        contrast=0.3,
                        saturation=0.3,
                        hue=0.1
                    ),
                    transforms.RandomAffine(
                        degrees=0,
                        translate=(0.1, 0.1),
                        scale=(0.9, 1.1)
                    ),
                ]
            
            # Combine transforms
            self.transforms = transforms.Compose(aug_transforms + base_transforms)
            
            logger.info(f"Image augmentation initialized: {self.strategy} strategy")
            
        except ImportError:
            logger.error("torchvision not installed. Install with: pip install torchvision")
            raise
    
    def __call__(self, image):
        """Apply transforms to image."""
        if self.transforms is None:
            raise RuntimeError("Transforms not initialized")
        return self.transforms(image)
    
    def get_transforms(self):
        """Get the transform pipeline."""
        return self.transforms


class MixupAugmenter:
    """
    Mixup augmentation for images.
    
    Mixes two images and their labels.
    """
    
    def __init__(self, alpha: float = 0.2):
        """
        Args:
            alpha: Mixup interpolation strength
        """
        self.alpha = alpha
    
    def __call__(self, images, labels):
        """
        Apply mixup augmentation.
        
        Args:
            images: Batch of images
            labels: Batch of labels
            
        Returns:
            Mixed images and labels
        """
        try:
            import torch
            
            batch_size = images.size(0)
            
            # Sample lambda from beta distribution
            if self.alpha > 0:
                lam = torch.distributions.Beta(self.alpha, self.alpha).sample()
            else:
                lam = 1.0
            
            # Random permutation
            index = torch.randperm(batch_size)
            
            # Mix images
            mixed_images = lam * images + (1 - lam) * images[index]
            
            # Mix labels
            labels_a = labels
            labels_b = labels[index]
            
            return mixed_images, labels_a, labels_b, lam
            
        except ImportError:
            logger.error("torch not installed")
            raise


class CutMixAugmenter:
    """
    CutMix augmentation for images.
    
    Cuts and pastes patches between images.
    """
    
    def __init__(self, alpha: float = 1.0):
        """
        Args:
            alpha: CutMix interpolation strength
        """
        self.alpha = alpha
    
    def __call__(self, images, labels):
        """
        Apply CutMix augmentation.
        
        Args:
            images: Batch of images
            labels: Batch of labels
            
        Returns:
            Mixed images and labels
        """
        try:
            import torch
            
            batch_size = images.size(0)
            _, _, h, w = images.size()
            
            # Sample lambda
            if self.alpha > 0:
                lam = torch.distributions.Beta(self.alpha, self.alpha).sample()
            else:
                lam = 1.0
            
            # Random permutation
            index = torch.randperm(batch_size)
            
            # Generate random box
            cut_ratio = torch.sqrt(1.0 - lam)
            cut_w = (w * cut_ratio).int()
            cut_h = (h * cut_ratio).int()
            
            cx = torch.randint(w, (1,)).item()
            cy = torch.randint(h, (1,)).item()
            
            x1 = max(0, cx - cut_w // 2)
            y1 = max(0, cy - cut_h // 2)
            x2 = min(w, cx + cut_w // 2)
            y2 = min(h, cy + cut_h // 2)
            
            # Apply CutMix
            mixed_images = images.clone()
            mixed_images[:, :, y1:y2, x1:x2] = images[index, :, y1:y2, x1:x2]
            
            # Adjust lambda
            lam = 1 - ((x2 - x1) * (y2 - y1) / (w * h))
            
            labels_a = labels
            labels_b = labels[index]
            
            return mixed_images, labels_a, labels_b, lam
            
        except ImportError:
            logger.error("torch not installed")
            raise


def get_image_augmenter(strategy: str = "standard", **kwargs):
    """
    Get image augmenter based on strategy.
    
    Args:
        strategy: Augmentation strategy
        **kwargs: Additional arguments
        
    Returns:
        Image augmenter
    """
    return ImageAugmenter(strategy=strategy, **kwargs)
