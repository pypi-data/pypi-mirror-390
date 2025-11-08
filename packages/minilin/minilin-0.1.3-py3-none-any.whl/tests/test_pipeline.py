"""Tests for AutoPipeline"""

import pytest
import tempfile
import json
from pathlib import Path

from minilin import AutoPipeline


@pytest.fixture
def sample_data():
    """Create sample dataset."""
    data = [
        {"text": "This is positive", "label": "positive"},
        {"text": "This is negative", "label": "negative"},
    ] * 10
    return data


@pytest.fixture
def temp_data_file(sample_data):
    """Create temporary data file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        return f.name


def test_pipeline_initialization():
    """Test pipeline initialization."""
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./dummy_path"
    )
    
    assert pipeline.task == "text_classification"
    assert pipeline.target_device == "cloud"
    assert pipeline.compression_level == "medium"


def test_data_analysis(temp_data_file):
    """Test data analysis."""
    pipeline = AutoPipeline(
        task="text_classification",
        data_path=temp_data_file
    )
    
    analysis = pipeline.analyze_data()
    
    assert 'num_samples' in analysis
    assert 'recommended_strategy' in analysis
    assert 'quality_score' in analysis
    assert analysis['num_samples'] == 20


def test_strategy_selection(temp_data_file):
    """Test automatic strategy selection."""
    pipeline = AutoPipeline(
        task="text_classification",
        data_path=temp_data_file,
        max_samples=50
    )
    
    analysis = pipeline.analyze_data()
    
    # With 20 samples, should recommend few_shot_learning
    assert analysis['recommended_strategy'] == "few_shot_learning"


def test_auto_hyperparameters(temp_data_file):
    """Test automatic hyperparameter selection."""
    pipeline = AutoPipeline(
        task="text_classification",
        data_path=temp_data_file
    )
    
    pipeline.analyze_data()
    
    epochs = pipeline._auto_select_epochs()
    batch_size = pipeline._auto_select_batch_size()
    lr = pipeline._auto_select_learning_rate()
    
    assert isinstance(epochs, int)
    assert isinstance(batch_size, int)
    assert isinstance(lr, float)
    assert epochs > 0
    assert batch_size > 0
    assert lr > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
