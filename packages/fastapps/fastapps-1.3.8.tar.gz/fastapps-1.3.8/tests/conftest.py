import pytest


@pytest.fixture
def mock_server():
    """Mock server configuration for testing."""
    return {"host": "localhost", "port": 8000, "reload": False}


@pytest.fixture
def sample_widget_data():
    """Sample widget data for testing."""
    return {"message": "Hello, World!", "status": "ok"}
