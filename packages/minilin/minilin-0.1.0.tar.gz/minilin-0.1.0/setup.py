from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minilin",
    version="0.1.0",
    author="MiniLin Team",
    author_email="contact@minilin.ai",
    description="A universal low-resource deep learning framework - Learn More with Less",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minilin-ai/minilin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "datasets>=2.14.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "tqdm>=4.65.0",
        "pyyaml>=6.0",
        "onnx>=1.14.0",
        "onnxruntime>=1.15.0",
    ],
    extras_require={
        "vision": [
            "timm>=0.9.0",
            "torchvision>=0.15.0",
            "Pillow>=10.0.0",
        ],
        "audio": [
            "librosa>=0.10.0",
            "soundfile>=0.12.0",
        ],
        "optimization": [
            "optuna>=3.3.0",
            "peft>=0.5.0",
        ],
        "deployment": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "all": [
            "timm>=0.9.0",
            "torchvision>=0.15.0",
            "Pillow>=10.0.0",
            "librosa>=0.10.0",
            "soundfile>=0.12.0",
            "optuna>=3.3.0",
            "peft>=0.5.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "minilin=minilin.cli:main",
        ],
    },
)
