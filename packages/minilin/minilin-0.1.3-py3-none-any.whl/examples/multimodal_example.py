"""
Example: Multi-Modal Learning with MiniLin
"""

from minilin.models import create_multimodal_model


def text_image_multimodal():
    """Example: Text + Image multi-modal classification."""
    print("=" * 60)
    print("Example 1: Text + Image Multi-Modal")
    print("=" * 60)
    
    try:
        # Create multi-modal model
        model = create_multimodal_model(
            text_model_name="distilbert-base-uncased",
            image_model_name="mobilenetv3_small_100",
            num_classes=10,
            fusion_method="concat"
        )
        
        print("\n✓ Multi-modal model created")
        print("  - Text encoder: DistilBERT")
        print("  - Image encoder: MobileNetV3")
        print("  - Fusion method: Concatenation")
        print("  - Output classes: 10")
        
        # Model can process both text and images
        print("\nUsage:")
        print("  outputs = model(text=text_input, image=image_input)")
        
    except Exception as e:
        print(f"\nNote: Multi-modal requires both text and vision dependencies")
        print(f"Install with: pip install minilin[all]")
        print(f"Error: {e}")


def text_audio_multimodal():
    """Example: Text + Audio multi-modal classification."""
    print("\n" + "=" * 60)
    print("Example 2: Text + Audio Multi-Modal")
    print("=" * 60)
    
    try:
        # Create multi-modal model
        model = create_multimodal_model(
            text_model_name="distilbert-base-uncased",
            audio_model_name="facebook/wav2vec2-base",
            num_classes=5,
            fusion_method="attention"
        )
        
        print("\n✓ Multi-modal model created")
        print("  - Text encoder: DistilBERT")
        print("  - Audio encoder: Wav2Vec2")
        print("  - Fusion method: Attention")
        print("  - Output classes: 5")
        
    except Exception as e:
        print(f"Error: {e}")


def trimodal_example():
    """Example: Text + Image + Audio multi-modal."""
    print("\n" + "=" * 60)
    print("Example 3: Text + Image + Audio (Tri-Modal)")
    print("=" * 60)
    
    try:
        # Create tri-modal model
        model = create_multimodal_model(
            text_model_name="distilbert-base-uncased",
            image_model_name="mobilenetv3_small_100",
            audio_model_name="facebook/wav2vec2-base",
            num_classes=20,
            fusion_method="attention"
        )
        
        print("\n✓ Tri-modal model created")
        print("  - Text encoder: DistilBERT")
        print("  - Image encoder: MobileNetV3")
        print("  - Audio encoder: Wav2Vec2")
        print("  - Fusion method: Attention-based")
        print("  - Output classes: 20")
        
        print("\nUse cases:")
        print("  - Video understanding (visual + audio + captions)")
        print("  - Social media analysis (text + images)")
        print("  - Multimedia content classification")
        
    except Exception as e:
        print(f"Error: {e}")


def fusion_methods_comparison():
    """Compare different fusion methods."""
    print("\n" + "=" * 60)
    print("Example 4: Fusion Methods Comparison")
    print("=" * 60)
    
    print("\nAvailable fusion methods:")
    print("\n1. Concatenation (concat):")
    print("   - Simple and effective")
    print("   - Concatenates all modality features")
    print("   - Good for balanced modalities")
    
    print("\n2. Addition (add):")
    print("   - Element-wise addition")
    print("   - Requires same feature dimensions")
    print("   - Fast and memory-efficient")
    
    print("\n3. Attention (attention):")
    print("   - Learns importance of each modality")
    print("   - More flexible and powerful")
    print("   - Best for complex tasks")
    
    print("\nRecommendation:")
    print("  - Start with 'concat' for simplicity")
    print("  - Use 'attention' for better performance")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MiniLin Multi-Modal Learning Examples")
    print("=" * 60)
    
    # Run examples
    text_image_multimodal()
    text_audio_multimodal()
    trimodal_example()
    fusion_methods_comparison()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nMulti-modal learning combines multiple data types")
    print("for more robust and accurate predictions.")
