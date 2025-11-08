"""
Example: Using Custom Data Formats with MiniLin
"""

from minilin import AutoPipeline
import json
import csv
import os


def json_format_example():
    """Example with JSON format."""
    print("JSON Format Example")
    print("=" * 50)
    
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/custom.json"
    )
    
    analysis = pipeline.analyze_data()
    print(f"Loaded {analysis['num_samples']} samples from JSON")


def jsonl_format_example():
    """Example with JSONL format."""
    print("\nJSONL Format Example")
    print("=" * 50)
    
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/custom.jsonl"
    )
    
    analysis = pipeline.analyze_data()
    print(f"Loaded {analysis['num_samples']} samples from JSONL")


def csv_format_example():
    """Example with CSV format."""
    print("\nCSV Format Example")
    print("=" * 50)
    
    pipeline = AutoPipeline(
        task="text_classification",
        data_path="./data/custom.csv"
    )
    
    analysis = pipeline.analyze_data()
    print(f"Loaded {analysis['num_samples']} samples from CSV")


if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)
    
    # Create sample data in different formats
    samples = [
        {"text": "Sample text 1", "label": "class_a"},
        {"text": "Sample text 2", "label": "class_b"},
        {"text": "Sample text 3", "label": "class_a"},
    ] * 20
    
    # JSON format
    with open("./data/custom.json", "w") as f:
        json.dump(samples, f, indent=2)
    
    # JSONL format
    with open("./data/custom.jsonl", "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    
    # CSV format
    with open("./data/custom.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'label'])
        writer.writeheader()
        writer.writerows(samples)
    
    print("Sample data created in multiple formats!\n")
    
    # Run examples
    json_format_example()
    jsonl_format_example()
    csv_format_example()
    
    print("\nAll formats supported!")
