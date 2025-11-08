"""Tests for FastApps widget functionality."""


def test_widget_data_structure(sample_widget_data):
    """Test widget data structure."""
    assert isinstance(sample_widget_data, dict)
    assert "message" in sample_widget_data
    assert sample_widget_data["message"] == "Hello, World!"
    assert sample_widget_data["status"] == "ok"


def test_widget_data_keys(sample_widget_data):
    """Test widget data has expected keys."""
    assert "message" in sample_widget_data
    assert "status" in sample_widget_data
    assert len(sample_widget_data) == 2
