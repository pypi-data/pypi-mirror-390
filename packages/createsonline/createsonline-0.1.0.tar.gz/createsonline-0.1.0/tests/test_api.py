"""
Tests for the API application.
"""
import pytest

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["framework"] == "CREATESONLINE"
    assert response.json()["status"] == "operational"

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
