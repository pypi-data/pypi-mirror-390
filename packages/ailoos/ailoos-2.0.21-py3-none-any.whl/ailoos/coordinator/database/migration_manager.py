"""
Database migration management for the coordinator service.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations using Alembic."""

    def __init__(self, alembic_dir: Optional[str] = None):
        if alembic_dir is None:
            # Default to the alembic directory relative to this file
            self.alembic_dir = Path(__file__).parent / "alembic"
        else:
            self.alembic_dir = Path(alembic_dir)

        self.alembic_ini = self.alembic_dir / "alembic.ini"

    def _run_alembic_command(self, command: List[str]) -> bool:
        """Run an Alembic command and return success status."""
        try:
            cmd = [sys.executable, "-m", "alembic"] + command
            if str(self.alembic_ini) != "alembic.ini":
                cmd.extend(["-c", str(self.alembic_ini)])

            logger.info(f"Running Alembic command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=self.alembic_dir.parent,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout:
                logger.info(f"Alembic output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Alembic stderr: {result.stderr}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Alembic command failed: {e}")
            if e.stdout:
                logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error running Alembic command: {e}")
            return False

    def init_migrations(self) -> bool:
        """Initialize Alembic migrations if not already done."""
        if not self.alembic_dir.exists():
            logger.info("Initializing Alembic migrations")
            return self._run_alembic_command(["init", str(self.alembic_dir)])
        else:
            logger.info("Alembic migrations already initialized")
            return True

    def create_revision(self, message: str, autogenerate: bool = True) -> bool:
        """Create a new migration revision."""
        command = ["revision", "--autogenerate" if autogenerate else "revision", "-m", message]
        return self._run_alembic_command(command)

    def upgrade(self, revision: str = "head") -> bool:
        """Upgrade database to specified revision."""
        return self._run_alembic_command(["upgrade", revision])

    def downgrade(self, revision: str) -> bool:
        """Downgrade database to specified revision."""
        return self._run_alembic_command(["downgrade", revision])

    def current(self) -> Optional[str]:
        """Get current migration revision."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "current"],
                cwd=self.alembic_dir.parent,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def history(self) -> Optional[str]:
        """Get migration history."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "history"],
                cwd=self.alembic_dir.parent,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def check_migration_needed(self) -> bool:
        """Check if there are pending migrations."""
        try:
            # Try to run alembic check (available in newer versions)
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "check"],
                cwd=self.alembic_dir.parent,
                capture_output=True,
                text=True
            )
            return result.returncode != 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: check if there are migration files newer than current revision
            # This is a simplified check
            return False


def run_migrations_on_startup():
    """Run database migrations on application startup."""
    migration_manager = MigrationManager()

    logger.info("Checking database migrations on startup")

    # Check if migrations are needed
    if migration_manager.check_migration_needed():
        logger.info("Running database migrations")
        if migration_manager.upgrade():
            logger.info("Database migrations completed successfully")
        else:
            logger.error("Database migrations failed")
            raise RuntimeError("Failed to run database migrations")
    else:
        logger.info("Database is up to date")


if __name__ == "__main__":
    # Allow running migrations from command line
    import argparse

    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("command", choices=["init", "upgrade", "downgrade", "current", "history", "create"])
    parser.add_argument("--message", "-m", help="Migration message for create command")
    parser.add_argument("--revision", "-r", default="head", help="Revision for upgrade/downgrade")

    args = parser.parse_args()

    manager = MigrationManager()

    if args.command == "init":
        success = manager.init_migrations()
    elif args.command == "upgrade":
        success = manager.upgrade(args.revision)
    elif args.command == "downgrade":
        success = manager.downgrade(args.revision)
    elif args.command == "current":
        current_rev = manager.current()
        print(f"Current revision: {current_rev}")
        success = current_rev is not None
    elif args.command == "history":
        history = manager.history()
        if history:
            print(history)
            success = True
        else:
            success = False
    elif args.command == "create":
        if not args.message:
            print("Message required for create command")
            success = False
        else:
            success = manager.create_revision(args.message)

    sys.exit(0 if success else 1)