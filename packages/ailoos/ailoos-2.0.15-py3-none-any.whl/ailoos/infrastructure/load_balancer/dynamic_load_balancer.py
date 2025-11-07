"""
Dynamic Load Balancer for Ailoos federated learning.
Provides intelligent workload distribution, auto-scaling, and resource optimization.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import random
import math

from ...core.config import Config
from ...utils.logging import AiloosLogger
from ..gcp.gcp_integration import GCPIntegration


@dataclass
class NodeMetrics:
    """Real-time metrics for a compute node."""
    node_id: str
    region: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    network_in: float = 0.0
    network_out: float = 0.0
    active_sessions: int = 0
    training_jobs: int = 0
    inference_jobs: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    health_score: float = 1.0
    reputation_score: float = 1.0
    cost_per_hour: float = 0.0
    uptime_hours: float = 0.0


@dataclass
class WorkloadRequest:
    """Workload request with requirements and constraints."""
    request_id: str
    workload_type: str  # 'training', 'inference', 'validation'
    priority: int  # 1-10, higher = more important
    required_cpu: float  # CPU cores required
    required_memory: float  # GB required
    required_gpu: bool = False
    gpu_memory_gb: float = 0.0
    max_latency_ms: int = 1000
    data_locality: Optional[str] = None  # Preferred region for data
    user_location: Optional[Dict[str, float]] = None  # {'lat': float, 'lng': float}
    estimated_duration_hours: float = 1.0
    deadline: Optional[datetime] = None
    compliance_requirements: List[str] = field(default_factory=list)


@dataclass
class LoadBalancingDecision:
    """Decision made by the load balancer."""
    request_id: str
    selected_nodes: List[str]
    estimated_cost: float
    estimated_completion_time: datetime
    confidence_score: float
    alternative_nodes: List[str] = field(default_factory=list)
    reasoning: str = ""


class DynamicLoadBalancer:
    """Intelligent dynamic load balancer for federated learning workloads."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = AiloosLogger(__name__)

        # Node management
        self.nodes: Dict[str, NodeMetrics] = {}
        self.node_capacity: Dict[str, Dict[str, float]] = {}
        self.node_regions: Dict[str, str] = {}

        # Workload queues
        self.pending_queue: asyncio.Queue[WorkloadRequest] = asyncio.Queue()
        self.processing_workloads: Dict[str, WorkloadRequest] = {}
        self.completed_workloads: deque = deque(maxlen=10000)

        # Metrics and analytics
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics: Dict[str, Any] = {}
        self.cost_metrics: Dict[str, float] = {}

        # Load balancing strategies
        self.strategies = {
            'cost_optimized': self._cost_optimized_strategy,
            'performance_optimized': self._performance_optimized_strategy,
            'latency_optimized': self._latency_optimized_strategy,
            'balanced': self._balanced_strategy,
            'compliance_first': self._compliance_first_strategy
        }

        # Auto-scaling
        self.scaling_policies: Dict[str, Dict[str, Any]] = {}
        self.scaling_history: deque = deque(maxlen=1000)

        # GCP integration for auto-scaling
        self.gcp_client = GCPIntegration(config)

        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.scaling_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None

        # Initialize
        self._initialize_load_balancer()

    def _initialize_load_balancer(self):
        """Initialize the load balancer with default settings."""
        # Default scaling policies
        self.scaling_policies = {
            'cpu_based': {
                'metric': 'cpu_usage',
                'threshold_high': 0.8,
                'threshold_low': 0.3,
                'scale_up_factor': 1.5,
                'scale_down_factor': 0.7,
                'cooldown_minutes': 5
            },
            'memory_based': {
                'metric': 'memory_usage',
                'threshold_high': 0.85,
                'threshold_low': 0.4,
                'scale_up_factor': 1.3,
                'scale_down_factor': 0.8,
                'cooldown_minutes': 3
            },
            'queue_based': {
                'metric': 'queue_length',
                'threshold_high': 50,
                'threshold_low': 10,
                'scale_up_factor': 2.0,
                'scale_down_factor': 0.5,
                'cooldown_minutes': 2
            }
        }

        self.logger.info("Dynamic Load Balancer initialized with default policies")

    async def start(self):
        """Start the load balancer background tasks."""
        self.monitoring_task = asyncio.create_task(self._monitor_nodes())
        self.scaling_task = asyncio.create_task(self._auto_scaling_loop())
        self.optimization_task = asyncio.create_task(self._optimization_loop())

        # Start processing workloads
        asyncio.create_task(self._process_workload_queue())

        self.logger.info("Dynamic Load Balancer started")

    async def stop(self):
        """Stop the load balancer background tasks."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.scaling_task:
            self.scaling_task.cancel()
        if self.optimization_task:
            self.optimization_task.cancel()

        self.logger.info("Dynamic Load Balancer stopped")

    async def register_node(self, node_id: str, region: str, capacity: Dict[str, float]):
        """Register a new node with the load balancer."""
        if node_id in self.nodes:
            self.logger.warning(f"Node {node_id} already registered, updating")
            return

        node_metrics = NodeMetrics(
            node_id=node_id,
            region=region,
            cost_per_hour=self._calculate_node_cost(capacity)
        )

        self.nodes[node_id] = node_metrics
        self.node_capacity[node_id] = capacity
        self.node_regions[node_id] = region

        self.logger.info(f"Registered node {node_id} in region {region}")

    async def unregister_node(self, node_id: str):
        """Unregister a node from the load balancer."""
        if node_id not in self.nodes:
            self.logger.warning(f"Node {node_id} not found")
            return

        # Reassign any workloads on this node
        await self._reassign_workloads_from_node(node_id)

        del self.nodes[node_id]
        del self.node_capacity[node_id]
        del self.node_regions[node_id]

        self.logger.info(f"Unregistered node {node_id}")

    async def submit_workload(self, workload: WorkloadRequest) -> LoadBalancingDecision:
        """Submit a workload for processing."""
        await self.pending_queue.put(workload)

        # Make initial load balancing decision
        decision = await self._make_load_balancing_decision(workload)

        if decision.selected_nodes:
            # Assign workload to selected nodes
            await self._assign_workload_to_nodes(workload, decision.selected_nodes)

        return decision

    async def update_node_metrics(self, node_id: str, metrics: Dict[str, Any]):
        """Update metrics for a specific node."""
        if node_id not in self.nodes:
            self.logger.warning(f"Node {node_id} not found")
            return

        node = self.nodes[node_id]

        # Update metrics
        for key, value in metrics.items():
            if hasattr(node, key):
                setattr(node, key, value)

        node.last_heartbeat = datetime.now()

        # Calculate health score
        node.health_score = self._calculate_health_score(node)

        # Store metrics history
        self.metrics_history[node_id].append({
            'timestamp': datetime.now(),
            'metrics': metrics.copy()
        })

    async def _make_load_balancing_decision(self, workload: WorkloadRequest) -> LoadBalancingDecision:
        """Make a load balancing decision for a workload."""
        try:
            # Filter eligible nodes
            eligible_nodes = self._filter_eligible_nodes(workload)

            if not eligible_nodes:
                return LoadBalancingDecision(
                    request_id=workload.request_id,
                    selected_nodes=[],
                    estimated_cost=0.0,
                    estimated_completion_time=datetime.now(),
                    confidence_score=0.0,
                    reasoning="No eligible nodes found"
                )

            # Choose load balancing strategy
            strategy = self._select_strategy(workload)
            selected_nodes, confidence = await strategy(workload, eligible_nodes)

            if not selected_nodes:
                return LoadBalancingDecision(
                    request_id=workload.request_id,
                    selected_nodes=[],
                    estimated_cost=0.0,
                    estimated_completion_time=datetime.now(),
                    confidence_score=0.0,
                    reasoning="Strategy could not select nodes"
                )

            # Calculate cost and timing estimates
            estimated_cost = self._estimate_cost(selected_nodes, workload)
            completion_time = self._estimate_completion_time(selected_nodes, workload)

            # Find alternative nodes
            alternative_nodes = self._find_alternative_nodes(workload, eligible_nodes, selected_nodes)

            return LoadBalancingDecision(
                request_id=workload.request_id,
                selected_nodes=selected_nodes,
                estimated_cost=estimated_cost,
                estimated_completion_time=completion_time,
                confidence_score=confidence,
                alternative_nodes=alternative_nodes,
                reasoning=f"Selected using {strategy.__name__} strategy"
            )

        except Exception as e:
            self.logger.error(f"Error making load balancing decision: {e}")
            return LoadBalancingDecision(
                request_id=workload.request_id,
                selected_nodes=[],
                estimated_cost=0.0,
                estimated_completion_time=datetime.now(),
                confidence_score=0.0,
                reasoning=f"Error: {str(e)}"
            )

    def _filter_eligible_nodes(self, workload: WorkloadRequest) -> List[str]:
        """Filter nodes that can handle the workload."""
        eligible = []

        for node_id, node in self.nodes.items():
            capacity = self.node_capacity[node_id]

            # Check basic requirements
            if workload.required_cpu > capacity.get('cpu_available', 0):
                continue
            if workload.required_memory > capacity.get('memory_available_gb', 0):
                continue

            # Check GPU requirements
            if workload.required_gpu and not capacity.get('gpu_available', False):
                continue
            if workload.gpu_memory_gb > capacity.get('gpu_memory_gb', 0):
                continue

            # Check compliance requirements
            if not self._check_compliance_requirements(node, workload):
                continue

            # Check health
            if node.health_score < 0.7:
                continue

            # Check data locality preference
            if workload.data_locality and workload.data_locality != node.region:
                # Penalize but don't exclude for data locality
                pass

            eligible.append(node_id)

        return eligible

    def _check_compliance_requirements(self, node: NodeMetrics, workload: WorkloadRequest) -> bool:
        """Check if node meets compliance requirements."""
        # Simplified compliance check (in production, this would be more sophisticated)
        node_region = node.region

        # Map regions to compliance frameworks
        region_compliance = {
            'europe-west1': ['GDPR', 'ISO27001'],
            'us-central1': ['CCPA', 'SOC2', 'ISO27001'],
            'asia-southeast1': ['PDPA', 'ISO27001'],
            'southamerica-east1': ['LGPD', 'ISO27001']
        }

        available_compliance = region_compliance.get(node_region, [])
        return all(req in available_compliance for req in workload.compliance_requirements)

    def _select_strategy(self, workload: WorkloadRequest):
        """Select the appropriate load balancing strategy."""
        # Strategy selection based on workload characteristics
        if workload.priority >= 9:
            return self.strategies['latency_optimized']
        elif workload.deadline and workload.deadline < datetime.now() + timedelta(hours=1):
            return self.strategies['performance_optimized']
        elif workload.workload_type == 'training':
            return self.strategies['balanced']
        elif any('GDPR' in req for req in workload.compliance_requirements):
            return self.strategies['compliance_first']
        else:
            return self.strategies['cost_optimized']

    async def _cost_optimized_strategy(self, workload: WorkloadRequest, eligible_nodes: List[str]) -> Tuple[List[str], float]:
        """Cost-optimized load balancing strategy."""
        # Sort nodes by cost efficiency
        node_scores = []
        for node_id in eligible_nodes:
            node = self.nodes[node_id]
            capacity = self.node_capacity[node_id]

            # Calculate cost efficiency score
            utilization = (node.cpu_usage + node.memory_usage) / 2
            efficiency_score = (1 - utilization) / max(node.cost_per_hour, 0.01)

            # Factor in reputation and health
            final_score = efficiency_score * node.reputation_score * node.health_score

            node_scores.append((node_id, final_score))

        # Select top nodes
        node_scores.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(len(node_scores), max(1, workload.priority // 2))
        selected_nodes = [node_id for node_id, _ in node_scores[:selected_count]]

        confidence = min(0.9, len(selected_nodes) / len(eligible_nodes))

        return selected_nodes, confidence

    async def _performance_optimized_strategy(self, workload: WorkloadRequest, eligible_nodes: List[str]) -> Tuple[List[str], float]:
        """Performance-optimized load balancing strategy."""
        # Sort nodes by performance metrics
        node_scores = []
        for node_id in eligible_nodes:
            node = self.nodes[node_id]

            # Performance score based on current load and capabilities
            load_penalty = (node.cpu_usage + node.memory_usage + node.gpu_usage) / 3
            performance_score = (1 - load_penalty) * node.reputation_score * node.health_score

            # Bonus for nodes with recent successful workloads
            recent_success_bonus = self._calculate_recent_success_bonus(node_id)
            performance_score *= (1 + recent_success_bonus)

            node_scores.append((node_id, performance_score))

        # Select top performers
        node_scores.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(len(node_scores), max(1, workload.priority // 3))
        selected_nodes = [node_id for node_id, _ in node_scores[:selected_count]]

        confidence = min(0.95, len(selected_nodes) / len(eligible_nodes))

        return selected_nodes, confidence

    async def _latency_optimized_strategy(self, workload: WorkloadRequest, eligible_nodes: List[str]) -> Tuple[List[str], float]:
        """Latency-optimized load balancing strategy."""
        # Prioritize nodes with lowest latency to user location
        node_scores = []
        for node_id in eligible_nodes:
            node = self.nodes[node_id]

            # Calculate latency score
            latency_score = 1.0
            if workload.user_location:
                latency_score = self._calculate_latency_score(node.region, workload.user_location)

            # Factor in current load
            load_factor = 1 - ((node.cpu_usage + node.memory_usage) / 2)

            final_score = latency_score * load_factor * node.health_score

            node_scores.append((node_id, final_score))

        # Select lowest latency nodes
        node_scores.sort(key=lambda x: x[1], reverse=True)
        selected_nodes = [node_id for node_id, _ in node_scores[:1]]  # Single node for latency

        confidence = 0.8 if selected_nodes else 0.0

        return selected_nodes, confidence

    async def _balanced_strategy(self, workload: WorkloadRequest, eligible_nodes: List[str]) -> Tuple[List[str], float]:
        """Balanced load balancing strategy."""
        # Balance between cost, performance, and load distribution
        node_scores = []
        for node_id in eligible_nodes:
            node = self.nodes[node_id]
            capacity = self.node_capacity[node_id]

            # Multi-factor scoring
            cost_score = 1 / max(node.cost_per_hour, 0.01)
            performance_score = (1 - node.cpu_usage) * node.reputation_score
            load_balance_score = 1 / (1 + node.active_sessions)  # Prefer less loaded nodes

            final_score = (cost_score * 0.3 + performance_score * 0.5 + load_balance_score * 0.2)

            node_scores.append((node_id, final_score))

        # Select balanced set
        node_scores.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(len(node_scores), max(1, workload.priority // 4))
        selected_nodes = [node_id for node_id, _ in node_scores[:selected_count]]

        confidence = min(0.85, len(selected_nodes) / len(eligible_nodes))

        return selected_nodes, confidence

    async def _compliance_first_strategy(self, workload: WorkloadRequest, eligible_nodes: List[str]) -> Tuple[List[str], float]:
        """Compliance-first load balancing strategy."""
        # Prioritize compliance over other factors
        node_scores = []
        for node_id in eligible_nodes:
            node = self.nodes[node_id]

            # Compliance score (primary factor)
            compliance_score = 1.0 if self._check_compliance_requirements(node, workload) else 0.0

            # Secondary factors
            performance_score = (1 - node.cpu_usage) * node.health_score
            cost_score = 1 / max(node.cost_per_hour, 0.01)

            final_score = compliance_score * (performance_score * 0.6 + cost_score * 0.4)

            node_scores.append((node_id, final_score))

        # Select compliance-compliant nodes
        compliant_nodes = [(nid, score) for nid, score in node_scores if score > 0]
        compliant_nodes.sort(key=lambda x: x[1], reverse=True)

        selected_count = min(len(compliant_nodes), max(1, workload.priority // 3))
        selected_nodes = [node_id for node_id, _ in compliant_nodes[:selected_count]]

        confidence = min(0.9, len(selected_nodes) / len(eligible_nodes)) if selected_nodes else 0.0

        return selected_nodes, confidence

    def _calculate_latency_score(self, region: str, user_location: Dict[str, float]) -> float:
        """Calculate latency score between region and user location."""
        # Simplified latency calculation (in production, use actual latency data)
        region_coords = {
            'europe-west1': {'lat': 50.0, 'lng': 5.0},
            'us-central1': {'lat': 41.0, 'lng': -87.0},
            'asia-southeast1': {'lat': 1.0, 'lng': 104.0},
            'southamerica-east1': {'lat': -23.0, 'lng': -46.0}
        }

        if region not in region_coords:
            return 0.5

        region_loc = region_coords[region]
        distance = math.sqrt(
            (user_location['latitude'] - region_loc['lat']) ** 2 +
            (user_location['longitude'] - region_loc['lng']) ** 2
        )

        # Convert distance to latency score (closer = higher score)
        max_distance = 200  # Approximate max distance
        latency_score = max(0.1, 1 - (distance / max_distance))

        return latency_score

    def _calculate_recent_success_bonus(self, node_id: str) -> float:
        """Calculate bonus for nodes with recent successful workloads."""
        # Check recent history (simplified)
        recent_completions = [
            w for w in self.completed_workloads
            if hasattr(w, 'assigned_nodes') and node_id in getattr(w, 'assigned_nodes', [])
        ]

        if len(recent_completions) < 5:
            return 0.0

        # Calculate success rate
        success_rate = len([w for w in recent_completions if getattr(w, 'success', True)]) / len(recent_completions)

        return min(0.2, success_rate * 0.1)  # Max 20% bonus

    def _calculate_health_score(self, node: NodeMetrics) -> float:
        """Calculate overall health score for a node."""
        # Factors: uptime, resource usage, heartbeat freshness
        uptime_score = min(1.0, node.uptime_hours / 24)  # Better with more uptime

        resource_score = 1 - ((node.cpu_usage + node.memory_usage) / 2)  # Lower usage = healthier

        heartbeat_age = (datetime.now() - node.last_heartbeat).total_seconds()
        heartbeat_score = max(0.0, 1 - (heartbeat_age / 300))  # Fresh heartbeat = healthy

        health_score = (uptime_score * 0.3 + resource_score * 0.4 + heartbeat_score * 0.3)

        return max(0.0, min(1.0, health_score))

    def _calculate_node_cost(self, capacity: Dict[str, float]) -> float:
        """Calculate cost per hour for a node."""
        # Simplified cost calculation (in production, use actual pricing)
        base_cost = 0.1  # Base cost per hour

        # Factor in capacity
        cpu_cores = capacity.get('cpu_cores', 1)
        memory_gb = capacity.get('memory_gb', 1)
        has_gpu = capacity.get('gpu_available', False)

        cost = base_cost * cpu_cores * (memory_gb / 4)  # Scale with resources

        if has_gpu:
            cost *= 3  # GPUs are more expensive

        return cost

    def _estimate_cost(self, node_ids: List[str], workload: WorkloadRequest) -> float:
        """Estimate cost for processing workload on selected nodes."""
        total_cost = 0.0

        for node_id in node_ids:
            if node_id in self.nodes:
                node_cost = self.nodes[node_id].cost_per_hour
                total_cost += node_cost * workload.estimated_duration_hours

        return total_cost / len(node_ids) if node_ids else 0.0

    def _estimate_completion_time(self, node_ids: List[str], workload: WorkloadRequest) -> datetime:
        """Estimate completion time for workload."""
        if not node_ids:
            return datetime.now()

        # Simplified estimation based on node performance
        avg_performance = sum(
            self.nodes[node_id].reputation_score for node_id in node_ids
            if node_id in self.nodes
        ) / len(node_ids)

        # Estimate time based on workload complexity and node performance
        base_time_hours = workload.estimated_duration_hours
        adjusted_time = base_time_hours / max(0.1, avg_performance)

        return datetime.now() + timedelta(hours=adjusted_time)

    def _find_alternative_nodes(self, workload: WorkloadRequest, eligible_nodes: List[str], selected_nodes: List[str]) -> List[str]:
        """Find alternative nodes for failover."""
        alternatives = [node_id for node_id in eligible_nodes if node_id not in selected_nodes]

        # Sort by suitability
        alternatives.sort(key=lambda nid: self.nodes[nid].health_score, reverse=True)

        return alternatives[:3]  # Top 3 alternatives

    async def _assign_workload_to_nodes(self, workload: WorkloadRequest, node_ids: List[str]):
        """Assign workload to selected nodes."""
        self.processing_workloads[workload.request_id] = workload

        # Update node metrics
        for node_id in node_ids:
            if node_id in self.nodes:
                self.nodes[node_id].active_sessions += 1
                if workload.workload_type == 'training':
                    self.nodes[node_id].training_jobs += 1
                elif workload.workload_type == 'inference':
                    self.nodes[node_id].inference_jobs += 1

        self.logger.info(f"Assigned workload {workload.request_id} to nodes {node_ids}")

    async def _reassign_workloads_from_node(self, node_id: str):
        """Reassign workloads from a failing node."""
        # Find workloads on this node
        affected_workloads = [
            wid for wid, workload in self.processing_workloads.items()
            if hasattr(workload, 'assigned_nodes') and node_id in getattr(workload, 'assigned_nodes', [])
        ]

        for workload_id in affected_workloads:
            workload = self.processing_workloads[workload_id]

            # Try to reassign to alternative nodes
            decision = await self._make_load_balancing_decision(workload)

            if decision.selected_nodes:
                await self._assign_workload_to_nodes(workload, decision.selected_nodes)
                self.logger.info(f"Reassigned workload {workload_id} from {node_id} to {decision.selected_nodes}")
            else:
                # Put back in queue
                await self.pending_queue.put(workload)
                self.logger.warning(f"Could not reassign workload {workload_id}, put back in queue")

    async def _process_workload_queue(self):
        """Process pending workloads."""
        while True:
            try:
                workload = await self.pending_queue.get()

                # Workload already processed
                if workload.request_id in self.processing_workloads:
                    continue

                # Make load balancing decision
                decision = await self._make_load_balancing_decision(workload)

                if decision.selected_nodes:
                    await self._assign_workload_to_nodes(workload, decision.selected_nodes)
                else:
                    # No nodes available, put back with delay
                    await asyncio.sleep(5)
                    await self.pending_queue.put(workload)

            except Exception as e:
                self.logger.error(f"Error processing workload queue: {e}")
                await asyncio.sleep(1)

    async def _monitor_nodes(self):
        """Monitor node health and performance."""
        while True:
            try:
                current_time = datetime.now()

                for node_id, node in self.nodes.items():
                    # Check for stale nodes
                    heartbeat_age = (current_time - node.last_heartbeat).total_seconds()

                    if heartbeat_age > 300:  # 5 minutes
                        node.health_score *= 0.9  # Degrade health score

                    if heartbeat_age > 1800:  # 30 minutes
                        self.logger.warning(f"Node {node_id} has stale heartbeat ({heartbeat_age}s)")
                        node.health_score *= 0.5

                    if heartbeat_age > 3600:  # 1 hour
                        self.logger.error(f"Node {node_id} appears offline, unregistering")
                        await self.unregister_node(node_id)
                        break

                # Update performance metrics
                self._update_performance_metrics()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in node monitoring: {e}")
                await asyncio.sleep(60)

    async def _auto_scaling_loop(self):
        """Auto-scaling loop based on policies."""
        while True:
            try:
                await self._evaluate_scaling_policies()
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in auto-scaling loop: {e}")
                await asyncio.sleep(300)

    async def _evaluate_scaling_policies(self):
        """Evaluate and apply scaling policies."""
        for policy_name, policy in self.scaling_policies.items():
            try:
                metric = policy['metric']
                threshold_high = policy['threshold_high']
                threshold_low = policy['threshold_low']

                # Calculate current metric value
                current_value = self._calculate_global_metric(metric)

                if current_value > threshold_high:
                    # Scale up
                    await self._scale_up(policy)
                    self.logger.info(f"Scaling up due to {metric}: {current_value:.2f} > {threshold_high}")

                elif current_value < threshold_low:
                    # Scale down
                    await self._scale_down(policy)
                    self.logger.info(f"Scaling down due to {metric}: {current_value:.2f} < {threshold_low}")

            except Exception as e:
                self.logger.error(f"Error evaluating scaling policy {policy_name}: {e}")

    def _calculate_global_metric(self, metric: str) -> float:
        """Calculate global metric across all nodes."""
        if metric == 'cpu_usage':
            usages = [node.cpu_usage for node in self.nodes.values() if node.health_score > 0.5]
            return statistics.mean(usages) if usages else 0.0

        elif metric == 'memory_usage':
            usages = [node.memory_usage for node in self.nodes.values() if node.health_score > 0.5]
            return statistics.mean(usages) if usages else 0.0

        elif metric == 'queue_length':
            return self.pending_queue.qsize()

        return 0.0

    async def _scale_up(self, policy: Dict[str, Any]):
        """Scale up infrastructure."""
        scale_factor = policy['scale_up_factor']

        # Determine how many new nodes to add
        current_node_count = len([n for n in self.nodes.values() if n.health_score > 0.5])
        target_count = int(current_node_count * scale_factor)

        nodes_to_add = max(1, target_count - current_node_count)

        self.logger.info(f"Scaling up: adding {nodes_to_add} nodes")

        # In production, this would trigger GCP auto-scaling
        # For now, just log the scaling decision
        self.scaling_history.append({
            'timestamp': datetime.now(),
            'action': 'scale_up',
            'nodes_added': nodes_to_add,
            'reason': f"Policy: {policy['metric']} > {policy['threshold_high']}"
        })

    async def _scale_down(self, policy: Dict[str, Any]):
        """Scale down infrastructure."""
        scale_factor = policy['scale_down_factor']

        # Determine how many nodes to remove
        current_node_count = len([n for n in self.nodes.values() if n.health_score > 0.5])
        target_count = int(current_node_count * scale_factor)

        nodes_to_remove = max(0, current_node_count - target_count)

        if nodes_to_remove == 0:
            return

        self.logger.info(f"Scaling down: removing {nodes_to_remove} nodes")

        # Find least utilized nodes to remove
        node_utilization = [
            (node_id, (node.cpu_usage + node.memory_usage) / 2)
            for node_id, node in self.nodes.items()
            if node.health_score > 0.5
        ]

        node_utilization.sort(key=lambda x: x[1])  # Sort by utilization (ascending)

        nodes_to_remove_list = [node_id for node_id, _ in node_utilization[:nodes_to_remove]]

        # Remove nodes
        for node_id in nodes_to_remove_list:
            await self.unregister_node(node_id)

        self.scaling_history.append({
            'timestamp': datetime.now(),
            'action': 'scale_down',
            'nodes_removed': nodes_to_remove,
            'reason': f"Policy: {policy['metric']} < {policy['threshold_low']}"
        })

    async def _optimization_loop(self):
        """Continuous optimization loop."""
        while True:
            try:
                await self._optimize_workload_distribution()
                await self._optimize_cost_efficiency()
                await asyncio.sleep(1800)  # Optimize every 30 minutes

            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(1800)

    async def _optimize_workload_distribution(self):
        """Optimize workload distribution across nodes."""
        # Analyze current distribution
        node_workloads = {node_id: node.active_sessions for node_id, node in self.nodes.items()}

        if not node_workloads:
            return

        # Calculate imbalance
        avg_workload = statistics.mean(node_workloads.values())
        max_imbalance = max(abs(workload - avg_workload) for workload in node_workloads.values())

        if max_imbalance > 5:  # Significant imbalance
            self.logger.info(f"Detected workload imbalance: {max_imbalance:.1f}, rebalancing...")

            # Rebalance logic would go here
            # This could involve migrating workloads between nodes

    async def _optimize_cost_efficiency(self):
        """Optimize for cost efficiency."""
        # Analyze cost efficiency
        node_efficiency = {}
        for node_id, node in self.nodes.items():
            if node.cost_per_hour > 0:
                utilization = (node.cpu_usage + node.memory_usage) / 2
                efficiency = utilization / node.cost_per_hour
                node_efficiency[node_id] = efficiency

        if node_efficiency:
            avg_efficiency = statistics.mean(node_efficiency.values())
            low_efficiency_nodes = [
                node_id for node_id, eff in node_efficiency.items()
                if eff < avg_efficiency * 0.7
            ]

            if low_efficiency_nodes:
                self.logger.info(f"Found {len(low_efficiency_nodes)} low-efficiency nodes, considering shutdown")

    def _update_performance_metrics(self):
        """Update global performance metrics."""
        current_time = datetime.now()

        # Calculate various metrics
        healthy_nodes = [node for node in self.nodes.values() if node.health_score > 0.7]
        total_nodes = len(self.nodes)

        if healthy_nodes:
            avg_cpu = statistics.mean(node.cpu_usage for node in healthy_nodes)
            avg_memory = statistics.mean(node.memory_usage for node in healthy_nodes)
            avg_health = statistics.mean(node.health_score for node in healthy_nodes)

            self.performance_metrics = {
                'timestamp': current_time,
                'total_nodes': total_nodes,
                'healthy_nodes': len(healthy_nodes),
                'avg_cpu_usage': avg_cpu,
                'avg_memory_usage': avg_memory,
                'avg_health_score': avg_health,
                'pending_workloads': self.pending_queue.qsize(),
                'active_workloads': len(self.processing_workloads)
            }

            # Calculate cost metrics
            total_cost_per_hour = sum(node.cost_per_hour for node in healthy_nodes)
            self.cost_metrics = {
                'timestamp': current_time,
                'total_hourly_cost': total_cost_per_hour,
                'cost_per_healthy_node': total_cost_per_hour / len(healthy_nodes) if healthy_nodes else 0,
                'utilization_efficiency': (avg_cpu + avg_memory) / 2
            }

    def get_load_balancer_status(self) -> Dict[str, Any]:
        """Get comprehensive load balancer status."""
        return {
            'nodes': {
                node_id: {
                    'region': node.region,
                    'cpu_usage': node.cpu_usage,
                    'memory_usage': node.memory_usage,
                    'gpu_usage': node.gpu_usage,
                    'active_sessions': node.active_sessions,
                    'health_score': node.health_score,
                    'cost_per_hour': node.cost_per_hour
                }
                for node_id, node in self.nodes.items()
            },
            'workloads': {
                'pending': self.pending_queue.qsize(),
                'processing': len(self.processing_workloads),
                'completed_recent': len(self.completed_workloads)
            },
            'performance': self.performance_metrics,
            'costs': self.cost_metrics,
            'scaling': {
                'policies': self.scaling_policies,
                'recent_actions': list(self.scaling_history)[-10:]  # Last 10 actions
            }
        }

    def get_workload_distribution(self) -> Dict[str, Any]:
        """Get workload distribution analytics."""
        distribution = {
            'by_region': defaultdict(int),
            'by_workload_type': defaultdict(int),
            'by_priority': defaultdict(int),
            'queue_wait_times': [],
            'completion_times': []
        }

        # Analyze current workloads
        for workload in self.processing_workloads.values():
            if hasattr(workload, 'assigned_nodes'):
                for node_id in getattr(workload, 'assigned_nodes', []):
                    if node_id in self.node_regions:
                        distribution['by_region'][self.node_regions[node_id]] += 1

            distribution['by_workload_type'][workload.workload_type] += 1
            distribution['by_priority'][workload.priority] += 1

        # Analyze completed workloads for timing metrics
        for workload in self.completed_workloads:
            if hasattr(workload, 'queue_time') and hasattr(workload, 'completion_time'):
                wait_time = (getattr(workload, 'start_time', datetime.now()) - getattr(workload, 'queue_time', datetime.now())).total_seconds()
                completion_time = (getattr(workload, 'completion_time', datetime.now()) - getattr(workload, 'start_time', datetime.now())).total_seconds()

                distribution['queue_wait_times'].append(wait_time)
                distribution['completion_times'].append(completion_time)

        # Calculate averages
        if distribution['queue_wait_times']:
            distribution['avg_queue_wait_seconds'] = statistics.mean(distribution['queue_wait_times'])
        if distribution['completion_times']:
            distribution['avg_completion_seconds'] = statistics.mean(distribution['completion_times'])

        return dict(distribution)