"""
Google Cloud Platform integration for Ailoos federated learning.
Provides enterprise-grade infrastructure components including GKE, Cloud Storage, BigQuery, and monitoring.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import base64

from google.cloud import storage, bigquery, secretmanager, monitoring_v3, monitoring_dashboard_v1
from google.cloud import container_v1, functions_v2, run_v2
from google.api_core.exceptions import GoogleAPIError
from kubernetes import client, config

from ...core.config import Config
from ...utils.logging import AiloosLogger


@dataclass
class GCPCluster:
    """GCP Kubernetes cluster configuration."""
    name: str
    region: str
    node_count: int
    machine_type: str
    gpu_type: Optional[str] = None
    gpu_count: Optional[int] = None
    status: str = "PROVISIONING"


@dataclass
class GCPStorageBucket:
    """Cloud Storage bucket for datasets and models."""
    name: str
    region: str
    storage_class: str
    encryption: str
    lifecycle_rules: List[Dict[str, Any]]


@dataclass
class GCPDataset:
    """BigQuery dataset for analytics and auditing."""
    dataset_id: str
    location: str
    description: str
    tables: List[str]


@dataclass
class GCPFunction:
    """Cloud Function for serverless processing."""
    name: str
    region: str
    runtime: str
    entry_point: str
    source_bucket: str
    trigger_type: str
    trigger_resource: Optional[str] = None


class GCPIntegration:
    """Main GCP integration manager for Ailoos infrastructure."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = AiloosLogger(__name__)

        # GCP project and authentication
        self.project_id = config.get('gcp_project_id', os.getenv('GCP_PROJECT_ID'))
        self.region = config.get('gcp_region', 'europe-west1')

        # Initialize GCP clients
        self._init_gcp_clients()

        # Infrastructure components
        self.clusters: Dict[str, GCPCluster] = {}
        self.buckets: Dict[str, GCPStorageBucket] = {}
        self.datasets: Dict[str, GCPDataset] = {}
        self.functions: Dict[str, GCPFunction] = {}

        # Kubernetes client (initialized when needed)
        self.k8s_client = None

    def _init_gcp_clients(self):
        """Initialize GCP service clients."""
        try:
            # Storage client for Cloud Storage
            self.storage_client = storage.Client(project=self.project_id)

            # BigQuery client
            self.bq_client = bigquery.Client(project=self.project_id)

            # Secret Manager client
            self.secret_client = secretmanager.SecretManagerServiceClient()

            # Monitoring client
            self.monitoring_client = monitoring_v3.MetricServiceClient()

            # Container (GKE) client
            self.container_client = container_v1.ClusterManagerClient()

            # Cloud Functions client
            self.functions_client = functions_v2.FunctionServiceClient()

            # Cloud Run client
            self.run_client = run_v2.ServicesClient()

            self.logger.info("GCP clients initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize GCP clients: {e}")
            raise

    async def create_gke_cluster(self, cluster_config: Dict[str, Any]) -> GCPCluster:
        """Create a GKE cluster for federated learning workloads."""
        try:
            cluster_name = cluster_config['name']
            region = cluster_config.get('region', self.region)

            # Define cluster
            cluster = container_v1.Cluster()
            cluster.name = cluster_name
            cluster.initial_node_count = cluster_config.get('node_count', 3)

            # Node configuration
            node_config = container_v1.NodeConfig()
            node_config.machine_type = cluster_config.get('machine_type', 'n1-standard-4')

            # GPU configuration if specified
            if 'gpu_type' in cluster_config:
                accelerator = container_v1.AcceleratorConfig()
                accelerator.accelerator_type = cluster_config['gpu_type']
                accelerator.accelerator_count = cluster_config.get('gpu_count', 1)
                node_config.accelerators.append(accelerator)

            cluster.node_config = node_config

            # Create cluster request
            request = container_v1.CreateClusterRequest(
                parent=f"projects/{self.project_id}/locations/{region}",
                cluster=cluster
            )

            # Create cluster
            operation = self.container_client.create_cluster(request=request)
            self.logger.info(f"Creating GKE cluster {cluster_name} in {region}...")

            # Wait for completion (simplified)
            result = operation.result(timeout=600)  # 10 minutes timeout

            # Create GCPCluster object
            gcp_cluster = GCPCluster(
                name=cluster_name,
                region=region,
                node_count=cluster.initial_node_count,
                machine_type=node_config.machine_type,
                gpu_type=cluster_config.get('gpu_type'),
                gpu_count=cluster_config.get('gpu_count'),
                status="RUNNING"
            )

            self.clusters[cluster_name] = gcp_cluster

            # Initialize Kubernetes client for the cluster
            await self._init_k8s_client(cluster_name, region)

            self.logger.info(f"GKE cluster {cluster_name} created successfully")
            return gcp_cluster

        except GoogleAPIError as e:
            self.logger.error(f"GCP API error creating cluster: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating GKE cluster: {e}")
            raise

    async def _init_k8s_client(self, cluster_name: str, region: str):
        """Initialize Kubernetes client for GKE cluster."""
        try:
            # Get cluster details
            cluster_request = container_v1.GetClusterRequest(
                name=f"projects/{self.project_id}/locations/{region}/clusters/{cluster_name}"
            )
            cluster = self.container_client.get_cluster(request=cluster_request)

            # Configure Kubernetes client
            config.load_kube_config_from_dict({
                'apiVersion': 'v1',
                'clusters': [{
                    'cluster': {
                        'certificate-authority-data': cluster.master_auth.cluster_ca_certificate,
                        'server': f"https://{cluster.endpoint}"
                    },
                    'name': cluster_name
                }],
                'contexts': [{
                    'context': {
                        'cluster': cluster_name,
                        'user': cluster_name
                    },
                    'name': cluster_name
                }],
                'current-context': cluster_name,
                'kind': 'Config',
                'preferences': {},
                'users': [{
                    'name': cluster_name,
                    'user': {
                        'auth-provider': {
                            'config': {
                                'cmd-args': 'config config-helper --format=json',
                                'cmd-path': 'gcloud',
                                'expiry-key': '{.credential.token_expiry}',
                                'token-key': '{.credential.access_token}'
                            },
                            'name': 'gcp'
                        }
                    }
                }]
            })

            self.k8s_client = client.ApiClient()
            self.logger.info(f"Kubernetes client initialized for cluster {cluster_name}")

        except Exception as e:
            self.logger.error(f"Error initializing Kubernetes client: {e}")
            raise

    async def deploy_federated_coordinator(self, cluster_name: str, config: Dict[str, Any]):
        """Deploy federated learning coordinator to GKE cluster."""
        try:
            if not self.k8s_client:
                await self._init_k8s_client(cluster_name, self.region)

            # Create namespace
            namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name="ailoos"))
            self.k8s_client.call_api(
                '/api/v1/namespaces', 'POST',
                body=namespace, auth_settings=['BearerToken']
            )

            # Deploy coordinator deployment
            coordinator_deployment = self._create_coordinator_deployment(config)
            apps_v1 = client.AppsV1Api(self.k8s_client)
            apps_v1.create_namespaced_deployment(
                namespace="ailoos",
                body=coordinator_deployment
            )

            # Deploy coordinator service
            coordinator_service = self._create_coordinator_service()
            core_v1 = client.CoreV1Api(self.k8s_client)
            core_v1.create_namespaced_service(
                namespace="ailoos",
                body=coordinator_service
            )

            # Deploy Redis for coordination
            redis_deployment = self._create_redis_deployment()
            apps_v1.create_namespaced_deployment(
                namespace="ailoos",
                body=redis_deployment
            )

            redis_service = self._create_redis_service()
            core_v1.create_namespaced_service(
                namespace="ailoos",
                body=redis_service
            )

            self.logger.info(f"Federated coordinator deployed to cluster {cluster_name}")

        except Exception as e:
            self.logger.error(f"Error deploying coordinator: {e}")
            raise

    def _create_coordinator_deployment(self, config: Dict[str, Any]) -> client.V1Deployment:
        """Create Kubernetes deployment for federated coordinator."""
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name="federated-coordinator"),
            spec=client.V1DeploymentSpec(
                replicas=config.get('replicas', 1),
                selector=client.V1LabelSelector(
                    match_labels={"app": "federated-coordinator"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": "federated-coordinator"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name="coordinator",
                            image=config.get('image', 'gcr.io/ailoos/federated-coordinator:latest'),
                            ports=[client.V1ContainerPort(container_port=5000)],
                            env=[
                                client.V1EnvVar(name="REDIS_URL", value="redis://redis-service:6379"),
                                client.V1EnvVar(name="GCP_PROJECT", value=self.project_id),
                                client.V1EnvVar(name="GCP_REGION", value=self.region)
                            ],
                            resources=client.V1ResourceRequirements(
                                requests={
                                    "cpu": config.get('cpu_request', '500m'),
                                    "memory": config.get('memory_request', '1Gi')
                                },
                                limits={
                                    "cpu": config.get('cpu_limit', '2000m'),
                                    "memory": config.get('memory_limit', '4Gi')
                                }
                            )
                        )]
                    )
                )
            )
        )
        return deployment

    def _create_coordinator_service(self) -> client.V1Service:
        """Create Kubernetes service for federated coordinator."""
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name="coordinator-service"),
            spec=client.V1ServiceSpec(
                selector={"app": "federated-coordinator"},
                ports=[client.V1ServicePort(
                    port=5000,
                    target_port=5000,
                    protocol="TCP"
                )],
                type="LoadBalancer"
            )
        )
        return service

    def _create_redis_deployment(self) -> client.V1Deployment:
        """Create Redis deployment for coordination."""
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name="redis"),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": "redis"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": "redis"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name="redis",
                            image="redis:7-alpine",
                            ports=[client.V1ContainerPort(container_port=6379)],
                            resources=client.V1ResourceRequirements(
                                requests={"cpu": "100m", "memory": "128Mi"},
                                limits={"cpu": "500m", "memory": "512Mi"}
                            )
                        )]
                    )
                )
            )
        )
        return deployment

    def _create_redis_service(self) -> client.V1Service:
        """Create Redis service."""
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name="redis-service"),
            spec=client.V1ServiceSpec(
                selector={"app": "redis"},
                ports=[client.V1ServicePort(
                    port=6379,
                    target_port=6379,
                    protocol="TCP"
                )]
            )
        )
        return service

    async def create_storage_bucket(self, bucket_config: Dict[str, Any]) -> GCPStorageBucket:
        """Create Cloud Storage bucket for datasets and models."""
        try:
            bucket_name = bucket_config['name']
            region = bucket_config.get('region', self.region)
            storage_class = bucket_config.get('storage_class', 'STANDARD')

            # Create bucket
            bucket = self.storage_client.bucket(bucket_name)
            bucket.storage_class = storage_class
            bucket.location = region
            bucket.create()

            # Configure lifecycle rules
            lifecycle_rules = bucket_config.get('lifecycle_rules', [])
            if lifecycle_rules:
                bucket.lifecycle_rules = lifecycle_rules
                bucket.patch()

            # Configure encryption
            encryption = bucket_config.get('encryption', 'google-managed')
            if encryption == 'customer-managed':
                # Configure customer-managed encryption
                pass  # Implementation would require KMS key

            gcp_bucket = GCPStorageBucket(
                name=bucket_name,
                region=region,
                storage_class=storage_class,
                encryption=encryption,
                lifecycle_rules=lifecycle_rules
            )

            self.buckets[bucket_name] = gcp_bucket

            # Create standard folders
            self._create_bucket_folders(bucket_name)

            self.logger.info(f"Cloud Storage bucket {bucket_name} created")
            return gcp_bucket

        except GoogleAPIError as e:
            self.logger.error(f"GCP API error creating bucket: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating storage bucket: {e}")
            raise

    def _create_bucket_folders(self, bucket_name: str):
        """Create standard folder structure in bucket."""
        bucket = self.storage_client.bucket(bucket_name)

        folders = [
            'datasets/',
            'models/',
            'checkpoints/',
            'logs/',
            'backups/',
            'temp/'
        ]

        for folder in folders:
            blob = bucket.blob(folder)
            blob.upload_from_string('', content_type='application/x-www-form-urlencoded')

    async def upload_dataset_to_gcs(self, bucket_name: str, dataset_path: str, dataset_name: str):
        """Upload dataset to Cloud Storage."""
        try:
            bucket = self.storage_client.bucket(bucket_name)

            # Upload dataset file(s)
            if os.path.isfile(dataset_path):
                blob = bucket.blob(f'datasets/{dataset_name}')
                blob.upload_from_filename(dataset_path)
                self.logger.info(f"Uploaded dataset {dataset_name} to gs://{bucket_name}/datasets/")
            else:
                # Upload directory
                for root, dirs, files in os.walk(dataset_path):
                    for file in files:
                        local_path = os.path.join(root, file)
                        relative_path = os.path.relpath(local_path, dataset_path)
                        blob_path = f'datasets/{dataset_name}/{relative_path}'
                        blob = bucket.blob(blob_path)
                        blob.upload_from_filename(local_path)

                self.logger.info(f"Uploaded dataset directory {dataset_name} to gs://{bucket_name}/datasets/")

        except Exception as e:
            self.logger.error(f"Error uploading dataset to GCS: {e}")
            raise

    async def create_bigquery_dataset(self, dataset_config: Dict[str, Any]) -> GCPDataset:
        """Create BigQuery dataset for analytics and auditing."""
        try:
            dataset_id = dataset_config['dataset_id']
            location = dataset_config.get('location', self.region)
            description = dataset_config.get('description', 'Ailoos analytics dataset')

            # Create dataset
            dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
            dataset.location = location
            dataset.description = description

            dataset = self.bq_client.create_dataset(dataset)

            # Create standard tables
            tables_config = dataset_config.get('tables', [])
            created_tables = []

            for table_config in tables_config:
                table_id = table_config['table_id']
                schema = table_config.get('schema', [])

                table = bigquery.Table(f"{self.project_id}.{dataset_id}.{table_id}", schema=schema)
                table.description = table_config.get('description', '')

                self.bq_client.create_table(table)
                created_tables.append(table_id)

            gcp_dataset = GCPDataset(
                dataset_id=dataset_id,
                location=location,
                description=description,
                tables=created_tables
            )

            self.datasets[dataset_id] = gcp_dataset

            self.logger.info(f"BigQuery dataset {dataset_id} created with {len(created_tables)} tables")
            return gcp_dataset

        except GoogleAPIError as e:
            self.logger.error(f"GCP API error creating dataset: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating BigQuery dataset: {e}")
            raise

    async def create_cloud_function(self, function_config: Dict[str, Any]) -> GCPFunction:
        """Create Cloud Function for serverless processing."""
        try:
            function_name = function_config['name']
            region = function_config.get('region', self.region)
            runtime = function_config.get('runtime', 'python39')
            entry_point = function_config['entry_point']
            source_bucket = function_config['source_bucket']
            trigger_type = function_config['trigger_type']

            # Create function
            function = functions_v2.Function()
            function.name = f"projects/{self.project_id}/locations/{region}/functions/{function_name}"
            function.runtime = runtime
            function.entry_point = entry_point

            # Source code
            source = functions_v2.Source()
            storage_source = functions_v2.StorageSource()
            storage_source.bucket = source_bucket
            storage_source.object = function_config.get('source_object', f'{function_name}.zip')
            source.storage_source = storage_source
            function.source = source

            # Trigger configuration
            if trigger_type == 'http':
                function.https_trigger = functions_v2.HttpsTrigger()
            elif trigger_type == 'pubsub':
                event_trigger = functions_v2.EventTrigger()
                event_trigger.event_type = 'google.cloud.pubsub.topic.v1.messagePublished'
                event_trigger.resource = function_config.get('trigger_resource', '')
                function.event_trigger = event_trigger

            # Create function request
            request = functions_v2.CreateFunctionRequest(
                parent=f"projects/{self.project_id}/locations/{region}",
                function=function
            )

            operation = self.functions_client.create_function(request=request)
            result = operation.result(timeout=300)  # 5 minutes timeout

            gcp_function = GCPFunction(
                name=function_name,
                region=region,
                runtime=runtime,
                entry_point=entry_point,
                source_bucket=source_bucket,
                trigger_type=trigger_type,
                trigger_resource=function_config.get('trigger_resource')
            )

            self.functions[function_name] = gcp_function

            self.logger.info(f"Cloud Function {function_name} created successfully")
            return gcp_function

        except GoogleAPIError as e:
            self.logger.error(f"GCP API error creating function: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating Cloud Function: {e}")
            raise

    async def setup_monitoring(self):
        """Setup Cloud Monitoring for Ailoos infrastructure."""
        try:
            # Create custom metrics
            await self._create_custom_metrics()

            # Setup dashboards
            await self._create_monitoring_dashboards()

            # Configure alerts
            await self._create_alert_policies()

            self.logger.info("Cloud Monitoring setup completed")

        except Exception as e:
            self.logger.error(f"Error setting up monitoring: {e}")
            raise

    async def _create_custom_metrics(self):
        """Create custom metrics for Ailoos monitoring."""
        metrics = [
            {
                'name': 'ailoos/nodes_active',
                'description': 'Number of active federated learning nodes',
                'unit': '1',
                'type': 'GAUGE'
            },
            {
                'name': 'ailoos/training_sessions',
                'description': 'Number of active training sessions',
                'unit': '1',
                'type': 'GAUGE'
            },
            {
                'name': 'ailoos/model_accuracy',
                'description': 'Model accuracy during training',
                'unit': '%',
                'type': 'GAUGE'
            },
            {
                'name': 'ailoos/drachma_distributed',
                'description': 'DRACMA tokens distributed',
                'unit': '1',
                'type': 'CUMULATIVE'
            }
        ]

        for metric in metrics:
            # Create metric descriptor
            descriptor = monitoring_v3.MetricDescriptor()
            descriptor.name = f"projects/{self.project_id}/metricDescriptors/custom.googleapis.com/{metric['name']}"
            descriptor.description = metric['description']
            descriptor.unit = metric['unit']
            descriptor.type = f"custom.googleapis.com/{metric['name']}"
            descriptor.metric_kind = metric['type']
            descriptor.value_type = 'DOUBLE'

            self.monitoring_client.create_metric_descriptor(
                name=f"projects/{self.project_id}",
                metric_descriptor=descriptor
            )

    async def _create_monitoring_dashboards(self):
        """Create monitoring dashboards for Ailoos."""
        try:
            from google.cloud import monitoring_dashboard_v1

            dashboard_client = monitoring_dashboard_v1.DashboardsServiceClient()

            # Create main Ailoos dashboard
            dashboard = monitoring_dashboard_v1.Dashboard()
            dashboard.display_name = "Ailoos Federated Learning"
            dashboard.description = "Comprehensive monitoring dashboard for Ailoos federated learning infrastructure"

            # Add widgets for key metrics
            widgets = []

            # Active nodes gauge
            gauge_widget = monitoring_dashboard_v1.Widget()
            gauge_widget.title = "Active Federated Nodes"
            gauge_chart = monitoring_dashboard_v1.XyChart()
            gauge_chart.data_sets.append(self._create_data_set("custom.googleapis.com/ailoos/nodes_active"))
            gauge_widget.xy_chart = gauge_chart
            widgets.append(gauge_widget)

            # Training sessions chart
            sessions_widget = monitoring_dashboard_v1.Widget()
            sessions_widget.title = "Training Sessions Over Time"
            sessions_chart = monitoring_dashboard_v1.XyChart()
            sessions_chart.data_sets.append(self._create_data_set("custom.googleapis.com/ailoos/training_sessions"))
            sessions_widget.xy_chart = sessions_chart
            widgets.append(sessions_widget)

            # Model accuracy chart
            accuracy_widget = monitoring_dashboard_v1.Widget()
            accuracy_widget.title = "Model Accuracy Trends"
            accuracy_chart = monitoring_dashboard_v1.XyChart()
            accuracy_chart.data_sets.append(self._create_data_set("custom.googleapis.com/ailoos/model_accuracy"))
            accuracy_widget.xy_chart = accuracy_chart
            widgets.append(accuracy_widget)

            # DRACMA distribution chart
            dracma_widget = monitoring_dashboard_v1.Widget()
            dracma_widget.title = "DRACMA Token Distribution"
            dracma_chart = monitoring_dashboard_v1.XyChart()
            dracma_chart.data_sets.append(self._create_data_set("custom.googleapis.com/ailoos/drachma_distributed"))
            dracma_widget.xy_chart = dracma_chart
            widgets.append(dracma_widget)

            # System health scorecard
            health_widget = monitoring_dashboard_v1.Widget()
            health_widget.title = "System Health Scorecard"
            scorecard = monitoring_dashboard_v1.Scorecard()
            scorecard.thresholds.append(self._create_threshold("custom.googleapis.com/ailoos/nodes_active", 10))
            health_widget.scorecard = scorecard
            widgets.append(health_widget)

            # Error rate chart
            error_widget = monitoring_dashboard_v1.Widget()
            error_widget.title = "Error Rate Monitoring"
            error_chart = monitoring_dashboard_v1.XyChart()
            error_chart.data_sets.append(self._create_data_set("custom.googleapis.com/ailoos/error_rate"))
            error_widget.xy_chart = error_chart
            widgets.append(error_widget)

            dashboard.grid_layout.widgets.extend(widgets)

            # Create dashboard request
            request = monitoring_dashboard_v1.CreateDashboardRequest(
                parent=f"projects/{self.project_id}",
                dashboard=dashboard
            )

            created_dashboard = dashboard_client.create_dashboard(request=request)
            self.logger.info(f"Monitoring dashboard created: {created_dashboard.name}")

        except Exception as e:
            self.logger.error(f"Error creating monitoring dashboards: {e}")
            raise

    def _create_data_set(self, metric_name: str) -> monitoring_dashboard_v1.XyChart.DataSet:
        """Create data set for dashboard chart."""
        from google.cloud import monitoring_dashboard_v1

        data_set = monitoring_dashboard_v1.XyChart.DataSet()
        data_set.time_series_query = monitoring_dashboard_v1.TimeSeriesQuery()
        data_set.time_series_query.time_series_filter = monitoring_dashboard_v1.TimeSeriesFilter()
        data_set.time_series_query.time_series_filter.metric_type = metric_name
        return data_set

    def _create_threshold(self, metric_name: str, value: float) -> monitoring_dashboard_v1.Scorecard.Threshold:
        """Create threshold for scorecard widget."""
        from google.cloud import monitoring_dashboard_v1

        threshold = monitoring_dashboard_v1.Scorecard.Threshold()
        threshold.value = value
        threshold.color = "RED" if value < 10 else "GREEN"
        return threshold

    async def _create_alert_policies(self):
        """Create alert policies for critical events."""
        alerts = [
            {
                'name': 'node_failure_alert',
                'condition': 'nodes_active < 10',
                'description': 'Critical: Low number of active nodes'
            },
            {
                'name': 'training_stalled_alert',
                'condition': 'training_sessions == 0',
                'description': 'Warning: No active training sessions'
            },
            {
                'name': 'high_error_rate_alert',
                'condition': 'error_rate > 0.05',
                'description': 'Warning: High error rate detected'
            }
        ]

        for alert in alerts:
            # Create alert policy
            policy = monitoring_v3.AlertPolicy()
            policy.display_name = alert['name']
            policy.documentation = monitoring_v3.Documentation(content=alert['description'])

            # Add condition (simplified)
            condition = monitoring_v3.AlertPolicy.Condition()
            condition.display_name = alert['name']
            # Condition configuration would be more complex in practice

            policy.conditions.append(condition)

            self.monitoring_client.create_alert_policy(
                name=f"projects/{self.project_id}",
                alert_policy=policy
            )

    async def store_secret(self, secret_id: str, secret_value: str):
        """Store secret in Secret Manager."""
        try:
            # Create secret
            secret = secretmanager.Secret()
            secret.replication.automatic = secretmanager.Replication.Automatic()

            secret_request = secretmanager.CreateSecretRequest(
                parent=f"projects/{self.project_id}",
                secret_id=secret_id,
                secret=secret
            )

            created_secret = self.secret_client.create_secret(request=secret_request)

            # Add secret version
            payload = secret_value.encode('UTF-8')
            version_request = secretmanager.AddSecretVersionRequest(
                parent=created_secret.name,
                payload={'data': payload}
            )

            self.secret_client.add_secret_version(request=version_request)

            self.logger.info(f"Secret {secret_id} stored in Secret Manager")

        except Exception as e:
            self.logger.error(f"Error storing secret: {e}")
            raise

    async def get_secret(self, secret_id: str) -> str:
        """Retrieve secret from Secret Manager."""
        try:
            # Get latest version
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.secret_client.access_secret_version(name=name)

            secret_value = response.payload.data.decode('UTF-8')
            return secret_value

        except Exception as e:
            self.logger.error(f"Error retrieving secret: {e}")
            raise

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get status of all GCP infrastructure components."""
        return {
            'clusters': {name: cluster.__dict__ for name, cluster in self.clusters.items()},
            'buckets': {name: bucket.__dict__ for name, bucket in self.buckets.items()},
            'datasets': {name: dataset.__dict__ for name, dataset in self.datasets.items()},
            'functions': {name: function.__dict__ for name, function in self.functions.items()},
            'project_id': self.project_id,
            'region': self.region
        }