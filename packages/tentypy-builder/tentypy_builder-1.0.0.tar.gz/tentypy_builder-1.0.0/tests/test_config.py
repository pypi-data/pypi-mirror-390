"""Tests for root config module"""

from tentypy.builder import DEFAULT_CONFIG
from tentypy.config import BuilderConfig


def test_root_config_import():
    """Test importing from root config"""
    assert BuilderConfig is not None
    assert DEFAULT_CONFIG is not None


def test_root_config_instance():
    """Test root config instance"""
    config = BuilderConfig()
    assert config.default_version == "1.0.0"
    assert config.default_python_version == "3.11"


def test_root_config_from_dict():
    """Test creating config from dict"""
    data = {"verbose": True, "default_author": "Test"}
    config = BuilderConfig.from_dict(data)
    assert config.verbose is True
    assert config.default_author == "Test"


def test_root_config_to_dict():
    """Test converting config to dict"""
    config = BuilderConfig()
    data = config.to_dict()
    assert isinstance(data, dict)
    assert "default_version" in data
