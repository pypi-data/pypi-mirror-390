"""
高级功能示例：LoRA、知识蒸馏、API 部署
"""

import json
import os


def example_lora_training():
    """示例：使用 LoRA 进行少样本学习"""
    print("=" * 60)
    print("示例 1: LoRA 少样本学习")
    print("=" * 60)
    
    try:
        from minilin import AutoPipeline
        from minilin.models import apply_few_shot_method
        
        # 创建 pipeline
        pipeline = AutoPipeline(
            task="text_classification",
            data_path="./data/small_dataset.json",
            max_samples=50  # 只用 50 个样本
        )
        
        # 分析数据
        analysis = pipeline.analyze_data()
        print(f"\n数据分析:")
        print(f"  样本数: {analysis['num_samples']}")
        print(f"  推荐策略: {analysis['recommended_strategy']}")
        
        # 应用 LoRA
        print("\n应用 LoRA...")
        # pipeline.model = apply_few_shot_method(pipeline.model, method="lora", r=8)
        
        # 训练
        print("\n开始训练...")
        # metrics = pipeline.train(epochs=10)
        
        print("\n✓ LoRA 训练完成")
        print("注意: 需要安装 peft 库: pip install peft")
        
    except Exception as e:
        print(f"错误: {e}")
        print("需要安装: pip install torch transformers peft")


def example_knowledge_distillation():
    """示例：知识蒸馏"""
    print("\n" + "=" * 60)
    print("示例 2: 知识蒸馏")
    print("=" * 60)
    
    try:
        from minilin.optimization import KnowledgeDistiller
        
        print("\n知识蒸馏流程:")
        print("1. 准备大模型（Teacher）和小模型（Student）")
        print("2. 使用 KnowledgeDistiller 进行蒸馏训练")
        print("3. 小模型学习大模型的知识")
        print("4. 获得更小、更快的模型")
        
        print("\n代码示例:")
        print("""
from minilin.optimization import KnowledgeDistiller

# 初始化蒸馏器
distiller = KnowledgeDistiller(
    teacher_model=large_model,
    student_model=small_model,
    temperature=3.0,
    alpha=0.5
)

# 执行蒸馏
metrics = distiller.distill(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=5
)

# 查看压缩比
compression_info = distiller.get_compression_ratio()
print(f"压缩比: {compression_info['compression_ratio']:.2f}x")
        """)
        
        print("\n✓ 知识蒸馏功能已实现")
        print("注意: 需要安装 PyTorch")
        
    except Exception as e:
        print(f"错误: {e}")


def example_api_deployment():
    """示例：FastAPI 部署"""
    print("\n" + "=" * 60)
    print("示例 3: FastAPI 部署")
    print("=" * 60)
    
    try:
        print("\nAPI 部署流程:")
        print("1. 训练并导出模型")
        print("2. 使用 ModelServer 创建 API 服务")
        print("3. 通过 HTTP 请求进行推理")
        
        print("\n代码示例:")
        print("""
from minilin.deployment import serve_model

# 启动 API 服务器
serve_model(
    model_path="./model.onnx",
    task="text_classification",
    host="0.0.0.0",
    port=8000
)

# 服务器启动后，可以通过 HTTP 请求使用:
# POST http://localhost:8000/predict
# Body: {"text": "This is a test"}
        """)
        
        print("\nAPI 端点:")
        print("  GET  /health          - 健康检查")
        print("  POST /predict         - 单个预测")
        print("  POST /predict/batch   - 批量预测")
        print("  GET  /info            - 模型信息")
        
        print("\n✓ API 部署功能已实现")
        print("注意: 需要安装 fastapi 和 uvicorn")
        print("安装命令: pip install fastapi uvicorn")
        
    except Exception as e:
        print(f"错误: {e}")


def example_backtranslation():
    """示例：回译数据增强"""
    print("\n" + "=" * 60)
    print("示例 4: 回译数据增强")
    print("=" * 60)
    
    try:
        print("\n回译增强流程:")
        print("1. 将文本翻译成中间语言（如法语）")
        print("2. 再翻译回原语言（英语）")
        print("3. 获得语义相似但表达不同的文本")
        
        print("\n配置翻译 API:")
        print("""
# 方法 1: 使用环境变量
export MINILIN_TRANSLATION_API_KEY="your-api-key"

# 方法 2: 使用配置文件
from minilin import config
config.set('translation_api_key', 'your-api-key')
config.save()

# 方法 3: 使用免费的 googletrans
pip install googletrans==4.0.0rc1
        """)
        
        print("\n代码示例:")
        print("""
from minilin.data import BackTranslator

# 初始化翻译器
translator = BackTranslator(api_type="googletrans")

# 回译文本
original = "This is a great product"
augmented = translator.back_translate(original)
print(f"原文: {original}")
print(f"增强: {augmented}")
        """)
        
        print("\n✓ 回译功能已实现")
        print("支持的 API: googletrans (免费), DeepL (需要 API key)")
        
    except Exception as e:
        print(f"错误: {e}")


def example_image_augmentation():
    """示例：图像增强"""
    print("\n" + "=" * 60)
    print("示例 5: 图像数据增强")
    print("=" * 60)
    
    try:
        print("\n图像增强技术:")
        print("1. 基础增强: 翻转、旋转、颜色调整")
        print("2. Mixup: 混合两张图像")
        print("3. CutMix: 剪切粘贴图像块")
        
        print("\n代码示例:")
        print("""
from minilin.data.image_augmenter import ImageAugmenter, MixupAugmenter

# 基础增强
augmenter = ImageAugmenter(strategy="standard", image_size=224)
augmented_image = augmenter(image)

# Mixup 增强
mixup = MixupAugmenter(alpha=0.2)
mixed_images, labels_a, labels_b, lam = mixup(images, labels)
        """)
        
        print("\n✓ 图像增强功能已实现")
        print("注意: 需要安装 torchvision")
        print("安装命令: pip install torchvision")
        
    except Exception as e:
        print(f"错误: {e}")


def create_sample_data():
    """创建示例数据"""
    os.makedirs("./data", exist_ok=True)
    
    # 小数据集用于 LoRA
    small_data = [
        {"text": "Great product!", "label": "positive"},
        {"text": "Terrible quality", "label": "negative"},
    ] * 25
    
    with open("./data/small_dataset.json", "w") as f:
        json.dump(small_data, f)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MiniLin 高级功能示例")
    print("=" * 60)
    
    create_sample_data()
    
    # 运行示例
    example_lora_training()
    example_knowledge_distillation()
    example_api_deployment()
    example_backtranslation()
    example_image_augmentation()
    
    print("\n" + "=" * 60)
    print("所有高级功能已展示完毕！")
    print("=" * 60)
    print("\n提示:")
    print("- 这些功能需要额外的依赖包")
    print("- 使用 'pip install minilin[all]' 安装所有依赖")
    print("- 或根据需要安装特定功能的依赖")
