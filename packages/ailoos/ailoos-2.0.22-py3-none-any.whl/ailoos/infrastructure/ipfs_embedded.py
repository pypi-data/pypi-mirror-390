"""
Embedded IPFS integration for Ailoos SDK.
Provides IPFS functionality without requiring separate installation.
"""

import os
import sys
import platform
import subprocess
import time
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class EmbeddedIPFS:
    """
    Embedded IPFS manager that bundles IPFS daemon with the SDK.
    Handles automatic download, installation, and lifecycle management.
    """

    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.ailoos_dir = Path.home() / ".ailoos"
        self.ipfs_dir = self.ailoos_dir / "ipfs"
        self.ipfs_binary = self._get_binary_path()
        self.daemon_process = None
        self.api_endpoint = "http://localhost:5001"
        self.gateway_endpoint = "http://localhost:8080"

    def _get_binary_path(self) -> Path:
        """Get the path to the IPFS binary based on platform."""
        if self.system == "darwin":
            if "arm64" in self.arch:
                return self.ipfs_dir / "kubo" / "ipfs"
            else:
                return self.ipfs_dir / "kubo" / "ipfs"
        elif self.system == "linux":
            return self.ipfs_dir / "kubo" / "ipfs"
        elif self.system == "windows":
            return self.ipfs_dir / "kubo" / "ipfs.exe"
        else:
            raise RuntimeError(f"Unsupported platform: {self.system} {self.arch}")

    def _get_download_url(self) -> str:
        """Get the download URL for IPFS binary."""
        version = "v0.21.0"

        if self.system == "darwin":
            if "arm64" in self.arch:
                return f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_darwin-arm64.tar.gz"
            else:
                return f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_darwin-amd64.tar.gz"
        elif self.system == "linux":
            return f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_linux-amd64.tar.gz"
        elif self.system == "windows":
            return f"https://dist.ipfs.tech/kubo/{version}/kubo_{version}_windows-amd64.zip"
        else:
            raise RuntimeError(f"No IPFS binary available for {self.system} {self.arch}")

    def _download_and_extract_ipfs(self) -> bool:
        """Download and extract IPFS binary."""
        try:
            import urllib.request
            import tarfile
            import zipfile

            logger.info("📥 Downloading IPFS daemon...")

            download_url = self._get_download_url()
            self.ipfs_dir.mkdir(parents=True, exist_ok=True)

            # Download file
            filename = download_url.split('/')[-1]
            archive_path = self.ipfs_dir / filename

            urllib.request.urlretrieve(download_url, archive_path)

            # Extract archive
            if filename.endswith('.tar.gz'):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(self.ipfs_dir)
            elif filename.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.ipfs_dir)

            # Make executable on Unix systems
            if self.system != "windows":
                self.ipfs_binary.chmod(0o755)

            # Cleanup
            archive_path.unlink()

            logger.info("✅ IPFS daemon downloaded and extracted")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to download/extract IPFS: {e}")
            return False

    def _init_repository(self) -> bool:
        """Initialize IPFS repository."""
        try:
            logger.info("🔧 Initializing IPFS repository...")

            result = subprocess.run(
                [str(self.ipfs_binary), "init"],
                capture_output=True,
                text=True,
                cwd=self.ailoos_dir
            )

            if result.returncode == 0:
                logger.info("✅ IPFS repository initialized")
                return True
            else:
                logger.error(f"❌ IPFS init failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize IPFS repository: {e}")
            return False

    def start_daemon(self, background: bool = True) -> bool:
        """
        Start IPFS daemon.

        Args:
            background: Whether to run in background

        Returns:
            True if daemon started successfully
        """
        try:
            # Check if binary exists
            if not self.ipfs_binary.exists():
                if not self._download_and_extract_ipfs():
                    return False

            # Check if repository exists
            ipfs_repo = self.ailoos_dir / ".ipfs"
            if not ipfs_repo.exists():
                if not self._init_repository():
                    return False

            logger.info("🚀 Starting IPFS daemon...")

            if background:
                self.daemon_process = subprocess.Popen(
                    [str(self.ipfs_binary), "daemon"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=self.ailoos_dir
                )

                # Wait for daemon to be ready
                max_attempts = 30
                for attempt in range(max_attempts):
                    if self._check_daemon_ready():
                        logger.info("✅ IPFS daemon started and ready")
                        return True
                    time.sleep(1)

                logger.error("❌ IPFS daemon failed to become ready")
                self.stop_daemon()
                return False
            else:
                # Run in foreground
                subprocess.run([str(self.ipfs_binary), "daemon"], cwd=self.ailoos_dir)
                return True

        except Exception as e:
            logger.error(f"❌ Failed to start IPFS daemon: {e}")
            return False

    def _check_daemon_ready(self) -> bool:
        """Check if IPFS daemon is ready."""
        try:
            import requests
            response = requests.post(
                f"{self.api_endpoint}/api/v0/id",
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False

    def stop_daemon(self):
        """Stop IPFS daemon."""
        if self.daemon_process:
            try:
                self.daemon_process.terminate()
                self.daemon_process.wait(timeout=10)
                logger.info("🛑 IPFS daemon stopped")
            except subprocess.TimeoutExpired:
                self.daemon_process.kill()
                logger.warning("⚠️ IPFS daemon force killed")

    def add_file(self, file_path: str) -> Optional[str]:
        """
        Add file to IPFS.

        Args:
            file_path: Path to file to add

        Returns:
            IPFS hash if successful, None otherwise
        """
        try:
            import requests

            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.api_endpoint}/api/v0/add",
                    files={'file': f}
                )

            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                logger.info(f"📄 File added to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"❌ Failed to add file: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error adding file to IPFS: {e}")
            return None

    def get_file(self, ipfs_hash: str, output_path: str) -> bool:
        """
        Retrieve file from IPFS.

        Args:
            ipfs_hash: IPFS hash of file
            output_path: Local path to save file

        Returns:
            True if successful
        """
        try:
            import requests

            response = requests.post(
                f"{self.api_endpoint}/api/v0/get",
                params={'arg': ipfs_hash}
            )

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"📂 File retrieved from IPFS: {ipfs_hash}")
                return True
            else:
                logger.error(f"❌ Failed to get file: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error retrieving file from IPFS: {e}")
            return False

    def pin_file(self, ipfs_hash: str) -> bool:
        """
        Pin file to ensure persistence.

        Args:
            ipfs_hash: IPFS hash to pin

        Returns:
            True if successful
        """
        try:
            import requests

            response = requests.post(
                f"{self.api_endpoint}/api/v0/pin/add",
                params={'arg': ipfs_hash}
            )

            if response.status_code == 200:
                logger.info(f"📌 File pinned: {ipfs_hash}")
                return True
            else:
                logger.error(f"❌ Failed to pin file: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error pinning file: {e}")
            return False

    def publish_message(self, topic: str, message: str) -> bool:
        """
        Publish message to IPFS PubSub.

        Args:
            topic: PubSub topic
            message: Message to publish

        Returns:
            True if successful
        """
        try:
            import requests

            response = requests.post(
                f"{self.api_endpoint}/api/v0/pubsub/pub",
                params={
                    'arg': topic,
                    'arg': message
                }
            )

            if response.status_code == 200:
                logger.debug(f"📢 Message published to topic '{topic}'")
                return True
            else:
                logger.error(f"❌ Failed to publish message: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error publishing message: {e}")
            return False

    def subscribe_topic(self, topic: str) -> Optional[List[Dict[str, Any]]]:
        """
        Subscribe to IPFS PubSub topic and get messages.

        Args:
            topic: Topic to subscribe to

        Returns:
            List of messages if successful
        """
        try:
            import requests

            response = requests.post(
                f"{self.api_endpoint}/api/v0/pubsub/sub",
                params={'arg': topic}
            )

            if response.status_code == 200:
                # Parse messages (simplified)
                messages = []
                for line in response.text.strip().split('\n'):
                    if line:
                        try:
                            msg = json.loads(line)
                            messages.append(msg)
                        except json.JSONDecodeError:
                            continue
                return messages
            else:
                logger.error(f"❌ Failed to subscribe to topic: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error subscribing to topic: {e}")
            return None

    def get_node_id(self) -> Optional[str]:
        """Get IPFS node ID."""
        try:
            import requests

            response = requests.post(f"{self.api_endpoint}/api/v0/id")

            if response.status_code == 200:
                data = response.json()
                return data.get('ID')
            else:
                logger.error(f"❌ Failed to get node ID: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error getting node ID: {e}")
            return None

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get IPFS node statistics."""
        try:
            import requests

            response = requests.post(f"{self.api_endpoint}/api/v0/stats/repo")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get stats: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return None


# Convenience functions for easy access
_embedded_ipfs_instance = None

def get_embedded_ipfs() -> EmbeddedIPFS:
    """Get singleton instance of embedded IPFS."""
    global _embedded_ipfs_instance
    if _embedded_ipfs_instance is None:
        _embedded_ipfs_instance = EmbeddedIPFS()
    return _embedded_ipfs_instance

def start_ipfs_daemon() -> bool:
    """Start embedded IPFS daemon."""
    return get_embedded_ipfs().start_daemon()

def stop_ipfs_daemon():
    """Stop embedded IPFS daemon."""
    get_embedded_ipfs().stop_daemon()

def add_to_ipfs(file_path: str) -> Optional[str]:
    """Add file to IPFS."""
    return get_embedded_ipfs().add_file(file_path)

def get_from_ipfs(ipfs_hash: str, output_path: str) -> bool:
    """Get file from IPFS."""
    return get_embedded_ipfs().get_file(ipfs_hash, output_path)