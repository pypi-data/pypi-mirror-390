"""
Tests for templates module
"""

from pathlib import Path


def test_templates_dir_import():
    """Test TEMPLATES_DIR import"""
    from tentypy.builder.templates import TEMPLATES_DIR

    assert isinstance(TEMPLATES_DIR, Path)
    assert TEMPLATES_DIR.exists()
    assert TEMPLATES_DIR.is_dir()


def test_templates_dir_contains_templates():
    """Test that TEMPLATES_DIR contains template files"""
    from tentypy.builder.templates import TEMPLATES_DIR

    # Should have at least one template file
    json_files = list(TEMPLATES_DIR.glob("*.json"))
    yaml_files = list(TEMPLATES_DIR.glob("*.yaml")) + list(TEMPLATES_DIR.glob("*.yml"))

    assert len(json_files) + len(yaml_files) > 0


def test_templates_module_all():
    """Test __all__ export"""
    from tentypy.builder import templates

    assert hasattr(templates, "__all__")
    assert "TEMPLATES_DIR" in templates.__all__
