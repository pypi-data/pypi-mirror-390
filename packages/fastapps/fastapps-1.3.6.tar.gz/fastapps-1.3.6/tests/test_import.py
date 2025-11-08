"""Test basic package structure and imports."""


def test_package_structure():
    """Test that package directory exists."""
    import os

    package_dir = os.path.join(os.path.dirname(__file__), "..", "fastapps")
    assert os.path.exists(package_dir)
    assert os.path.isdir(package_dir)


def test_module_files_exist():
    """Test that core module files exist."""
    import os

    base_dir = os.path.join(os.path.dirname(__file__), "..", "fastapps")

    # Check core files exist
    assert os.path.exists(os.path.join(base_dir, "__init__.py"))
    assert os.path.exists(os.path.join(base_dir, "core"))
    assert os.path.exists(os.path.join(base_dir, "cli"))
    assert os.path.exists(os.path.join(base_dir, "auth"))


def test_pyproject_config():
    """Test that pyproject.toml exists and is valid."""
    import os
    import tomllib

    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    assert os.path.exists(pyproject_path)

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    assert "project" in config
    assert config["project"]["name"] == "fastapps"
    assert "version" in config["project"]
