import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Returns a FastAPI TestClient.
    """
    with TestClient(app) as client:
        yield client