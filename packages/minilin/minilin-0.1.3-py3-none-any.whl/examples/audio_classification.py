"""
Example: Audio Classification with MiniLin
"""

import os
from minilin import AutoPipeline


def basic_audio_classification():
    """Basic audio classification example."""
    print("=" * 60)
    print("Example 1: Basic Audio Classification")
    print("=" * 60)
    
    # Create sample audio directory structure
    create_sample_audio_data()
    
    try:
        # Create pipeline
        pipeline = AutoPipeline(
            task="audio_classification",
            data_path="./data/audio"
        )
        
        # Analyze data
        analysis = pipeline.analyze_data()
        print(f"\nData Analysis:")
        print(f"  - Samples: {analysis['num_samples']}")
        print(f"  - Classes: {analysis.get('num_classes', 'N/A')}")
        print(f"  - Strategy: {analysis['recommended_strategy']}")
        
        # Train
        print("\nTraining...")
        metrics = pipeline.train(
            epochs=10,
            batch_size=16,
            sample_rate=16000,
            max_duration=10.0
        )
        print(f"Training complete! Best val acc: {metrics.get('best_val_acc', 'N/A')}")
        
        # Deploy
        print("\nDeploying...")
        output_path = pipeline.deploy(output_path="./outputs/audio_model.onnx")
        print(f"Model deployed to: {output_path}")
        
    except Exception as e:
        print(f"\nNote: Full training requires dependencies.")
        print(f"Install with: pip install minilin[audio]")
        print(f"Error: {e}")


def audio_augmentation_example():
    """Example of audio augmentation techniques."""
    print("\n" + "=" * 60)
    print("Example 2: Audio Augmentation")
    print("=" * 60)
    
    try:
        from minilin.data import AudioAugmenter
        import numpy as np
        
        print("\nAvailable augmentation techniques:")
        print("  - Noise injection")
        print("  - Time shifting")
        print("  - Speed change")
        print("  - SpecAugment (for spectrograms)")
        
        # Create augmenter
        augmenter = AudioAugmenter(sample_rate=16000, strategy="standard")
        
        # Create dummy audio
        audio = np.random.randn(16000)  # 1 second of audio
        
        # Apply augmentation
        augmented = augmenter.augment(audio)
        
        print("\n✓ Audio augmentation applied")
        print(f"  Original shape: {audio.shape}")
        print(f"  Augmented shape: {augmented.shape}")
        
    except Exception as e:
        print(f"Error: {e}")


def speech_recognition_example():
    """Example of speech recognition task."""
    print("\n" + "=" * 60)
    print("Example 3: Speech Recognition")
    print("=" * 60)
    
    try:
        pipeline = AutoPipeline(
            task="speech_recognition",
            data_path="./data/speech",
            target_device="edge"
        )
        
        print("\nSpeech recognition pipeline created")
        print("  - Automatic speech-to-text")
        print("  - Optimized for edge devices")
        print("  - Supports multiple languages")
        
        # Train
        # pipeline.train(epochs=10)
        
        print("\n✓ Speech recognition configured")
        
    except Exception as e:
        print(f"Note: Speech recognition requires audio dependencies")
        print(f"Error: {e}")


def create_sample_audio_data():
    """Create sample audio directory structure."""
    print("\nCreating sample audio directory structure...")
    
    os.makedirs("./data/audio/music", exist_ok=True)
    os.makedirs("./data/audio/speech", exist_ok=True)
    os.makedirs("./outputs", exist_ok=True)
    
    # Create dummy audio files (just placeholders)
    for i in range(10):
        open(f"./data/audio/music/music_{i}.wav", 'a').close()
        open(f"./data/audio/speech/speech_{i}.wav", 'a').close()
    
    print("✓ Sample directory created")
    print("  Structure:")
    print("    data/audio/")
    print("      music/ (10 audio files)")
    print("      speech/ (10 audio files)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MiniLin Audio Classification Examples")
    print("=" * 60)
    
    # Run examples
    basic_audio_classification()
    # audio_augmentation_example()
    # speech_recognition_example()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nNote: Replace dummy audio files with real audio for actual training")
    print("Install dependencies: pip install minilin[audio]")
