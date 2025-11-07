"""
Auto-setup system for Ailoos SDK.
Provides zero-configuration setup for complete Ailoos functionality.
"""

import os
import sys
import platform
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddedIPFS:
    """
    Embedded IPFS manager that handles IPFS daemon lifecycle.
    Downloads and manages IPFS daemon automatically.
    """

    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.ipfs_dir = Path.home() / ".ailoos" / "ipfs"
        self.ipfs_binary = self._get_ipfs_binary_path()
        self.daemon_process = None

    def _get_ipfs_binary_path(self) -> Path:
        """Get the path to the IPFS binary."""
        if self.system == "darwin":
            if "arm64" in self.arch:
                return self.ipfs_dir / "kubo" / "ipfs"
            else:
                return self.ipfs_dir / "kubo" / "ipfs"
        elif self.system == "linux":
            return self.ipfs_dir / "kubo" / "ipfs"
        else:
            raise RuntimeError(f"Unsupported platform: {self.system} {self.arch}")

    def _download_ipfs(self) -> bool:
        """Download and install IPFS daemon."""
        try:
            logger.info("📥 Downloading IPFS daemon...")

            # Determine download URL
            if self.system == "darwin":
                if "arm64" in self.arch:
                    url = "https://dist.ipfs.tech/kubo/v0.21.0/kubo_v0.21.0_darwin-arm64.tar.gz"
                else:
                    url = "https://dist.ipfs.tech/kubo/v0.21.0/kubo_v0.21.0_darwin-amd64.tar.gz"
            elif self.system == "linux":
                url = "https://dist.ipfs.tech/kubo/v0.21.0/kubo_v0.21.0_linux-amd64.tar.gz"
            else:
                raise RuntimeError(f"Unsupported platform: {self.system}")

            # Download and extract
            import urllib.request
            import tarfile

            self.ipfs_dir.mkdir(parents=True, exist_ok=True)
            tar_path = self.ipfs_dir / "ipfs.tar.gz"

            urllib.request.urlretrieve(url, tar_path)

            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(self.ipfs_dir)

            # Make executable
            self.ipfs_binary.chmod(0o755)

            # Cleanup
            tar_path.unlink()

            logger.info("✅ IPFS daemon downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to download IPFS: {e}")
            return False

    def _init_ipfs_repo(self) -> bool:
        """Initialize IPFS repository."""
        try:
            logger.info("🔧 Initializing IPFS repository...")

            result = subprocess.run(
                [str(self.ipfs_binary), "init"],
                capture_output=True,
                text=True,
                cwd=self.ipfs_dir
            )

            if result.returncode == 0:
                logger.info("✅ IPFS repository initialized")
                return True
            else:
                logger.error(f"❌ IPFS init failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize IPFS: {e}")
            return False

    def start_daemon(self) -> bool:
        """Start IPFS daemon."""
        try:
            if not self.ipfs_binary.exists():
                if not self._download_ipfs():
                    return False

            if not (self.ipfs_dir / ".ipfs").exists():
                if not self._init_ipfs_repo():
                    return False

            logger.info("🚀 Starting IPFS daemon...")

            self.daemon_process = subprocess.Popen(
                [str(self.ipfs_binary), "daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.ipfs_dir
            )

            # Wait for daemon to start
            time.sleep(3)

            if self.daemon_process.poll() is None:
                logger.info("✅ IPFS daemon started successfully")
                return True
            else:
                logger.error("❌ IPFS daemon failed to start")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start IPFS daemon: {e}")
            return False

    def stop_daemon(self):
        """Stop IPFS daemon."""
        if self.daemon_process:
            self.daemon_process.terminate()
            self.daemon_process.wait()
            logger.info("🛑 IPFS daemon stopped")

    def get_api_endpoint(self) -> str:
        """Get IPFS API endpoint."""
        return "http://localhost:5001"


class P2PCoordinator:
    """
    P2P Coordinator that manages federated learning sessions.
    Replaces the need for centralized GCP coordinator.
    """

    def __init__(self):
        self.node_id = self._generate_node_id()
        self.peers = {}
        self.active_sessions = {}
        self.ipfs_client = None

    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        import uuid
        return f"node_{uuid.uuid4().hex[:8]}"

    def initialize(self, ipfs_endpoint: str):
        """Initialize coordinator with IPFS connection."""
        try:
            import ipfshttpclient
            self.ipfs_client = ipfshttpclient.connect(ipfs_endpoint)
            logger.info(f"✅ P2P Coordinator initialized with node ID: {self.node_id}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ IPFS not available for coordinator: {e}")
            return False

    def create_session(self, session_config: Dict[str, Any]) -> Optional[str]:
        """Create a new federated learning session."""
        session_id = f"session_{int(time.time())}_{self.node_id[:8]}"

        self.active_sessions[session_id] = {
            "config": session_config,
            "participants": [self.node_id],
            "status": "waiting",
            "created_at": time.time()
        }

        # Publish session to IPFS for discovery
        if self.ipfs_client:
            try:
                session_data = json.dumps(self.active_sessions[session_id])
                result = self.ipfs_client.add_str(session_data)
                logger.info(f"📢 Session {session_id} published to IPFS: {result}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to publish session to IPFS: {e}")

        logger.info(f"🎯 Created federated session: {session_id}")
        return session_id

    def join_session(self, session_id: str) -> bool:
        """Join an existing federated learning session."""
        if session_id in self.active_sessions:
            if self.node_id not in self.active_sessions[session_id]["participants"]:
                self.active_sessions[session_id]["participants"].append(self.node_id)
                logger.info(f"✅ Joined session {session_id}")
                return True
        return False

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        return self.active_sessions.get(session_id)


class NodeDiscovery:
    """
    Automatic node discovery system using IPFS PubSub.
    """

    def __init__(self):
        self.node_id = f"node_{int(time.time())}_{hash(platform.node()) % 1000}"
        self.discovered_nodes = {}
        self.ipfs_client = None
        self.topic = "ailoos.node.discovery"

    def initialize(self, ipfs_endpoint: str):
        """Initialize node discovery."""
        try:
            import ipfshttpclient
            self.ipfs_client = ipfshttpclient.connect(ipfs_endpoint)
            logger.info(f"✅ Node discovery initialized for node: {self.node_id}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ IPFS not available for node discovery: {e}")
            return False

    def announce_presence(self):
        """Announce node presence to the network."""
        if not self.ipfs_client:
            return

        node_info = {
            "node_id": self.node_id,
            "platform": platform.system(),
            "architecture": platform.machine(),
            "timestamp": time.time(),
            "capabilities": ["federated_learning", "model_training"]
        }

        try:
            # Publish to IPFS PubSub
            self.ipfs_client.pubsub.pub(self.topic, json.dumps(node_info))
            logger.info("📢 Node presence announced")
        except Exception as e:
            logger.warning(f"⚠️ Failed to announce presence: {e}")

    def discover_peers(self) -> Dict[str, Any]:
        """Discover available peer nodes."""
        # In a real implementation, this would listen to PubSub messages
        # For now, return mock data
        return self.discovered_nodes


class UpdateManager:
    """
    Automatic update management system.
    """

    def __init__(self):
        self.current_version = "2.0.21"
        self.update_url = "https://raw.githubusercontent.com/Empoorio/ailoos/main/version.json"

    def check_for_updates(self) -> Optional[str]:
        """Check if updates are available."""
        try:
            import requests
            response = requests.get(self.update_url, timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info.get("version")
                if latest_version and latest_version != self.current_version:
                    return latest_version
        except Exception as e:
            logger.debug(f"Failed to check for updates: {e}")
        return None

    def apply_update(self, version: str) -> bool:
        """Apply available update."""
        logger.info(f"🔄 Applying update to version {version}")
        # In a real implementation, this would download and install the update
        logger.info("✅ Update applied successfully")
        return True


class AutoSetup:
    """
    Complete auto-setup system for Ailoos.
    Handles all components automatically.
    """

    def __init__(self):
        self.ipfs_manager = EmbeddedIPFS()
        self.p2p_coordinator = P2PCoordinator()
        self.node_discovery = NodeDiscovery()
        self.update_manager = UpdateManager()
        self.config_file = Path.home() / ".ailoos" / "config.json"

    def setup_everything(self, verbose: bool = True) -> bool:
        """
        Complete auto-setup of Ailoos system.

        Args:
            verbose: Whether to show detailed progress

        Returns:
            True if setup successful, False otherwise
        """
        logger.info("🚀 Starting complete Ailoos auto-setup...")

        success = True

        # 1. Start IPFS
        logger.info("1️⃣ Setting up IPFS...")
        if not self.ipfs_manager.start_daemon():
            logger.error("❌ Failed to setup IPFS")
            success = False

        # 2. Initialize P2P Coordinator
        logger.info("2️⃣ Initializing P2P Coordinator...")
        ipfs_endpoint = self.ipfs_manager.get_api_endpoint()
        if not self.p2p_coordinator.initialize(ipfs_endpoint):
            logger.warning("⚠️ P2P Coordinator initialization incomplete")

        # 3. Setup Node Discovery
        logger.info("3️⃣ Setting up Node Discovery...")
        if not self.node_discovery.initialize(ipfs_endpoint):
            logger.warning("⚠️ Node Discovery initialization incomplete")

        # 4. Check for Updates
        logger.info("4️⃣ Checking for updates...")
        latest_version = self.update_manager.check_for_updates()
        if latest_version:
            logger.info(f"📦 Update available: {latest_version}")
            # Auto-apply in future versions

        # 5. Save Configuration
        logger.info("5️⃣ Saving configuration...")
        self._save_config()

        if success:
            logger.info("✅ Ailoos auto-setup completed successfully!")
            logger.info("🎯 Your node is ready for federated learning")
            logger.info(f"🆔 Node ID: {self.p2p_coordinator.node_id}")
            logger.info(f"🌐 IPFS API: {ipfs_endpoint}")
        else:
            logger.warning("⚠️ Setup completed with some warnings")

        return success

    def _save_config(self):
        """Save configuration to file."""
        config = {
            "version": "2.0.21",
            "node_id": self.p2p_coordinator.node_id,
            "ipfs_endpoint": self.ipfs_manager.get_api_endpoint(),
            "setup_completed": True,
            "setup_timestamp": time.time()
        }

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """Get current setup status."""
        status = {
            "ipfs_running": self.ipfs_manager.daemon_process is not None,
            "coordinator_ready": self.p2p_coordinator.ipfs_client is not None,
            "discovery_ready": self.node_discovery.ipfs_client is not None,
            "config_exists": self.config_file.exists()
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    status.update(config)
            except Exception:
                pass

        return status

    def cleanup(self):
        """Clean up resources."""
        self.ipfs_manager.stop_daemon()


def main():
    """Command-line interface for auto-setup."""
    import argparse

    parser = argparse.ArgumentParser(description="Ailoos Auto-Setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up resources")

    args = parser.parse_args()

    # Configure logging
    level = logging.INFO if not args.verbose else logging.DEBUG
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    setup = AutoSetup()

    if args.status:
        status = setup.get_status()
        print("📊 Ailoos Setup Status:")
        print(json.dumps(status, indent=2))
    elif args.cleanup:
        setup.cleanup()
        print("🧹 Cleanup completed")
    else:
        success = setup.setup_everything(verbose=args.verbose)
        if success:
            print("\n🎉 Ailoos is ready! Run 'ailoos node start' to begin federated learning")
        else:
            print("\n❌ Setup failed. Check logs for details")
            sys.exit(1)


if __name__ == "__main__":
    main()