"""
Audio data loader
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import random
import numpy as np

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class AudioDataLoader:
    """
    Load and prepare audio datasets.
    
    Supports directory structure:
    data/
      class_a/
        audio1.wav
        audio2.wav
      class_b/
        audio3.wav
    """
    
    def __init__(
        self,
        data_path: str,
        sample_rate: int = 16000,
        max_duration: float = 10.0,
        train_split: float = 0.8,
        val_split: float = 0.1,
        extensions: Optional[List[str]] = None
    ):
        """
        Args:
            data_path: Path to audio directory
            sample_rate: Target sample rate
            max_duration: Maximum audio duration in seconds
            train_split: Training split ratio
            val_split: Validation split ratio
            extensions: Allowed audio extensions
        """
        self.data_path = Path(data_path)
        self.sample_rate = sample_rate
        self.max_duration = max_duration
        self.max_length = int(sample_rate * max_duration)
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = 1.0 - train_split - val_split
        
        if extensions is None:
            self.extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        else:
            self.extensions = extensions
        
        self.class_to_idx = {}
        self.idx_to_class = {}
    
    def load(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Load and split audio dataset.
        
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        logger.info(f"Loading audio from: {self.data_path}")
        
        # Scan directory and collect audio files
        samples = self._scan_directory()
        
        if not samples:
            raise ValueError(f"No audio files found in {self.data_path}")
        
        # Build class mapping
        self._build_class_mapping(samples)
        
        # Split dataset
        train_data, val_data, test_data = self._split_data(samples)
        
        logger.info(
            f"Loaded {len(samples)} audio files: "
            f"train={len(train_data)}, val={len(val_data)}, test={len(test_data)}, "
            f"classes={len(self.class_to_idx)}"
        )
        
        return train_data, val_data, test_data
    
    def _scan_directory(self) -> List[Dict[str, Any]]:
        """Scan directory and collect audio paths."""
        samples = []
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
        
        # Iterate through class directories
        for class_dir in self.data_path.iterdir():
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            
            # Collect audio files in this class
            for audio_path in class_dir.iterdir():
                if audio_path.suffix.lower() in self.extensions:
                    samples.append({
                        'audio_path': str(audio_path),
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


class AudioDataset:
    """
    PyTorch-compatible audio dataset.
    """
    
    def __init__(
        self,
        samples: List[Dict[str, Any]],
        sample_rate: int = 16000,
        max_length: int = 160000,
        transform=None,
        class_to_idx: Optional[Dict[str, int]] = None
    ):
        """
        Args:
            samples: List of sample dictionaries
            sample_rate: Target sample rate
            max_length: Maximum audio length in samples
            transform: Audio transformation pipeline
            class_to_idx: Class to index mapping
        """
        self.samples = samples
        self.sample_rate = sample_rate
        self.max_length = max_length
        self.transform = transform
        self.class_to_idx = class_to_idx or {}
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Get audio and label."""
        sample = self.samples[idx]
        
        # Load audio
        audio = self._load_audio(sample['audio_path'])
        
        # Apply transforms
        if self.transform:
            audio = self.transform(audio)
        
        # Get label
        label = sample.get('label_idx', 0)
        
        return audio, label
    
    def _load_audio(self, audio_path: str) -> np.ndarray:
        """Load and preprocess audio file."""
        try:
            import librosa
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Pad or truncate to max_length
            if len(audio) < self.max_length:
                # Pad with zeros
                audio = np.pad(audio, (0, self.max_length - len(audio)))
            else:
                # Truncate
                audio = audio[:self.max_length]
            
            return audio
            
        except ImportError:
            raise ImportError("librosa not installed. Install with: pip install librosa")
        except Exception as e:
            logger.error(f"Failed to load audio {audio_path}: {e}")
            # Return zeros as fallback
            return np.zeros(self.max_length, dtype=np.float32)
