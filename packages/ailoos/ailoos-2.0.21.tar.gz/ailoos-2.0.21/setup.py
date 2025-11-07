"""
Setup script for Ailoos - Sovereign Decentralized AI Library
"""

from setuptools import setup, find_packages
import os

# Read README
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = """
    Ailoos - Sovereign Decentralized AI Library
    ==========================================

    Ailoos is a comprehensive library for decentralized AI training and inference,
    specifically designed for training EmpoorioLM and other models across a global
    network of nodes using federated learning.

    Key Features:
    - Federated Learning with FedAvg algorithm
    - Decentralized node management
    - EmpoorioLM model training and inference
    - Easy-to-use APIs for developers
    - VS Code integration support
    - CLI tools for quick node activation
    """

# Read requirements
def read_requirements(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name="ailoos",
    version="2.0.21",  # Fixed CLI help formatting and layout
    author="Empoorio",
    author_email="dev@empoorio.com",
    description="Sovereign Decentralized AI Library for EmpoorioLM Training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/empoorio/ailoos",
    project_urls={
        "Bug Tracker": "https://github.com/empoorio/ailoos/issues",
        "Documentation": "https://ailoos.dev/docs",
        "Source Code": "https://github.com/empoorio/ailoos",
        "Discord": "https://discord.gg/ailoos",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="ai, machine-learning, federated-learning, decentralized, blockchain, empoorio, sovereign-ai",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (lite version)
        "aiohttp>=3.8.0",
        "psutil>=5.9.0",
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "tqdm>=4.64.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "torchaudio>=2.0.0",
        ],
        "ai": [
            "transformers>=4.21.0",
            "accelerate>=0.12.0",
            "datasets>=2.4.0",
        ],
        "full": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "torchaudio>=2.0.0",
            "transformers>=4.21.0",
            "datasets>=2.4.0",
            "accelerate>=0.12.0",
            "pandas>=1.5.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "scikit-learn>=1.1.0",
        ],
        "lite": [],  # No additional dependencies for lite version
    },
    entry_points={
        "console_scripts": [
            "ailoos=ailoos.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="Proprietary - Ailoos Technologies & Empoorio Ecosystem",
    platforms=["any"],
)