"""
High Availability Database Manager for the coordinator service.
Handles connection failover, load balancing, and health monitoring.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any, Callable
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from .connection import get_engine, get_read_replica_engine
from ..config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseRole(Enum):
    """Database instance roles."""
    PRIMARY = "primary"
    REPLICA = "replica"


class ConnectionState(Enum):
    """Connection health states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class DatabaseInstance:
    """Represents a database instance with health status."""
    role: DatabaseRole
    host: str
    port: int
    state: ConnectionState
    last_health_check: float
    consecutive_failures: int
    connection_pool: Optional[Any] = None


class HighAvailabilityManager:
    """Manages high availability database connections with automatic failover."""

    def __init__(self):
        self.instances: Dict[str, DatabaseInstance] = {}
        self.health_check_interval = 30  # seconds
        self.max_consecutive_failures = 3
        self.failover_timeout = 60  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        self._failover_callbacks: List[Callable] = []

        # Initialize primary instance
        self._add_instance(
            "primary",
            DatabaseRole.PRIMARY,
            settings.database.host,
            settings.database.port
        )

        # Initialize read replica if configured
        if settings.database.use_read_replica and settings.database.read_replica_host:
            self._add_instance(
                "replica",
                DatabaseRole.REPLICA,
                settings.database.read_replica_host,
                settings.database.port
            )

    def _add_instance(self, name: str, role: DatabaseRole, host: str, port: int):
        """Add a database instance to the pool."""
        self.instances[name] = DatabaseInstance(
            role=role,
            host=host,
            port=port,
            state=ConnectionState.HEALTHY,
            last_health_check=time.time(),
            consecutive_failures=0
        )

    def add_failover_callback(self, callback: Callable):
        """Add a callback to be called on failover events."""
        self.failover_callbacks.append(callback)

    async def start_health_monitoring(self):
        """Start the health monitoring loop."""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
            logger.info("Started database health monitoring")

    async def stop_health_monitoring(self):
        """Stop the health monitoring loop."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
            logger.info("Stopped database health monitoring")

    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _perform_health_checks(self):
        """Perform health checks on all database instances."""
        for name, instance in self.instances.items():
            try:
                healthy = await self._check_instance_health(instance)
                if healthy:
                    if instance.state != ConnectionState.HEALTHY:
                        logger.info(f"Database instance {name} recovered to healthy state")
                        instance.state = ConnectionState.HEALTHY
                        instance.consecutive_failures = 0
                    instance.last_health_check = time.time()
                else:
                    instance.consecutive_failures += 1
                    if instance.consecutive_failures >= self.max_consecutive_failures:
                        if instance.state != ConnectionState.UNHEALTHY:
                            logger.warning(f"Database instance {name} marked as unhealthy")
                            instance.state = ConnectionState.UNHEALTHY
                            await self._handle_instance_failure(name, instance)
                    else:
                        instance.state = ConnectionState.DEGRADED
                        logger.warning(f"Database instance {name} health check failed ({instance.consecutive_failures}/{self.max_consecutive_failures})")

            except Exception as e:
                logger.error(f"Error checking health of instance {name}: {e}")
                instance.consecutive_failures += 1

    async def _check_instance_health(self, instance: DatabaseInstance) -> bool:
        """Check the health of a database instance."""
        try:
            # Use a simple query to test connectivity
            engine = instance.connection_pool
            if engine is None:
                # Create a temporary connection for health check
                connection_string = self._build_connection_string(instance)
                engine = create_async_engine(
                    connection_string,
                    poolclass=AsyncAdaptedQueuePool,
                    pool_size=1,
                    max_overflow=0,
                    pool_pre_ping=True
                )

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                return row is not None and row[0] == 1

        except Exception as e:
            logger.debug(f"Health check failed for {instance.host}:{instance.port}: {e}")
            return False

    def _build_connection_string(self, instance: DatabaseInstance) -> str:
        """Build connection string for an instance."""
        if settings.database.cloud_sql_instance:
            # Cloud SQL connection
            return f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}@/{settings.database.name}?host=/cloudsql/{settings.database.cloud_sql_instance}&sslmode={settings.database.ssl_mode}"
        else:
            # Standard connection
            return f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}@{instance.host}:{instance.port}/{settings.database.name}?sslmode={settings.database.ssl_mode}"

    async def _handle_instance_failure(self, name: str, instance: DatabaseInstance):
        """Handle failure of a database instance."""
        logger.error(f"Handling failure of database instance {name}")

        # Notify failover callbacks
        for callback in self._failover_callbacks:
            try:
                await callback(name, instance)
            except Exception as e:
                logger.error(f"Error in failover callback: {e}")

        # If primary fails, attempt to promote a replica
        if instance.role == DatabaseRole.PRIMARY:
            await self._attempt_failover()

    async def _attempt_failover(self):
        """Attempt to failover to a healthy replica."""
        logger.info("Attempting database failover")

        # Find a healthy replica
        healthy_replica = None
        for name, instance in self.instances.items():
            if (instance.role == DatabaseRole.REPLICA and
                instance.state == ConnectionState.HEALTHY):
                healthy_replica = (name, instance)
                break

        if healthy_replica:
            name, instance = healthy_replica
            logger.info(f"Promoting replica {name} to primary")

            # In a real implementation, you would:
            # 1. Promote the replica to primary
            # 2. Update connection routing
            # 3. Reconfigure other replicas
            # For now, we'll just log the event

            # Update the instance role
            instance.role = DatabaseRole.PRIMARY

            # Notify callbacks
            for callback in self._failover_callbacks:
                try:
                    await callback("failover_completed", instance)
                except Exception as e:
                    logger.error(f"Error in failover callback: {e}")
        else:
            logger.error("No healthy replicas available for failover")

    def get_healthy_instances(self, role: Optional[DatabaseRole] = None) -> List[DatabaseInstance]:
        """Get list of healthy database instances, optionally filtered by role."""
        instances = [
            instance for instance in self.instances.values()
            if instance.state == ConnectionState.HEALTHY
        ]

        if role:
            instances = [inst for inst in instances if inst.role == role]

        return instances

    def get_primary_instance(self) -> Optional[DatabaseInstance]:
        """Get the current primary instance if healthy."""
        primaries = self.get_healthy_instances(DatabaseRole.PRIMARY)
        return primaries[0] if primaries else None

    def get_replica_instances(self) -> List[DatabaseInstance]:
        """Get all healthy replica instances."""
        return self.get_healthy_instances(DatabaseRole.REPLICA)

    @asynccontextmanager
    async def get_session(self, read_only: bool = False):
        """Get a database session with automatic failover."""
        if read_only and self.get_replica_instances():
            # Use a replica for read operations
            instances = self.get_replica_instances()
        else:
            # Use primary for write operations or if no replicas available
            primary = self.get_primary_instance()
            instances = [primary] if primary else []

        if not instances:
            raise RuntimeError("No healthy database instances available")

        # Simple load balancing: round-robin
        instance = instances[0]  # For now, just use the first available

        # Get or create async engine for this instance
        if instance.connection_pool is None:
            connection_string = self._build_connection_string(instance)
            instance.connection_pool = create_async_engine(
                connection_string,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_pre_ping=settings.database.pool_pre_ping,
                pool_recycle=settings.database.pool_recycle,
                echo=settings.database.echo
            )

        # Create session
        async_session = async_sessionmaker(instance.connection_pool, expire_on_commit=False)
        session = async_session()

        try:
            yield session
        finally:
            await session.close()

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics for monitoring."""
        stats = {
            "total_instances": len(self.instances),
            "healthy_instances": len(self.get_healthy_instances()),
            "primary_healthy": self.get_primary_instance() is not None,
            "replicas_healthy": len(self.get_replica_instances()),
            "instances": {}
        }

        for name, instance in self.instances.items():
            stats["instances"][name] = {
                "role": instance.role.value,
                "host": instance.host,
                "port": instance.port,
                "state": instance.state.value,
                "last_health_check": instance.last_health_check,
                "consecutive_failures": instance.consecutive_failures
            }

        return stats


# Global HA manager instance
ha_manager = HighAvailabilityManager()


async def init_ha_manager():
    """Initialize the high availability manager."""
    await ha_manager.start_health_monitoring()
    logger.info("High availability database manager initialized")


async def shutdown_ha_manager():
    """Shutdown the high availability manager."""
    await ha_manager.stop_health_monitoring()
    logger.info("High availability database manager shutdown")


# Convenience functions for backward compatibility
@asynccontextmanager
async def get_ha_session(read_only: bool = False):
    """Get a high availability database session."""
    async with ha_manager.get_session(read_only=read_only) as session:
        yield session


async def get_ha_connection_stats() -> Dict[str, Any]:
    """Get high availability connection statistics."""
    return await ha_manager.get_connection_stats()