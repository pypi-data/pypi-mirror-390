"""
Image data loader
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import random

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class ImageDataLoader:
    """
    Load and prepare image datasets.
    
    Supports directory structure:
    data/
      class_a/
        image1.jpg
        image2.jpg
      class_b/
        image3.jpg
    """
    
    def __init__(
        self,
        data_path: str,
        image_size: int = 224,
        train_split: float = 0.8,
        val_split: float = 0.1,
        extensions: Optional[List[str]] = None
    ):
        """
        Args:
            data_path: Path to image directory
            image_size: Target image size
            train_split: Training split ratio
            val_split: Validation split ratio
            extensions: Allowed image extensions
        """
        self.data_path = Path(data_path)
        self.image_size = image_size
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = 1.0 - train_split - val_split
        
        if extensions is None:
            self.extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        else:
            self.extensions = extensions
        
        self.class_to_idx = {}
        self.idx_to_class = {}
    
    def load(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Load and split image dataset.
        
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        logger.info(f"Loading images from: {self.data_path}")
        
        # Scan directory and collect images
        samples = self._scan_directory()
        
        if not samples:
            raise ValueError(f"No images found in {self.data_path}")
        
        # Build class mapping
        self._build_class_mapping(samples)
        
        # Split dataset
        train_data, val_data, test_data = self._split_data(samples)
        
        logger.info(
            f"Loaded {len(samples)} images: "
            f"train={len(train_data)}, val={len(val_data)}, test={len(test_data)}, "
            f"classes={len(self.class_to_idx)}"
        )
        
        return train_data, val_data, test_data
    
    def _scan_directory(self) -> List[Dict[str, Any]]:
        """Scan directory and collect image paths."""
        samples = []
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
        
        # Iterate through class directories
        for class_dir in self.data_path.iterdir():
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            
            # Collect images in this class
            for img_path in class_dir.iterdir():
                if img_path.suffix.lower() in self.extensions:
                    samples.append({
                        'image_path': str(img_path),
                        'label': class_name,
                        'class_dir': class_name
                    })
        
        return samples
    
    def _build_class_mapping(self, samples: List[Dict[str, Any]]):
        """Build class name to index mapping."""
        classes = sorted(set(s['label'] for s in samples))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
        self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}
        
        # Add numeric labels to samples
        for sample in samples:
            sample['label_idx'] = self.class_to_idx[sample['label']]
    
    def _split_data(
        self,
        samples: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split data into train/val/test sets."""
        # Shuffle data
        random.shuffle(samples)
        
        n = len(samples)
        train_end = int(n * self.train_split)
        val_end = train_end + int(n * self.val_split)
        
        train_data = samples[:train_end]
        val_data = samples[train_end:val_end]
        test_data = samples[val_end:]
        
        return train_data, val_data, test_data
    
    def get_class_mapping(self) -> Dict[str, int]:
        """Get class to index mapping."""
        return self.class_to_idx.copy()
    
    def get_num_classes(self) -> int:
        """Get number of classes."""
        return len(self.class_to_idx)


class ImageDataset:
    """
    PyTorch-compatible image dataset.
    """
    
    def __init__(
        self,
        samples: List[Dict[str, Any]],
        transform=None,
        class_to_idx: Optional[Dict[str, int]] = None
    ):
        """
        Args:
            samples: List of sample dictionaries
            transform: Image transformation pipeline
            class_to_idx: Class to index mapping
        """
        self.samples = samples
        self.transform = transform
        self.class_to_idx = class_to_idx or {}
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Get image and label."""
        sample = self.samples[idx]
        
        # Load image
        try:
            from PIL import Image
            image = Image.open(sample['image_path']).convert('RGB')
        except ImportError:
            raise ImportError("PIL not installed. Install with: pip install Pillow")
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = sample.get('label_idx', 0)
        
        return image, label
