"""Command-line interface for MiniLin"""

import argparse
import sys
from pathlib import Path

from minilin import AutoPipeline
from minilin.utils import setup_logger

logger = setup_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MiniLin - Learn More with Less",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training
  minilin train --task text_classification --data ./data

  # Train with custom config
  minilin train --task text_classification --data ./data --device mobile --epochs 10

  # Analyze data only
  minilin analyze --task text_classification --data ./data

  # Deploy existing model
  minilin deploy --model ./model.pt --output ./model.onnx --quantization int8
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train a model')
    train_parser.add_argument('--task', required=True, help='Task type')
    train_parser.add_argument('--data', required=True, help='Path to training data')
    train_parser.add_argument('--device', default='cloud', choices=['mobile', 'edge', 'cloud'],
                             help='Target device')
    train_parser.add_argument('--compression', default='medium', choices=['low', 'medium', 'high'],
                             help='Compression level')
    train_parser.add_argument('--epochs', type=int, help='Number of epochs')
    train_parser.add_argument('--batch-size', type=int, help='Batch size')
    train_parser.add_argument('--lr', type=float, help='Learning rate')
    train_parser.add_argument('--output', default='./model.onnx', help='Output model path')
    train_parser.add_argument('--quantization', choices=['int8', 'fp16'], help='Quantization type')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dataset')
    analyze_parser.add_argument('--task', required=True, help='Task type')
    analyze_parser.add_argument('--data', required=True, help='Path to data')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy a trained model')
    deploy_parser.add_argument('--model', required=True, help='Path to trained model')
    deploy_parser.add_argument('--output', required=True, help='Output path')
    deploy_parser.add_argument('--quantization', choices=['int8', 'fp16'], help='Quantization type')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'train':
            train_command(args)
        elif args.command == 'analyze':
            analyze_command(args)
        elif args.command == 'deploy':
            deploy_command(args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


def train_command(args):
    """Execute train command."""
    logger.info("Starting training pipeline...")
    
    pipeline = AutoPipeline(
        task=args.task,
        data_path=args.data,
        target_device=args.device,
        compression_level=args.compression
    )
    
    # Analyze
    analysis = pipeline.analyze_data()
    logger.info(f"Data analysis: {analysis['num_samples']} samples, "
               f"strategy: {analysis['recommended_strategy']}")
    
    # Train
    train_kwargs = {}
    if args.epochs:
        train_kwargs['epochs'] = args.epochs
    if args.batch_size:
        train_kwargs['batch_size'] = args.batch_size
    if args.lr:
        train_kwargs['learning_rate'] = args.lr
    
    metrics = pipeline.train(**train_kwargs)
    logger.info(f"Training complete: {metrics}")
    
    # Deploy
    pipeline.deploy(
        output_path=args.output,
        quantization=args.quantization
    )
    
    logger.info(f"Model saved to: {args.output}")


def analyze_command(args):
    """Execute analyze command."""
    logger.info("Analyzing dataset...")
    
    pipeline = AutoPipeline(
        task=args.task,
        data_path=args.data
    )
    
    analysis = pipeline.analyze_data()
    
    print("\n" + "=" * 50)
    print("Dataset Analysis")
    print("=" * 50)
    print(f"Samples: {analysis['num_samples']}")
    print(f"Quality Score: {analysis['quality_score']:.2f}")
    print(f"Recommended Strategy: {analysis['recommended_strategy']}")
    
    if 'num_classes' in analysis:
        print(f"Number of Classes: {analysis['num_classes']}")
    if 'is_balanced' in analysis:
        print(f"Balanced: {analysis['is_balanced']}")
    
    print("=" * 50)


def deploy_command(args):
    """Execute deploy command."""
    logger.info("Deploying model...")
    logger.warning("Deploy command for existing models not fully implemented yet")
    logger.info("Please use the train command with --output flag")


if __name__ == "__main__":
    main()
