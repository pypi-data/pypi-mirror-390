"""Model management and training modules"""

from minilin.models.zoo import ModelZoo
from minilin.models.trainer import Trainer

try:
    from minilin.models.few_shot import apply_few_shot_method, LoRAWrapper, AdapterWrapper
    from minilin.models.image_trainer import ImageTrainer
    from minilin.models.audio_trainer import AudioTrainer
    from minilin.models.multimodal import MultiModalModel, create_multimodal_model
    __all__ = [
        "ModelZoo", "Trainer", "apply_few_shot_method", "LoRAWrapper", "AdapterWrapper",
        "ImageTrainer", "AudioTrainer", "MultiModalModel", "create_multimodal_model"
    ]
except ImportError:
    __all__ = ["ModelZoo", "Trainer"]
