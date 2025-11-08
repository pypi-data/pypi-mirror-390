"""
Example: Text Classification with MiniLin

This example demonstrates how to use MiniLin for text classification
with minimal code.
"""

from minilin import AutoPipeline

# Example 1: Basic usage (3 lines!)
def basic_example():
    print("=" * 50)
    print("Example 1: Basic Text Classification")
    print("=" * 50)
    
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/text_classification.json"
    )
    
    # Analyze data
    analysis = pipeline.analyze_data()
    print(f"\nData Analysis:")
    print(f"  - Samples: {analysis['num_samples']}")
    print(f"  - Strategy: {analysis['recommended_strategy']}")
    print(f"  - Quality Score: {analysis['quality_score']:.2f}")
    
    # Train
    print("\nTraining...")
    metrics = pipeline.train()
    print(f"Training complete! Best val loss: {metrics['best_val_loss']:.4f}")
    
    # Deploy
    print("\nDeploying...")
    output_path = pipeline.deploy(output_path="./outputs/model.onnx")
    print(f"Model deployed to: {output_path}")


# Example 2: Advanced usage with custom configuration
def advanced_example():
    print("\n" + "=" * 50)
    print("Example 2: Advanced Configuration")
    print("=" * 50)
    
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/text_classification.json",
        target_device="mobile",      # Optimize for mobile
        max_samples=500,             # Limit training samples
        compression_level="high"     # Aggressive compression
    )
    
    # Analyze
    analysis = pipeline.analyze_data()
    print(f"\nRecommended strategy: {analysis['recommended_strategy']}")
    
    # Train with custom hyperparameters
    pipeline.train(
        epochs=10,
        batch_size=16,
        learning_rate=2e-5
    )
    
    # Evaluate
    metrics = pipeline.evaluate()
    print(f"\nEvaluation Metrics:")
    print(f"  - Accuracy: {metrics['accuracy']:.4f}")
    print(f"  - F1 Score: {metrics['f1']:.4f}")
    
    # Deploy with quantization
    pipeline.deploy(
        output_path="./outputs/model_mobile.onnx",
        quantization="int8"
    )


# Example 3: Few-shot learning scenario
def few_shot_example():
    print("\n" + "=" * 50)
    print("Example 3: Few-shot Learning")
    print("=" * 50)
    
    # Simulate very small dataset
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/small_dataset.json",
        max_samples=50  # Only 50 samples!
    )
    
    analysis = pipeline.analyze_data()
    print(f"\nWith only {analysis['num_samples']} samples:")
    print(f"  - Strategy: {analysis['recommended_strategy']}")
    print(f"  - Will use aggressive data augmentation")
    
    pipeline.train(epochs=20)  # More epochs for few-shot
    pipeline.deploy(output_path="./outputs/few_shot_model.onnx")


if __name__ == "__main__":
    # Create sample data first
    import json
    import os
    
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./outputs", exist_ok=True)
    
    # Create sample dataset
    sample_data = [
        {"text": "This movie is great!", "label": "positive"},
        {"text": "I love this product", "label": "positive"},
        {"text": "Terrible experience", "label": "negative"},
        {"text": "Waste of money", "label": "negative"},
    ] * 50  # 200 samples
    
    with open("./data/text_classification.json", "w") as f:
        json.dump(sample_data, f)
    
    # Small dataset for few-shot
    with open("./data/small_dataset.json", "w") as f:
        json.dump(sample_data[:50], f)
    
    print("Sample data created!\n")
    
    # Run examples
    try:
        basic_example()
        # advanced_example()
        # few_shot_example()
    except Exception as e:
        print(f"\nNote: Full training requires dependencies.")
        print(f"Install with: pip install minilin[all]")
        print(f"Error: {e}")
