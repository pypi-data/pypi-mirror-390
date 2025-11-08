"""
Audio data augmentation
"""

import numpy as np
import random
from typing import Optional

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class AudioAugmenter:
    """
    Audio augmentation for speech and audio classification tasks.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        strategy: str = "standard"
    ):
        """
        Args:
            sample_rate: Audio sample rate
            strategy: Augmentation strategy ('light', 'standard', 'aggressive')
        """
        self.sample_rate = sample_rate
        self.strategy = strategy
        
        # Set augmentation probabilities based on strategy
        if strategy == "light":
            self.noise_prob = 0.2
            self.shift_prob = 0.2
            self.speed_prob = 0.1
        elif strategy == "standard":
            self.noise_prob = 0.4
            self.shift_prob = 0.4
            self.speed_prob = 0.3
        else:  # aggressive
            self.noise_prob = 0.6
            self.shift_prob = 0.6
            self.speed_prob = 0.5
        
        logger.info(f"AudioAugmenter initialized with {strategy} strategy")
    
    def augment(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply augmentation to audio.
        
        Args:
            audio: Audio array
            
        Returns:
            Augmented audio
        """
        # Add noise
        if random.random() < self.noise_prob:
            audio = self._add_noise(audio)
        
        # Time shift
        if random.random() < self.shift_prob:
            audio = self._time_shift(audio)
        
        # Speed change
        if random.random() < self.speed_prob:
            audio = self._change_speed(audio)
        
        return audio
    
    def _add_noise(self, audio: np.ndarray, noise_factor: float = 0.005) -> np.ndarray:
        """Add random noise to audio."""
        noise = np.random.randn(len(audio))
        augmented = audio + noise_factor * noise
        return augmented.astype(audio.dtype)
    
    def _time_shift(self, audio: np.ndarray, shift_max: float = 0.2) -> np.ndarray:
        """Shift audio in time."""
        shift = int(random.uniform(-shift_max, shift_max) * len(audio))
        return np.roll(audio, shift)
    
    def _change_speed(self, audio: np.ndarray, speed_range: tuple = (0.9, 1.1)) -> np.ndarray:
        """Change audio speed."""
        try:
            import librosa
            
            speed_factor = random.uniform(*speed_range)
            augmented = librosa.effects.time_stretch(audio, rate=speed_factor)
            
            # Pad or truncate to original length
            if len(augmented) < len(audio):
                augmented = np.pad(augmented, (0, len(audio) - len(augmented)))
            else:
                augmented = augmented[:len(audio)]
            
            return augmented
            
        except ImportError:
            logger.warning("librosa not installed, skipping speed change")
            return audio
        except Exception as e:
            logger.warning(f"Speed change failed: {e}")
            return audio
    
    def spec_augment(
        self,
        spectrogram: np.ndarray,
        freq_mask_param: int = 15,
        time_mask_param: int = 35,
        num_masks: int = 2
    ) -> np.ndarray:
        """
        Apply SpecAugment to spectrogram.
        
        Args:
            spectrogram: Spectrogram array (freq, time)
            freq_mask_param: Maximum frequency mask size
            time_mask_param: Maximum time mask size
            num_masks: Number of masks to apply
            
        Returns:
            Augmented spectrogram
        """
        aug_spec = spectrogram.copy()
        
        for _ in range(num_masks):
            # Frequency masking
            f = random.randint(0, freq_mask_param)
            f0 = random.randint(0, aug_spec.shape[0] - f)
            aug_spec[f0:f0+f, :] = 0
            
            # Time masking
            t = random.randint(0, time_mask_param)
            t0 = random.randint(0, aug_spec.shape[1] - t)
            aug_spec[:, t0:t0+t] = 0
        
        return aug_spec


class MelSpectrogramTransform:
    """
    Transform audio to mel spectrogram.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        n_mels: int = 128,
        n_fft: int = 2048,
        hop_length: int = 512
    ):
        """
        Args:
            sample_rate: Audio sample rate
            n_mels: Number of mel bands
            n_fft: FFT window size
            hop_length: Hop length
        """
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    def __call__(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert audio to mel spectrogram.
        
        Args:
            audio: Audio array
            
        Returns:
            Mel spectrogram
        """
        try:
            import librosa
            
            # Compute mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=self.sample_rate,
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            # Convert to log scale
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            return log_mel_spec
            
        except ImportError:
            raise ImportError("librosa not installed. Install with: pip install librosa")


def get_audio_augmenter(strategy: str = "standard", **kwargs):
    """
    Get audio augmenter based on strategy.
    
    Args:
        strategy: Augmentation strategy
        **kwargs: Additional arguments
        
    Returns:
        Audio augmenter
    """
    return AudioAugmenter(strategy=strategy, **kwargs)
