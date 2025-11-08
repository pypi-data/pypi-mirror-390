"""
Example: Image Classification with MiniLin
"""

import os
from minilin import AutoPipeline


def basic_image_classification():
    """Basic image classification example."""
    print("=" * 60)
    print("Example 1: Basic Image Classification")
    print("=" * 60)
    
    # Create sample image directory structure
    create_sample_image_data()
    
    try:
        # Create pipeline
        pipeline = AutoPipeline(
            task="image_classification",
            data_path="./data/images"
        )
        
        # Analyze data
        analysis = pipeline.analyze_data()
        print(f"\nData Analysis:")
        print(f"  - Samples: {analysis['num_samples']}")
        print(f"  - Classes: {analysis.get('num_classes', 'N/A')}")
        print(f"  - Strategy: {analysis['recommended_strategy']}")
        
        # Train
        print("\nTraining...")
        metrics = pipeline.train(epochs=5, batch_size=16)
        print(f"Training complete! Best val acc: {metrics.get('best_val_acc', 'N/A')}")
        
        # Deploy
        print("\nDeploying...")
        output_path = pipeline.deploy(output_path="./outputs/image_model.onnx")
        print(f"Model deployed to: {output_path}")
        
    except Exception as e:
        print(f"\nNote: Full training requires dependencies.")
        print(f"Install with: pip install minilin[vision]")
        print(f"Error: {e}")


def advanced_image_classification():
    """Advanced image classification with custom config."""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Image Classification")
    print("=" * 60)
    
    try:
        # Create pipeline with custom config
        pipeline = AutoPipeline(
            task="image_classification",
            data_path="./data/images",
            target_device="mobile",
            compression_level="high"
        )
        
        # Train with custom parameters
        pipeline.train(
            epochs=10,
            batch_size=32,
            learning_rate=1e-3,
            image_size=224,
            augmentation_strategy="aggressive"
        )
        
        # Evaluate
        metrics = pipeline.evaluate()
        print(f"\nEvaluation Metrics:")
        print(f"  - Accuracy: {metrics['accuracy']:.4f}")
        
        # Deploy with quantization
        pipeline.deploy(
            output_path="./outputs/image_model_mobile.onnx",
            quantization="int8"
        )
        
        print("\n✓ Advanced image classification complete!")
        
    except Exception as e:
        print(f"Error: {e}")


def image_augmentation_example():
    """Example of image augmentation techniques."""
    print("\n" + "=" * 60)
    print("Example 3: Image Augmentation")
    print("=" * 60)
    
    try:
        from minilin.data import ImageAugmenter
        
        print("\nAvailable augmentation strategies:")
        print("  - light: Basic transforms (flip)")
        print("  - standard: Rotation, color jitter")
        print("  - aggressive: Heavy augmentation")
        
        # Create augmenter
        augmenter = ImageAugmenter(strategy="standard", image_size=224)
        
        print("\n✓ Image augmentation configured")
        print("  Transforms: Flip, Rotation, ColorJitter")
        
    except Exception as e:
        print(f"Error: {e}")


def create_sample_image_data():
    """Create sample image directory structure."""
    print("\nCreating sample image directory structure...")
    
    os.makedirs("./data/images/cat", exist_ok=True)
    os.makedirs("./data/images/dog", exist_ok=True)
    os.makedirs("./outputs", exist_ok=True)
    
    # Create dummy image files (just placeholders)
    for i in range(10):
        open(f"./data/images/cat/cat_{i}.jpg", 'a').close()
        open(f"./data/images/dog/dog_{i}.jpg", 'a').close()
    
    print("✓ Sample directory created")
    print("  Structure:")
    print("    data/images/")
    print("      cat/ (10 images)")
    print("      dog/ (10 images)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MiniLin Image Classification Examples")
    print("=" * 60)
    
    # Run examples
    basic_image_classification()
    # advanced_image_classification()
    # image_augmentation_example()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nNote: Replace dummy images with real images for actual training")
    print("Install dependencies: pip install minilin[vision]")
