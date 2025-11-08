"""Tests for data modules"""

import pytest
import tempfile
import json

from minilin.data import DataAnalyzer, DataAugmenter, DataLoader


@pytest.fixture
def sample_data():
    """Create sample dataset."""
    return [
        {"text": "Sample text 1", "label": "positive"},
        {"text": "Sample text 2", "label": "negative"},
        {"text": "Sample text 3", "label": "positive"},
    ] * 10


def test_data_analyzer(sample_data):
    """Test DataAnalyzer."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_file = f.name
    
    analyzer = DataAnalyzer(task="text_classification")
    analysis = analyzer.analyze(temp_file)
    
    assert analysis['num_samples'] == 30
    assert 'quality_score' in analysis
    assert 0 <= analysis['quality_score'] <= 1


def test_data_augmenter(sample_data):
    """Test DataAugmenter."""
    augmenter = DataAugmenter(
        task="text_classification",
        strategy="data_augmentation_transfer"
    )
    
    augmented = augmenter.augment(sample_data, num_augmented=10)
    
    assert len(augmented) >= len(sample_data)
    assert len(augmented) <= len(sample_data) + 10


def test_data_loader(sample_data):
    """Test DataLoader."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_file = f.name
    
    loader = DataLoader(
        data_path=temp_file,
        task="text_classification"
    )
    
    train, val, test = loader.load()
    
    assert len(train) + len(val) + len(test) == 30
    assert len(train) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
