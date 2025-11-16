"""
Example test file for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main_api import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# Add more tests for extract, index, chat endpoints
# Example:
# def test_extract():
#     with open("test_file.pdf", "rb") as f:
#         response = client.post(
#             "/extract/",
#             files={"file": ("test.pdf", f, "application/pdf")}
#         )
#     assert response.status_code == 200
