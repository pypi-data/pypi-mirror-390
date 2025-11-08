"""Data analysis module"""

import json
from pathlib import Path
from typing import Dict, Any, Union, List
import numpy as np
from collections import Counter

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class DataAnalyzer:
    """
    Analyze dataset characteristics and recommend strategies.
    
    Args:
        task: Task type (e.g., 'text_classification', 'ner')
    """
    
    def __init__(self, task: str):
        self.task = task
        self.supported_tasks = [
            'text_classification',
            'ner',
            'sentiment_analysis',
            'image_classification',
            'audio_classification'
        ]
        
        if task not in self.supported_tasks:
            logger.warning(f"Task '{task}' may not be fully supported yet")
    
    def analyze(self, data_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze dataset and return statistics.
        
        Args:
            data_path: Path to dataset
            
        Returns:
            Dictionary containing analysis results
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data path not found: {data_path}")
        
        logger.info(f"Analyzing data at: {data_path}")
        
        # Determine data format and load
        if data_path.is_file():
            analysis = self._analyze_file(data_path)
        else:
            analysis = self._analyze_directory(data_path)
        
        # Add quality score
        analysis['quality_score'] = self._calculate_quality_score(analysis)
        
        # Add recommended strategy
        num_samples = analysis.get('num_samples', 0)
        if num_samples < 100:
            strategy = "few_shot_learning"
        elif num_samples < 1000:
            strategy = "data_augmentation_transfer"
        else:
            strategy = "standard_training"
        analysis['recommended_strategy'] = strategy
        
        logger.info(f"Analysis complete: {analysis['num_samples']} samples, "
                   f"quality score: {analysis['quality_score']:.2f}")
        
        return analysis
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single data file."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return self._analyze_json(file_path)
        elif suffix == '.jsonl':
            return self._analyze_jsonl(file_path)
        elif suffix == '.csv':
            return self._analyze_csv(file_path)
        elif suffix == '.txt':
            return self._analyze_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _analyze_json(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            samples = data
        elif isinstance(data, dict) and 'data' in data:
            samples = data['data']
        else:
            samples = [data]
        
        return self._analyze_samples(samples)
    
    def _analyze_jsonl(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JSONL file."""
        samples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    samples.append(json.loads(line))
        
        return self._analyze_samples(samples)
    
    def _analyze_csv(self, file_path: Path) -> Dict[str, Any]:
        """Analyze CSV file."""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            samples = df.to_dict('records')
            return self._analyze_samples(samples)
        except ImportError:
            logger.warning("pandas not installed, using basic CSV parsing")
            # Basic CSV parsing without pandas
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                samples = list(reader)
            return self._analyze_samples(samples)
    
    def _analyze_txt(self, file_path: Path) -> Dict[str, Any]:
        """Analyze plain text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        return {
            'num_samples': len(lines),
            'avg_length': np.mean([len(line) for line in lines]),
            'min_length': min(len(line) for line in lines) if lines else 0,
            'max_length': max(len(line) for line in lines) if lines else 0,
            'format': 'txt'
        }
    
    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze directory structure (for image/audio datasets)."""
        # Count files by extension
        file_counts = Counter()
        total_size = 0
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                file_counts[file_path.suffix.lower()] += 1
                total_size += file_path.stat().st_size
        
        num_samples = sum(file_counts.values())
        
        return {
            'num_samples': num_samples,
            'file_types': dict(file_counts),
            'total_size_mb': total_size / (1024 * 1024),
            'format': 'directory'
        }
    
    def _analyze_samples(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze list of samples."""
        num_samples = len(samples)
        
        if num_samples == 0:
            return {'num_samples': 0, 'format': 'empty'}
        
        # Detect text field
        text_field = self._detect_text_field(samples[0])
        label_field = self._detect_label_field(samples[0])
        
        analysis = {
            'num_samples': num_samples,
            'text_field': text_field,
            'label_field': label_field,
            'format': 'structured'
        }
        
        # Analyze text lengths if text field exists
        if text_field and text_field in samples[0]:
            lengths = [len(str(s.get(text_field, ''))) for s in samples]
            analysis.update({
                'avg_length': np.mean(lengths),
                'min_length': min(lengths),
                'max_length': max(lengths),
                'std_length': np.std(lengths)
            })
        
        # Analyze label distribution
        if label_field and label_field in samples[0]:
            labels = [s.get(label_field) for s in samples]
            label_counts = Counter(labels)
            analysis.update({
                'num_classes': len(label_counts),
                'label_distribution': dict(label_counts),
                'is_balanced': self._check_balance(label_counts)
            })
        
        return analysis
    
    def _detect_text_field(self, sample: Dict[str, Any]) -> str:
        """Detect which field contains text data."""
        text_candidates = ['text', 'sentence', 'content', 'input', 'question']
        
        for field in text_candidates:
            if field in sample:
                return field
        
        # Return first string field
        for key, value in sample.items():
            if isinstance(value, str) and len(value) > 10:
                return key
        
        return 'text'
    
    def _detect_label_field(self, sample: Dict[str, Any]) -> str:
        """Detect which field contains labels."""
        label_candidates = ['label', 'labels', 'class', 'category', 'target']
        
        for field in label_candidates:
            if field in sample:
                return field
        
        return 'label'
    
    def _check_balance(self, label_counts: Counter) -> bool:
        """Check if dataset is balanced."""
        if not label_counts:
            return True
        
        counts = list(label_counts.values())
        max_count = max(counts)
        min_count = min(counts)
        
        # Consider balanced if ratio < 2
        return (max_count / min_count) < 2.0
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall data quality score (0-1).
        
        Factors:
        - Sample size
        - Label balance
        - Text length consistency
        """
        score = 0.0
        
        # Sample size score (0-0.4)
        num_samples = analysis.get('num_samples', 0)
        if num_samples >= 10000:
            score += 0.4
        elif num_samples >= 1000:
            score += 0.3
        elif num_samples >= 100:
            score += 0.2
        else:
            score += 0.1
        
        # Balance score (0-0.3)
        if analysis.get('is_balanced', False):
            score += 0.3
        else:
            score += 0.15
        
        # Length consistency score (0-0.3)
        if 'std_length' in analysis and 'avg_length' in analysis:
            avg_length = analysis['avg_length']
            std_length = analysis['std_length']
            if avg_length > 0:
                cv = std_length / avg_length  # Coefficient of variation
                if cv < 0.5:
                    score += 0.3
                elif cv < 1.0:
                    score += 0.2
                else:
                    score += 0.1
        else:
            score += 0.2
        
        return min(score, 1.0)
