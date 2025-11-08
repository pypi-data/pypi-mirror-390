"""
MiniLin Framework - Learn More with Less

A universal low-resource deep learning framework for text, image, and audio tasks.
"""

__version__ = "0.1.0"
__author__ = "MiniLin Team"
__email__ = "contact@minilin.ai"

from minilin.pipeline import AutoPipeline
from minilin.data import DataAnalyzer
from minilin.models import ModelZoo
from minilin.config import config

__all__ = [
    "AutoPipeline",
    "DataAnalyzer",
    "ModelZoo",
    "config",
]
