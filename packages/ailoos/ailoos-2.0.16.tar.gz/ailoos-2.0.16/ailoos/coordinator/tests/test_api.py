"""
Integration tests for the coordinator API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
import json

from ..main import create_application
from ..database.connection import get_db, create_tables, reset_database
from ..auth.dependencies import create_node_token, create_admin_token
from ..models.base import Node, FederatedSession


@pytest.fixture
async def client():
    """Create test client."""
    app = create_application()
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def db_session():
    """Create test database session."""
    # Reset database for tests
    reset_database()
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def test_node(db_session: Session):
    """Create test node."""
    node = Node(
        id="test-node-001",
        public_key="test-public-key",
        status="active",
        reputation_score=0.8,
        trust_level="verified",
        is_verified=True
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return node


@pytest.fixture
async def test_session(db_session: Session, test_node: Node):
    """Create test session."""
    session = FederatedSession(
        id="test-session-001",
        name="Test Session",
        description="Test federated learning session",
        model_type="neural_network",
        min_nodes=2,
        max_nodes=10,
        total_rounds=5,
        coordinator_node_id=test_node.id
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def node_token(test_node: Node):
    """Create node JWT token."""
    return create_node_token(test_node.id, test_node.public_key, test_node.trust_level)


@pytest.fixture
def admin_token():
    """Create admin JWT token."""
    return create_admin_token("admin-001", "test-admin", ["admin"], ["all"])


class TestSessionAPI:
    """Test session API endpoints."""

    async def test_list_sessions(self, client: AsyncClient, node_token: str):
        """Test listing sessions."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/sessions/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    async def test_create_session(self, client: AsyncClient, admin_token: str, test_node: Node):
        """Test creating a session."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        session_data = {
            "id": "new-session-001",
            "name": "New Test Session",
            "description": "A new test session",
            "model_type": "neural_network",
            "min_nodes": 2,
            "max_nodes": 10,
            "total_rounds": 5
        }

        response = await client.post(
            "/api/v1/sessions/",
            json=session_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "new-session-001"

    async def test_get_session(self, client: AsyncClient, node_token: str, test_session: FederatedSession):
        """Test getting a specific session."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get(f"/api/v1/sessions/{test_session.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_session.id

    async def test_start_session(self, client: AsyncClient, admin_token: str, test_session: FederatedSession):
        """Test starting a session."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(f"/api/v1/sessions/{test_session.id}/start", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestModelAPI:
    """Test model API endpoints."""

    async def test_list_models(self, client: AsyncClient, node_token: str):
        """Test listing models."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/models/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_create_model(self, client: AsyncClient, admin_token: str, test_session: FederatedSession):
        """Test creating a model."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        model_data = {
            "id": "new-model-001",
            "name": "Test Model",
            "version": "1.0.0",
            "model_type": "neural_network",
            "session_id": test_session.id,
            "is_public": False
        }

        response = await client.post(
            "/api/v1/models/",
            json=model_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "new-model-001"


class TestContributionAPI:
    """Test contribution API endpoints."""

    async def test_list_contributions(self, client: AsyncClient, node_token: str):
        """Test listing contributions."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/contributions/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_create_contribution(self, client: AsyncClient, node_token: str, test_session: FederatedSession, test_node: Node):
        """Test creating a contribution."""
        headers = {"Authorization": f"Bearer {node_token}"}
        contribution_data = {
            "session_id": test_session.id,
            "node_id": test_node.id,
            "round_number": 1,
            "parameters_trained": 10000,
            "data_samples_used": 1000,
            "training_time_seconds": 300.0,
            "model_accuracy": 0.85
        }

        response = await client.post(
            "/api/v1/contributions/",
            json=contribution_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestRewardAPI:
    """Test reward API endpoints."""

    async def test_list_rewards(self, client: AsyncClient, node_token: str):
        """Test listing reward transactions."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/rewards/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_get_my_rewards(self, client: AsyncClient, node_token: str):
        """Test getting current node's rewards."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/rewards/my-rewards", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAdminAPI:
    """Test admin API endpoints."""

    async def test_get_system_stats(self, client: AsyncClient, admin_token: str):
        """Test getting system statistics."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/v1/admin/stats", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    async def test_get_audit_logs(self, client: AsyncClient, admin_token: str):
        """Test getting audit logs."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/v1/admin/audit-logs", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestHealthCheck:
    """Test health check endpoint."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ailoos-coordinator"


class TestAuthentication:
    """Test authentication and authorization."""

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/sessions/")

        assert response.status_code == 401

    async def test_invalid_token(self, client: AsyncClient):
        """Test accessing with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/sessions/", headers=headers)

        assert response.status_code == 401

    async def test_admin_only_endpoint(self, client: AsyncClient, node_token: str):
        """Test accessing admin-only endpoint with node token."""
        headers = {"Authorization": f"Bearer {node_token}"}
        response = await client.get("/api/v1/admin/stats", headers=headers)

        assert response.status_code == 403