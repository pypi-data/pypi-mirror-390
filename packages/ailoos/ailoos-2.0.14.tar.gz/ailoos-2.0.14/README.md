# 🚀 Ailoos - Sovereign Decentralized AI Library

**Ailoos** is a comprehensive Python library for decentralized AI training and inference, specifically designed for training **EmpoorioLM** and other models across a global network of nodes using federated learning.

[![PyPI version](https://badge.fury.io/py/ailoos.svg)](https://pypi.org/project/ailoos/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/123456789)](https://discord.gg/ailoos)

## 🌟 Key Features

- 🤖 **Federated Learning**: FedAvg algorithm for privacy-preserving distributed training
- 🌐 **Decentralized Network**: P2P communication between training nodes
- 🧠 **EmpoorioLM Support**: Native support for sovereign AI model training
- 💻 **CLI Tools**: Command-line interface for easy node management
- 🔧 **Auto-Setup**: Intelligent environment configuration
- 📊 **Monitoring**: Built-in logging and performance metrics
- 🔒 **Privacy-First**: Zero-trust architecture, data never leaves your device
- ⚡ **Hardware Optimization**: Automatic GPU/CPU detection and optimization

## 📦 Installation

### Quick Install
```bash
pip install ailoos
```

### Development Install
```bash
git clone https://github.com/empoorio/ailoos.git
cd ailoos
pip install -e .[dev]
```

### Full Installation (with GPU support)
```bash
pip install ailoos[gpu,full]
```

## 🚀 Quick Start

### 1. Auto-Setup
```bash
ailoos setup --auto
```

### 2. Start a Training Node
```bash
ailoos node start --id my_node
```

### 3. Download and Train
```bash
ailoos models download empoorio-lm
ailoos train start --model empoorio-lm --rounds 5
```

### 4. Monitor Progress
```bash
ailoos train status
ailoos node status
```

## 💻 Python API Usage

### Basic Node Management
```python
from ailoos import Node, setup_logging

# Setup logging
logger = setup_logging()

# Create and start node
node = Node(node_id="my_training_node")
await node.start()

print(f"✅ Node active: {node.status}")
```

### Federated Training
```python
from ailoos import FederatedTrainer

# Create federated trainer
trainer = FederatedTrainer(
    model_name="empoorio-lm",
    rounds=10,
    local_epochs=3
)

# Train across network
results = await trainer.train()

print(f"🎉 Training complete! Accuracy: {results['average_accuracy']:.2f}%")
```

### Model Management
```python
from ailoos import ModelManager

# Load and use models
manager = ModelManager()
await manager.load_model("empoorio-lm")

response = await manager.infer(
    "empoorio-lm",
    "¿Cómo funciona la IA soberana?"
)
print(response)
```

## 🏗️ Architecture

```
ailoos/
├── core/                    # Core AI functionality
│   ├── node.py             # P2P node management
│   └── model_manager.py    # Model loading/inference
├── federated/              # Federated learning
│   ├── trainer.py          # FedAvg client training
│   └── aggregator.py       # Aggregation algorithms
├── utils/                  # Utilities
│   ├── hardware.py         # Hardware detection
│   └── logging.py          # Logging system
└── cli/                    # Command-line interface
    └── main.py            # CLI commands
```

## 🔒 Security & Privacy

- **Zero Data Exposure**: Training data never leaves your device
- **End-to-End Encryption**: All network communications encrypted
- **Auditable Code**: 100% open-source client code
- **Sovereign AI**: No dependency on external AI providers
- **Blockchain Integration**: Transparent governance via DracmaS

## 📊 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 16GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection
- **GPU**: NVIDIA GPU with CUDA (optional, for acceleration)

## 🌐 Network Participation

### Becoming a Training Node
1. Install Ailoos
2. Run auto-setup
3. Start your node
4. Join federated training sessions
5. Earn DracmaS tokens for contributions

### Network Benefits
- **Contribute to EmpoorioLM**: Help improve the sovereign AI model
- **Earn Rewards**: DracmaS tokens for computational contributions
- **Privacy Preserved**: Your data stays local
- **Community Governance**: Vote on model improvements

## 📚 Documentation

- [Complete API Reference](https://ailoos.dev/docs/api)
- [Federated Learning Guide](https://ailoos.dev/docs/federated)
- [Node Management](https://ailoos.dev/docs/nodes)
- [Security Architecture](https://ailoos.dev/docs/security)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Discord**: [Join our community](https://discord.gg/ailoos)
- **Issues**: [GitHub Issues](https://github.com/empoorio/ailoos/issues)
- **Documentation**: [Official Docs](https://ailoos.dev/docs)
- **Email**: dev@empoorio.com

## 🙏 Acknowledgments

- Empoorio Ecosystem for the vision
- PyTorch and Transformers communities
- Federated Learning research community
- Open-source AI community

---

**Ailoos - Democratizing AI through Sovereign, Decentralized Training** 🚀✨

*Built with ❤️ for the Empoorio Ecosystem*