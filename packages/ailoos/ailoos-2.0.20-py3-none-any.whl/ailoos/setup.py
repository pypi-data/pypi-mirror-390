"""
Ailoos - Decentralized AI Training Platform
Setup script for package installation and CLI entry point.
"""

from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Read README
def read_readme():
    """Read README content"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Package metadata
setup(
    name="ailoos",
    version="1.0.0",
    author="Ailoos Team",
    author_email="team@ailoos.ai",
    description="Decentralized AI Training Platform - Sovereign Federated Learning",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ailoos/ailoos",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        'gpu': ['torch[cu118]>=2.0.0'],
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
        'blockchain': [
            'web3>=6.0.0',
            'eth-account>=0.8.0',
        ],
        'all': [
            'torch[cu118]>=2.0.0',
            'web3>=6.0.0',
            'eth-account>=0.8.0',
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ailoos=ailoos.cli.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'ailoos': [
            'templates/*',
            'static/*',
            'config/*',
        ],
    },
    keywords="ai machine-learning federated-learning blockchain decentralized p2p",
    project_urls={
        "Bug Reports": "https://github.com/ailoos/ailoos/issues",
        "Source": "https://github.com/ailoos/ailoos",
        "Documentation": "https://docs.ailoos.ai",
        "Discord": "https://discord.gg/ailoos",
    },
)


class AiloosSetup:
    """Automated setup for Ailoos development environment."""

    def __init__(self):
        self.logger = setup_logging()
        self.project_root = Path(__file__).parent
        self.hardware = None

    def run_auto_setup(self) -> bool:
        """
        Run complete automated setup.

        Returns:
            True if setup successful
        """
        print("🔧 Starting Ailoos Auto-Setup...")
        print("=" * 50)

        try:
            # Step 1: Hardware detection
            if not self._check_hardware():
                return False

            # Step 2: Dependencies check
            if not self._check_dependencies():
                return False

            # Step 3: Create directories
            if not self._create_directories():
                return False

            # Step 4: Generate config files
            if not self._generate_configs():
                return False

            # Step 5: Setup complete
            self._print_success_message()
            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            print(f"❌ Setup failed: {e}")
            return False

    def _check_hardware(self) -> bool:
        """Check hardware capabilities."""
        print("\n1️⃣ Checking hardware capabilities...")

        self.hardware = get_hardware_info()

        if self.hardware['detection_status'] == 'success':
            print("✅ Hardware detection successful")
            print(f"   CPU: {self.hardware['cpu']['logical_cores']} cores")
            print(f"   RAM: {self.hardware['memory']['total_gb']} GB")

            gpu_devices = self.hardware['gpu'].get('devices', [])
            if gpu_devices:
                print(f"   GPU: {len(gpu_devices)} device(s) available")
                for gpu in gpu_devices[:2]:  # Show first 2 GPUs
                    print(f"     • {gpu['name']} ({gpu['memory_gb']}GB)")
            else:
                print("   GPU: None detected (CPU training only)")

            return True
        else:
            print(f"⚠️  Hardware detection limited: {self.hardware.get('error_message', 'Unknown error')}")
            return True  # Continue anyway

    def _check_dependencies(self) -> bool:
        """Check and install required dependencies."""
        print("\n2️⃣ Checking Python dependencies...")

        required_packages = [
            "torch",
            "aiohttp",
            "psutil",
            "numpy",
            "flask",
            "flask-cors"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                if package == "torch":
                    import torch
                    version = torch.__version__
                    cuda_available = torch.cuda.is_available()
                    print(f"✅ PyTorch {version} {'(CUDA)' if cuda_available else '(CPU)'}")
                else:
                    __import__(package.replace("-", "_"))
                    print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - MISSING")

        if missing_packages:
            print(f"\n📦 Installing {len(missing_packages)} missing packages...")
            try:
                # Install missing packages
                cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                print("💡 Try: pip install -r requirements.txt")
                return False

        return True

    def _create_directories(self) -> bool:
        """Create necessary project directories."""
        print("\n3️⃣ Creating project directories...")

        directories = [
            "models",
            "logs",
            "checkpoints",
            "data",
            "configs",
            ".ailoos"
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 {dir_name}/")

        print("✅ Directories created")
        return True

    def _generate_configs(self) -> bool:
        """Generate configuration files."""
        print("\n4️⃣ Generating configuration files...")

        # Generate main config
        config = {
            "version": "1.0.0",
            "coordinator_url": "http://localhost:5000",
            "node_id": None,  # Will be generated on first run
            "hardware": self.hardware,
            "training": {
                "default_model": "empoorio-lm",
                "default_rounds": 5,
                "batch_size": 32,
                "learning_rate": 0.001
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ailoos.log"
            }
        }

        config_path = self.project_root / ".ailoos" / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)

        print(f"   📄 {config_path}")

        # Generate environment file template
        env_template = """# Ailoos Environment Configuration
# Copy this to .env and fill in your values

# Coordinator API
AILOOS_COORDINATOR_URL=http://localhost:5000

# Node Configuration
AILOOS_NODE_ID=
AILOOS_AUTO_START=false

# Training Configuration
AILOOS_DEFAULT_MODEL=empoorio-lm
AILOOS_DEFAULT_ROUNDS=5

# Logging
AILOOS_LOG_LEVEL=INFO
AILOOS_LOG_FILE=logs/ailoos.log

# Hardware (auto-detected)
# AILOOS_CPU_CORES={cpu_cores}
# AILOOS_MEMORY_GB={memory_gb}
# AILOOS_GPU_AVAILABLE={gpu_available}
""".format(
            cpu_cores=self.hardware['cpu']['logical_cores'],
            memory_gb=self.hardware['memory']['total_gb'],
            gpu_available=len(self.hardware['gpu'].get('devices', [])) > 0
        )

        env_path = self.project_root / ".ailoos" / "env.template"
        with open(env_path, 'w') as f:
            f.write(env_template)

        print(f"   📄 {env_path}")

        print("✅ Configuration files generated")
        return True

    def _print_success_message(self):
        """Print success message with next steps."""
        print("\n" + "=" * 50)
        print("🎉 Ailoos Auto-Setup Completed!")
        print("=" * 50)

        print("\n🚀 Next Steps:")
        print("   1. Start a training node:")
        print("      ailoos node start")
        print()
        print("   2. Begin federated training:")
        print("      ailoos train start")
        print()
        print("   3. Check status anytime:")
        print("      ailoos node status")
        print()
        print("   4. Get help:")
        print("      ailoos --help")

        print("\n📚 Useful Commands:")
        print("   • ailoos hardware info    # Check your hardware")
        print("   • ailoos models list      # See available models")
        print("   • ailoos setup --help     # More setup options")

        print("\n🌐 Join the Community:")
        print("   Discord: https://discord.gg/ailoos")
        print("   Docs: https://ailoos.dev/docs")

        print("\n💡 Pro Tips:")
        print("   • Use 'ailoos node start --id my_node' for custom node names")
        print("   • Training works better with GPU acceleration")
        print("   • Check logs/ailoos.log for detailed information")

        print("\n✨ Happy training with Ailoos!")


def main():
    """Main setup entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Ailoos Setup Tool")
    parser.add_argument("--auto", action="store_true",
                       help="Run automatic setup")
    parser.add_argument("--hardware-only", action="store_true",
                       help="Only check hardware capabilities")
    parser.add_argument("--force", action="store_true",
                       help="Force reinstallation of dependencies")

    args = parser.parse_args()

    if args.hardware_only:
        print_hardware_summary()
        return

    if args.auto or len(sys.argv) == 1:
        setup = AiloosSetup()
        success = setup.run_auto_setup()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()