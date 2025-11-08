# MiniLin 框架

**用更少，学更多** - 通用低资源深度学习框架

[English](README.md) | [中文](README_cn.md) | [Русский](README_ru.md) | [Français](README_fr.md) | [العربية](README_ar.md)

[![Python 版本](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![版本](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/alltobebetter/minilin)

## 什么是 MiniLin？

MiniLin 是一个专为**低资源场景**设计的深度学习框架，适用于数据稀缺和计算资源受限的情况。它提供了从数据到部署的端到端自动化工作流，支持文本、图像和音频任务，并针对边缘设备部署进行了优化。

### 核心特性

- **3 行代码解决方案**：从数据到部署的完整机器学习流程
- **自动策略选择**：根据数据量自动选择最优训练策略
- **轻量级模型**：预集成高效模型（DistilBERT、MobileNet、Wav2Vec2）
- **模型压缩**：量化、剪枝和知识蒸馏
- **边缘部署**：导出为 ONNX、PyTorch、TFLite
- **多模态支持**：文本、图像和音频任务
- **少样本学习**：LoRA、Adapter 和 Prompt Tuning
- **数据增强**：回译、Mixup、CutMix、SpecAugment
- **API 部署**：FastAPI REST API 服务器

## 安装

### 基础安装
```bash
pip install minilin
```

### 安装可选依赖
```bash
# 视觉任务
pip install minilin[vision]

# 音频任务
pip install minilin[audio]

# 优化功能
pip install minilin[optimization]

# 部署功能
pip install minilin[deployment]

# 安装所有功能
pip install minilin[all]
```

### 从源码安装
```bash
git clone https://github.com/alltobebetter/minilin.git
cd minilin
pip install -e .
```

## 快速开始

### 基础用法（3 行代码！）
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(task="text_classification", data_path="./data")
pipeline.train()
pipeline.deploy(output_path="./model.onnx")
```

### 高级用法
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(
    task="text_classification",
    data_path="./data",
    target_device="mobile",
    max_samples=500,
    compression_level="high"
)

analysis = pipeline.analyze_data()
print(f"推荐策略: {analysis['recommended_strategy']}")

pipeline.train(epochs=10, batch_size=16, learning_rate=2e-5)

metrics = pipeline.evaluate()
print(f"准确率: {metrics['accuracy']:.4f}")

pipeline.deploy(output_path="./model.onnx", quantization="int8")
```

## 高级功能

### 使用 LoRA 进行少样本学习
```python
from minilin.models import apply_few_shot_method

model = apply_few_shot_method(model, method="lora", r=8, alpha=16)
pipeline.train(max_samples=50, epochs=20)
```

### 知识蒸馏
```python
from minilin.optimization import KnowledgeDistiller

distiller = KnowledgeDistiller(
    teacher_model=large_model,
    student_model=small_model,
    temperature=3.0,
    alpha=0.5
)

metrics = distiller.distill(train_loader, val_loader, epochs=5)
```

### 多模态学习
```python
from minilin.models import create_multimodal_model

model = create_multimodal_model(
    text_model_name="distilbert-base-uncased",
    image_model_name="mobilenetv3_small_100",
    audio_model_name="facebook/wav2vec2-base",
    num_classes=10,
    fusion_method="attention"
)
```

### FastAPI 部署
```python
from minilin.deployment import serve_model

serve_model(
    model_path="./model.onnx",
    task="text_classification",
    host="0.0.0.0",
    port=8000
)
```

## 支持的任务

### 文本任务
- 文本分类
- 命名实体识别（NER）
- 情感分析

### 视觉任务
- 图像分类
- 图像增强（Mixup、CutMix）

### 音频任务
- 音频分类
- 音频增强（SpecAugment）

### 多模态任务
- 文本 + 图像
- 文本 + 音频
- 文本 + 图像 + 音频

## 核心模块

### 数据层
- **DataAnalyzer**：自动数据分析和质量评估
- **DataLoader**：支持 JSON、JSONL、CSV、TXT、目录格式
- **DataAugmenter**：文本增强（同义词、插入、删除、交换）
- **BackTranslator**：回译增强（googletrans、DeepL）
- **ImageAugmenter**：图像增强（Mixup、CutMix、变换）
- **AudioAugmenter**：音频增强（噪声、位移、速度、SpecAugment）

### 模型层
- **ModelZoo**：预集成轻量级模型
- **Trainer**：文本模型训练器（自动超参数调优）
- **ImageTrainer**：图像模型训练器
- **AudioTrainer**：音频模型训练器
- **MultiModalModel**：多模态融合模型
- **少样本学习**：LoRA、Adapter、Prompt Tuning

### 优化层
- **Quantizer**：INT8/FP16 量化
- **Pruner**：结构化/非结构化剪枝
- **KnowledgeDistiller**：Teacher-Student 蒸馏
- **ModelCompressor**：压缩编排

### 部署层
- **ModelExporter**：导出为 ONNX、PyTorch、TFLite
- **ModelServer**：FastAPI REST API 服务器
- **边缘优化**：移动和嵌入式设备支持

## 性能

- **训练速度**：比标准训练快 2-3 倍
- **模型大小**：压缩至原始大小的 10-20%
- **推理速度**：边缘设备上实时运行（>30 FPS）
- **准确率损失**：压缩后 <2%

## 示例

查看 [examples](examples/) 目录：

- [文本分类](examples/text_classification.py)
- [情感分析](examples/sentiment_analysis.py)
- [图像分类](examples/image_classification.py)
- [音频分类](examples/audio_classification.py)
- [多模态学习](examples/multimodal_example.py)
- [高级功能](examples/advanced_features.py)

## 配置

### 配置文件
创建 `~/.minilin/config.json`：
```json
{
  "translation_api_key": "your-api-key",
  "huggingface_token": "your-token",
  "cache_dir": "~/.minilin/cache"
}
```

### 环境变量
```bash
export MINILIN_TRANSLATION_API_KEY="your-api-key"
export MINILIN_HUGGINGFACE_TOKEN="your-token"
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- **GitHub**: https://github.com/alltobebetter/minilin
- **邮箱**: me@supage.eu.org

---

由 MiniLin 团队用 ❤️ 制作
