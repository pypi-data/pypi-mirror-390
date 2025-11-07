"""
Database monitoring and metrics collection for the coordinator service.
Provides real-time monitoring, performance metrics, and alerting.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import psutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .connection import get_db
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    timestamp: datetime
    active_connections: int
    total_connections: int
    connection_pool_size: int
    connection_pool_available: int
    query_count: int
    slow_queries: int
    deadlock_count: int
    cache_hit_ratio: float
    avg_query_time: float
    max_query_time: float
    database_size_bytes: int
    table_sizes: Dict[str, int]
    index_usage: Dict[str, float]
    replication_lag: Optional[float] = None


@dataclass
class QueryMetrics:
    """Individual query performance metrics."""
    query_id: str
    query_text: str
    execution_count: int
    total_time: float
    mean_time: float
    max_time: float
    min_time: float
    last_executed: datetime


class DatabaseMonitor:
    """Monitors database performance and health."""

    def __init__(self):
        self.collection_interval = 60  # seconds
        self.retention_period = timedelta(days=7)
        self.slow_query_threshold = 1.0  # seconds
        self.metrics_history: List[DatabaseMetrics] = []
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self.alert_callbacks: List[callable] = []

    def add_alert_callback(self, callback: callable):
        """Add a callback for alerts."""
        self.alert_callbacks.append(callback)

    async def start_monitoring(self):
        """Start the monitoring loop."""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Database monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            logger.info("Database monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await self._collect_metrics()
                await self._check_alerts()
                await self._cleanup_old_metrics()

                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _collect_metrics(self):
        """Collect current database metrics."""
        try:
            async with get_db() as session:
                metrics = await self._gather_database_metrics(session)
                self.metrics_history.append(metrics)

                # Keep only recent metrics
                cutoff = datetime.utcnow() - self.retention_period
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp > cutoff
                ]

                logger.debug(f"Collected database metrics: connections={metrics.active_connections}")

        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")

    async def _gather_database_metrics(self, session: AsyncSession) -> DatabaseMetrics:
        """Gather comprehensive database metrics."""
        timestamp = datetime.utcnow()

        # Basic connection info
        active_connections = await self._get_active_connections(session)
        total_connections = await self._get_total_connections(session)

        # Query performance
        query_count, slow_queries = await self._get_query_metrics(session)

        # Database size
        database_size = await self._get_database_size(session)
        table_sizes = await self._get_table_sizes(session)

        # Cache and performance
        cache_hit_ratio = await self._get_cache_hit_ratio(session)
        avg_query_time, max_query_time = await self._get_query_times(session)

        # Deadlocks
        deadlock_count = await self._get_deadlock_count(session)

        # Index usage
        index_usage = await self._get_index_usage(session)

        # Replication lag (if replica exists)
        replication_lag = await self._get_replication_lag(session)

        return DatabaseMetrics(
            timestamp=timestamp,
            active_connections=active_connections,
            total_connections=total_connections,
            connection_pool_size=settings.database.pool_size,
            connection_pool_available=settings.database.pool_size - active_connections,
            query_count=query_count,
            slow_queries=slow_queries,
            deadlock_count=deadlock_count,
            cache_hit_ratio=cache_hit_ratio,
            avg_query_time=avg_query_time,
            max_query_time=max_query_time,
            database_size_bytes=database_size,
            table_sizes=table_sizes,
            index_usage=index_usage,
            replication_lag=replication_lag
        )

    async def _get_active_connections(self, session: AsyncSession) -> int:
        """Get number of active connections."""
        try:
            result = await session.execute(text("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """))
            row = result.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    async def _get_total_connections(self, session: AsyncSession) -> int:
        """Get total number of connections."""
        try:
            result = await session.execute(text("""
                SELECT count(*) as total_connections
                FROM pg_stat_activity
            """))
            row = result.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    async def _get_query_metrics(self, session: AsyncSession) -> tuple[int, int]:
        """Get query count and slow queries."""
        try:
            result = await session.execute(text("""
                SELECT
                    sum(calls) as total_queries,
                    sum(case when mean_time > %s then 1 else 0 end) as slow_queries
                FROM pg_stat_statements
            """), (self.slow_query_threshold * 1000,))  # Convert to milliseconds

            row = result.fetchone()
            return (row[0] if row and row[0] else 0,
                   row[1] if row and row[1] else 0)
        except Exception:
            return 0, 0

    async def _get_database_size(self, session: AsyncSession) -> int:
        """Get total database size in bytes."""
        try:
            result = await session.execute(text("""
                SELECT pg_database_size(current_database()) as size_bytes
            """))
            row = result.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    async def _get_table_sizes(self, session: AsyncSession) -> Dict[str, int]:
        """Get sizes of main tables."""
        try:
            result = await session.execute(text("""
                SELECT
                    schemaname || '.' || tablename as table_name,
                    pg_total_relation_size(schemaname || '.' || tablename) as size_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN ('nodes', 'federated_sessions', 'contributions', 'audit_logs')
                ORDER BY size_bytes DESC
            """))

            return {row[0]: row[1] for row in result.fetchall()}
        except Exception:
            return {}

    async def _get_cache_hit_ratio(self, session: AsyncSession) -> float:
        """Get database cache hit ratio."""
        try:
            result = await session.execute(text("""
                SELECT
                    sum(blks_hit) / (sum(blks_hit) + sum(blks_read))::float as cache_hit_ratio
                FROM pg_stat_database
                WHERE datname = current_database()
            """))
            row = result.fetchone()
            return row[0] if row and row[0] else 0.0
        except Exception:
            return 0.0

    async def _get_query_times(self, session: AsyncSession) -> tuple[float, float]:
        """Get average and max query execution times."""
        try:
            result = await session.execute(text("""
                SELECT
                    avg(mean_time) / 1000 as avg_time_seconds,
                    max(max_time) / 1000 as max_time_seconds
                FROM pg_stat_statements
                WHERE calls > 10  -- Only consider frequently executed queries
            """))
            row = result.fetchone()
            return (row[0] if row and row[0] else 0.0,
                   row[1] if row and row[1] else 0.0)
        except Exception:
            return 0.0, 0.0

    async def _get_deadlock_count(self, session: AsyncSession) -> int:
        """Get deadlock count."""
        try:
            result = await session.execute(text("""
                SELECT deadlocks
                FROM pg_stat_database
                WHERE datname = current_database()
            """))
            row = result.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    async def _get_index_usage(self, session: AsyncSession) -> Dict[str, float]:
        """Get index usage statistics."""
        try:
            result = await session.execute(text("""
                SELECT
                    schemaname || '.' || tablename || '.' || indexname as index_name,
                    CASE
                        WHEN idx_scan + idx_tup_read > 0
                        THEN (idx_scan::float / (idx_scan + idx_tup_read)) * 100
                        ELSE 0
                    END as usage_percentage
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY usage_percentage DESC
                LIMIT 10
            """))

            return {row[0]: row[1] for row in result.fetchall()}
        except Exception:
            return {}

    async def _get_replication_lag(self, session: AsyncSession) -> Optional[float]:
        """Get replication lag in seconds (if replica)."""
        try:
            # This would check replication lag on a replica
            # For now, return None (not a replica)
            return None
        except Exception:
            return None

    async def _check_alerts(self):
        """Check for alert conditions."""
        if not self.metrics_history:
            return

        latest = self.metrics_history[-1]

        # Check connection pool usage
        pool_usage = (latest.connection_pool_size - latest.connection_pool_available) / latest.connection_pool_size
        if pool_usage > 0.9:
            await self._trigger_alert("high_connection_pool_usage", {
                "usage_percentage": pool_usage * 100,
                "active_connections": latest.active_connections
            })

        # Check slow queries
        if latest.slow_queries > 10:
            await self._trigger_alert("high_slow_query_count", {
                "slow_queries": latest.slow_queries,
                "threshold": 10
            })

        # Check deadlocks
        if latest.deadlock_count > 0:
            await self._trigger_alert("deadlocks_detected", {
                "deadlock_count": latest.deadlock_count
            })

        # Check cache hit ratio
        if latest.cache_hit_ratio < 0.95:
            await self._trigger_alert("low_cache_hit_ratio", {
                "cache_hit_ratio": latest.cache_hit_ratio
            })

    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """Trigger an alert."""
        logger.warning(f"Database alert: {alert_type} - {data}")

        for callback in self.alert_callbacks:
            try:
                await callback(alert_type, data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics data."""
        cutoff = datetime.utcnow() - self.retention_period
        self.metrics_history = [
            m for m in self.metrics_history
            if m.timestamp > cutoff
        ]

    def get_current_metrics(self) -> Optional[DatabaseMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_history(self, hours: int = 24) -> List[DatabaseMetrics]:
        """Get metrics history for the specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp > cutoff]

    async def get_detailed_report(self) -> Dict[str, Any]:
        """Generate a detailed database health report."""
        current = self.get_current_metrics()
        if not current:
            return {"error": "No metrics available"}

        # Calculate trends
        history = self.get_metrics_history(24)
        if len(history) >= 2:
            prev = history[-2]
            connection_trend = current.active_connections - prev.active_connections
            query_trend = current.query_count - prev.query_count
        else:
            connection_trend = 0
            query_trend = 0

        return {
            "timestamp": current.timestamp.isoformat(),
            "connections": {
                "active": current.active_connections,
                "total": current.total_connections,
                "pool_size": current.connection_pool_size,
                "pool_available": current.connection_pool_available,
                "trend": connection_trend
            },
            "performance": {
                "query_count": current.query_count,
                "slow_queries": current.slow_queries,
                "cache_hit_ratio": current.cache_hit_ratio,
                "avg_query_time": current.avg_query_time,
                "max_query_time": current.max_query_time,
                "query_trend": query_trend
            },
            "storage": {
                "database_size_bytes": current.database_size_bytes,
                "database_size_mb": current.database_size_bytes / (1024 * 1024),
                "table_sizes": current.table_sizes
            },
            "health": {
                "deadlock_count": current.deadlock_count,
                "replication_lag": current.replication_lag,
                "index_usage": current.index_usage
            }
        }


# Global monitor instance
db_monitor = DatabaseMonitor()


async def init_database_monitoring():
    """Initialize database monitoring."""
    await db_monitor.start_monitoring()
    logger.info("Database monitoring initialized")


async def shutdown_database_monitoring():
    """Shutdown database monitoring."""
    await db_monitor.stop_monitoring()
    logger.info("Database monitoring shutdown")


async def get_database_health_report() -> Dict[str, Any]:
    """Get a comprehensive database health report."""
    return await db_monitor.get_detailed_report()


def get_current_database_metrics() -> Optional[DatabaseMetrics]:
    """Get current database metrics."""
    return db_monitor.get_current_metrics()