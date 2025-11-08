"""
Example: Sentiment Analysis with MiniLin
"""

from minilin import AutoPipeline

def sentiment_analysis_example():
    """Sentiment analysis on product reviews."""
    
    print("Sentiment Analysis Example")
    print("=" * 50)
    
    # Create pipeline
    pipeline = AutoPipeline(
        task="sentiment_analysis",
        data_path="./data/reviews.json",
        target_device="edge"
    )
    
    # Analyze data
    analysis = pipeline.analyze_data()
    print(f"\nDataset Info:")
    print(f"  - Total reviews: {analysis['num_samples']}")
    print(f"  - Classes: {analysis.get('num_classes', 'N/A')}")
    print(f"  - Balanced: {analysis.get('is_balanced', 'N/A')}")
    
    # Train
    print("\nTraining sentiment model...")
    pipeline.train(epochs=5, batch_size=32)
    
    # Deploy
    print("\nDeploying for edge device...")
    pipeline.deploy(
        output_path="./outputs/sentiment_model.onnx",
        quantization="int8"
    )
    
    print("\nDone! Model ready for deployment.")


if __name__ == "__main__":
    import json
    import os
    
    # Create sample review data
    os.makedirs("./data", exist_ok=True)
    
    reviews = [
        {"text": "Amazing product! Highly recommend.", "label": "positive"},
        {"text": "Best purchase ever!", "label": "positive"},
        {"text": "Disappointed with quality", "label": "negative"},
        {"text": "Not worth the price", "label": "negative"},
        {"text": "It's okay, nothing special", "label": "neutral"},
    ] * 100
    
    with open("./data/reviews.json", "w") as f:
        json.dump(reviews, f)
    
    print("Sample review data created!\n")
    
    try:
        sentiment_analysis_example()
    except Exception as e:
        print(f"\nNote: Install dependencies with: pip install minilin[all]")
        print(f"Error: {e}")
