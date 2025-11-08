"""Data augmentation strategies"""

import random
from typing import List, Dict, Any, Optional
import numpy as np

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class DataAugmenter:
    """
    Data augmentation for low-resource scenarios.
    
    Args:
        task: Task type
        strategy: Training strategy (affects augmentation intensity)
    """
    
    def __init__(self, task: str, strategy: str = "standard_training"):
        self.task = task
        self.strategy = strategy
        
        # Set augmentation probability based on strategy
        if strategy == "few_shot_learning":
            self.aug_prob = 0.9  # Aggressive augmentation
        elif strategy == "data_augmentation_transfer":
            self.aug_prob = 0.7  # Moderate augmentation
        else:
            self.aug_prob = 0.3  # Light augmentation
        
        logger.info(f"DataAugmenter initialized for {task} with strategy {strategy}")
    
    def augment(self, samples: List[Dict[str, Any]], num_augmented: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Augment dataset.
        
        Args:
            samples: Original samples
            num_augmented: Number of augmented samples to generate (None = auto)
            
        Returns:
            Augmented samples (original + new)
        """
        if not samples:
            return samples
        
        # Auto-determine augmentation count
        if num_augmented is None:
            if self.strategy == "few_shot_learning":
                num_augmented = len(samples) * 5  # 5x augmentation
            elif self.strategy == "data_augmentation_transfer":
                num_augmented = len(samples) * 2  # 2x augmentation
            else:
                num_augmented = len(samples) // 2  # 0.5x augmentation
        
        logger.info(f"Augmenting {len(samples)} samples to generate {num_augmented} new samples")
        
        augmented = []
        for _ in range(num_augmented):
            sample = random.choice(samples)
            aug_sample = self._augment_sample(sample)
            if aug_sample:
                augmented.append(aug_sample)
        
        logger.info(f"Generated {len(augmented)} augmented samples")
        return samples + augmented
    
    def _augment_sample(self, sample: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Augment a single sample based on task type."""
        if random.random() > self.aug_prob:
            return None
        
        if self.task in ['text_classification', 'sentiment_analysis', 'ner']:
            return self._augment_text(sample)
        elif self.task == 'image_classification':
            return self._augment_image(sample)
        else:
            return None
    
    def _augment_text(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Augment text sample."""
        aug_sample = sample.copy()
        
        # Detect text field
        text_field = self._detect_text_field(sample)
        if not text_field or text_field not in sample:
            return aug_sample
        
        text = sample[text_field]
        
        # Apply random augmentation technique
        techniques = [
            self._synonym_replacement,
            self._random_insertion,
            self._random_swap,
            self._random_deletion
        ]
        
        aug_technique = random.choice(techniques)
        aug_text = aug_technique(text)
        aug_sample[text_field] = aug_text
        
        return aug_sample
    
    def _synonym_replacement(self, text: str, n: int = 2) -> str:
        """Replace n words with synonyms (simplified version)."""
        words = text.split()
        if len(words) < 3:
            return text
        
        # Simple synonym dictionary (in production, use WordNet or similar)
        synonyms = {
            'good': ['great', 'excellent', 'nice', 'fine'],
            'bad': ['poor', 'terrible', 'awful', 'horrible'],
            'big': ['large', 'huge', 'enormous', 'giant'],
            'small': ['tiny', 'little', 'mini', 'compact'],
            'happy': ['joyful', 'pleased', 'delighted', 'glad'],
            'sad': ['unhappy', 'sorrowful', 'depressed', 'gloomy']
        }
        
        for _ in range(n):
            idx = random.randint(0, len(words) - 1)
            word = words[idx].lower()
            if word in synonyms:
                words[idx] = random.choice(synonyms[word])
        
        return ' '.join(words)
    
    def _random_insertion(self, text: str, n: int = 1) -> str:
        """Insert random words."""
        words = text.split()
        if len(words) < 2:
            return text
        
        for _ in range(n):
            # Insert a random word from the text
            random_word = random.choice(words)
            random_idx = random.randint(0, len(words))
            words.insert(random_idx, random_word)
        
        return ' '.join(words)
    
    def _random_swap(self, text: str, n: int = 2) -> str:
        """Swap random words."""
        words = text.split()
        if len(words) < 2:
            return text
        
        for _ in range(n):
            idx1 = random.randint(0, len(words) - 1)
            idx2 = random.randint(0, len(words) - 1)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ' '.join(words)
    
    def _random_deletion(self, text: str, p: float = 0.1) -> str:
        """Randomly delete words with probability p."""
        words = text.split()
        if len(words) < 2:
            return text
        
        new_words = [word for word in words if random.random() > p]
        
        # Ensure at least one word remains
        if len(new_words) == 0:
            return random.choice(words)
        
        return ' '.join(new_words)
    
    def _augment_image(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Augment image sample (placeholder for future implementation)."""
        # This would use torchvision transforms or similar
        logger.warning("Image augmentation not fully implemented yet")
        return sample
    
    def _detect_text_field(self, sample: Dict[str, Any]) -> Optional[str]:
        """Detect text field in sample."""
        text_candidates = ['text', 'sentence', 'content', 'input', 'question']
        
        for field in text_candidates:
            if field in sample:
                return field
        
        # Return first string field
        for key, value in sample.items():
            if isinstance(value, str):
                return key
        
        return None
