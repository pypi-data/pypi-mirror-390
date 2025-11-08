# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-07

### Added
- Initial release of MiniLin framework
- AutoPipeline for end-to-end ML workflow
- Data analysis and quality assessment
- Automatic training strategy selection
- Data augmentation for text tasks
- Model zoo with lightweight models (DistilBERT, TinyBERT, MobileBERT)
- Model compression (quantization and pruning)
- ONNX export for deployment
- Command-line interface
- Comprehensive documentation
- Example scripts for common use cases
- Unit tests for core modules

### Supported Features
- Text classification
- Sentiment analysis
- Named Entity Recognition (NER)
- Multiple data formats (JSON, JSONL, CSV, TXT)
- Automatic hyperparameter selection
- INT8/FP16 quantization
- Model pruning
- Target device optimization (mobile, edge, cloud)

### Known Limitations
- Image and audio tasks not yet implemented
- TFLite export is placeholder
- Knowledge distillation not implemented
- FastAPI deployment not implemented
- Limited test coverage

## [Unreleased]

### Planned for v0.2.0
- Image classification support
- Few-shot learning (LoRA, Adapter)
- Advanced quantization techniques
- FastAPI deployment service
- More comprehensive examples
- Improved documentation

### Planned for v0.3.0
- Audio task support
- Knowledge distillation
- Multi-modal learning
- Web UI for model training
- Cloud training service integration
