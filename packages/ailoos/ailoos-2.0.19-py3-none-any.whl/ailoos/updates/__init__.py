"""
Automatic updates system for Ailoos.
Provides seamless updates for models, software, and configurations.
"""

from .auto_updater import UpdateManager, RollingUpdateManager, UpdateInfo, UpdateStatus
from .update_server import UpdateServer, UpdateMetadata

__all__ = [
    'UpdateManager',
    'RollingUpdateManager',
    'UpdateServer',
    'UpdateInfo',
    'UpdateStatus',
    'UpdateMetadata'
]