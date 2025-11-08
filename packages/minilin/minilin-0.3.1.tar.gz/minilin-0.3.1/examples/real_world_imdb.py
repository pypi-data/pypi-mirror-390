"""
IMDB Sentiment Analysis - Real World Example

This script demonstrates sentiment analysis on the IMDB movie review dataset
using MiniLin's low-resource training capabilities.

Usage:
    python examples/real_world_imdb.py --samples 1000 --epochs 3
"""

import argparse
import json
import os
import random
import time
from pathlib import Path

from datasets import load_dataset
from minilin import AutoPipeline


def prepare_dataset(dataset, num_samples, output_file):
    """Prepare balanced dataset."""
    print(f"📝 Preparing dataset with {num_samples} samples...")
    
    # Get equal number of positive and negative samples
    train_data = list(dataset['train'])
    pos_samples = [item for item in train_data if item['label'] == 1]
    neg_samples = [item for item in train_data if item['label'] == 0]
    
    # Sample equally
    samples_per_class = num_samples // 2
    pos_selected = random.sample(pos_samples, samples_per_class)
    neg_selected = random.sample(neg_samples, samples_per_class)
    
    # Combine and format
    all_samples = pos_selected + neg_selected
    random.shuffle(all_samples)
    
    # Convert to MiniLin format
    formatted_data = [
        {
            "text": item["text"],
            "label": item["label"]
        }
        for item in all_samples
    ]
    
    # Save
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Dataset saved to: {output_file}")
    return len(formatted_data)


def main():
    parser = argparse.ArgumentParser(description="IMDB Sentiment Analysis with MiniLin")
    parser.add_argument("--samples", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--output-dir", type=str, default="./imdb_output", help="Output directory")
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎬 IMDB Sentiment Analysis with MiniLin")
    print("=" * 70)
    
    # Load dataset
    print("\n📥 Loading IMDB dataset from Hugging Face...")
    dataset = load_dataset("imdb")
    print(f"✓ Dataset loaded: {len(dataset['train'])} training samples")
    
    # Prepare data
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_file = output_dir / "train.json"
    num_samples = prepare_dataset(dataset, args.samples, train_file)
    
    # Create pipeline
    print(f"\n🚀 Creating MiniLin pipeline...")
    pipeline = AutoPipeline(
        task="text_classification",
        data_path=str(train_file),
        target_device="cloud",
        compression_level="medium"
    )
    
    # Analyze data
    print("\n📊 Analyzing data...")
    analysis = pipeline.analyze_data()
    print(f"  • Samples: {analysis['num_samples']}")
    print(f"  • Quality Score: {analysis['quality_score']:.2f}")
    print(f"  • Recommended Strategy: {analysis['recommended_strategy']}")
    
    # Train
    print(f"\n⏳ Training model...")
    print(f"  • Epochs: {args.epochs}")
    print(f"  • Batch Size: {args.batch_size}")
    print(f"  • Samples: {num_samples}")
    
    start_time = time.time()
    
    metrics = pipeline.train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=2e-5
    )
    
    train_time = time.time() - start_time
    
    print(f"\n✅ Training completed in {train_time:.1f} seconds!")
    print(f"\n📈 Training Metrics:")
    print(f"  • Final train loss: {metrics['train_losses'][-1]:.4f}")
    print(f"  • Final val loss: {metrics['val_losses'][-1]:.4f}")
    print(f"  • Best val loss: {metrics['best_val_loss']:.4f}")
    
    # Evaluate
    print(f"\n🎯 Evaluating model...")
    eval_metrics = pipeline.evaluate()
    print(f"  • Accuracy:  {eval_metrics['accuracy']:.4f}")
    print(f"  • Precision: {eval_metrics['precision']:.4f}")
    print(f"  • Recall:    {eval_metrics['recall']:.4f}")
    print(f"  • F1 Score:  {eval_metrics['f1']:.4f}")
    
    # Deploy
    model_path = output_dir / "sentiment_model.onnx"
    print(f"\n📦 Deploying model to: {model_path}")
    pipeline.deploy(output_path=str(model_path))
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Model deployed successfully!")
        print(f"  • Size: {size_mb:.2f} MB")
    
    # Test on sample reviews
    print(f"\n🎬 Testing on sample reviews...")
    test_reviews = [
        "This movie was absolutely fantastic! The acting was superb.",
        "Terrible waste of time. Poor acting and weak storyline.",
        "One of the best films I've seen this year!",
        "Disappointing. Expected much more from this director."
    ]
    
    print("\nSample predictions (simulated):")
    for i, review in enumerate(test_reviews, 1):
        # Simple heuristic for demo
        positive_words = ['fantastic', 'superb', 'best', 'amazing']
        negative_words = ['terrible', 'poor', 'disappointing', 'waste']
        
        review_lower = review.lower()
        is_positive = any(word in review_lower for word in positive_words)
        is_negative = any(word in review_lower for word in negative_words)
        
        sentiment = "Positive 😊" if is_positive and not is_negative else "Negative 😞"
        
        print(f"\n{i}. {review[:60]}...")
        print(f"   → {sentiment}")
    
    print("\n" + "=" * 70)
    print("✅ Experiment completed successfully!")
    print("=" * 70)
    print(f"\nResults saved to: {output_dir}")
    print(f"  • Training data: {train_file}")
    print(f"  • Model: {model_path}")
    print(f"\n💡 Try different sample sizes:")
    print(f"  python {__file__} --samples 200   # Few-shot learning")
    print(f"  python {__file__} --samples 1000  # Low-resource")
    print(f"  python {__file__} --samples 5000  # Standard")


if __name__ == "__main__":
    main()
