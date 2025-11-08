"""Data loading utilities"""

import json
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Tuple
import random

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class DataLoader:
    """
    Load and prepare datasets for training.
    
    Args:
        data_path: Path to dataset
        task: Task type
        max_samples: Maximum number of samples to load
        train_split: Training split ratio
        val_split: Validation split ratio
    """
    
    def __init__(
        self,
        data_path: Union[str, Path],
        task: str,
        max_samples: Optional[int] = None,
        train_split: float = 0.8,
        val_split: float = 0.1
    ):
        self.data_path = Path(data_path)
        self.task = task
        self.max_samples = max_samples
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = 1.0 - train_split - val_split
        
        if self.test_split < 0:
            raise ValueError("train_split + val_split must be <= 1.0")
    
    def load(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Load and split dataset.
        
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        logger.info(f"Loading data from: {self.data_path}")
        
        # Load all samples
        if self.data_path.is_file():
            samples = self._load_file(self.data_path)
        else:
            samples = self._load_directory(self.data_path)
        
        # Limit samples if specified
        if self.max_samples and len(samples) > self.max_samples:
            logger.info(f"Limiting dataset to {self.max_samples} samples")
            random.shuffle(samples)
            samples = samples[:self.max_samples]
        
        # Split dataset
        train_data, val_data, test_data = self._split_data(samples)
        
        logger.info(f"Loaded {len(samples)} samples: "
                   f"train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")
        
        return train_data, val_data, test_data
    
    def _load_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from a single file."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return self._load_json(file_path)
        elif suffix == '.jsonl':
            return self._load_jsonl(file_path)
        elif suffix == '.csv':
            return self._load_csv(file_path)
        elif suffix == '.txt':
            return self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'data' in data:
                return data['data']
            elif 'examples' in data:
                return data['examples']
            else:
                return [data]
        else:
            return []
    
    def _load_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSONL file."""
        samples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    samples.append(json.loads(line))
        return samples
    
    def _load_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load CSV file."""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except ImportError:
            logger.warning("pandas not installed, using basic CSV parsing")
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
    
    def _load_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load plain text file (one sample per line)."""
        samples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                if line.strip():
                    samples.append({
                        'id': idx,
                        'text': line.strip()
                    })
        return samples
    
    def _load_directory(self, dir_path: Path) -> List[Dict[str, Any]]:
        """Load data from directory structure."""
        samples = []
        
        # Assume directory structure: data_path/class_name/files
        for class_dir in dir_path.iterdir():
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            
            for file_path in class_dir.iterdir():
                if file_path.is_file():
                    samples.append({
                        'file_path': str(file_path),
                        'label': class_name
                    })
        
        return samples
    
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
