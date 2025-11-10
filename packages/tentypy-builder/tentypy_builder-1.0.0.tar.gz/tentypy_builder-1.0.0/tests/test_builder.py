"""
Comprehensive Tests for TentyPy Builder
Author: Keniding
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tentypy.builder.cli import BuilderCLI
from tentypy.builder.config import DEFAULT_CONFIG, BuilderConfig
from tentypy.builder.core.file_generator import FileGenerator
from tentypy.builder.core.template_engine import ProjectTemplate, TemplateEngine
from tentypy.builder.core.validator import TemplateValidator

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_template_data():
    """Sample template data"""
    return {
        "name": "Test Template",
        "description": "Test description",
        "version": "1.0.0",
        "author": "Test Author",
        "variables": {"PYTHON_VERSION": "3.11", "AUTHOR": "Test"},
        "structure": ["src/", {"src": ["__init__.py", "main.py"]}, "README.md"],
        "files": {
            "README.md": "# {{PROJECT_NAME}}\n\nBy {{AUTHOR}}",
            "src/main.py": "# Main file\nprint('{{PROJECT_NAME}}')",
        },
    }


@pytest.fixture
def sample_template_file(temp_dir, sample_template_data):
    """Create sample template JSON file"""
    template_file = temp_dir / "test_template.json"
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(sample_template_data, f)
    return template_file


@pytest.fixture
def template_engine():
    """Template engine instance"""
    return TemplateEngine()


@pytest.fixture
def file_generator(temp_dir):
    """File generator instance"""
    return FileGenerator(temp_dir)


# ============================================================================
# TEMPLATE VALIDATOR TESTS
# ============================================================================


class TestTemplateValidator:
    """Tests for TemplateValidator"""

    def test_valid_template(self):
        """Test validator with valid template"""
        template_data = {"name": "Test Template", "structure": ["folder/", "file.py"]}
        is_valid, errors = TemplateValidator.validate(template_data)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test validator with missing required fields"""
        template_data = {"description": "Missing name and structure"}
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert len(errors) > 0
        assert any("name" in err.lower() for err in errors)

    def test_invalid_name_type(self):
        """Test validator with invalid name type"""
        template_data = {"name": 123, "structure": []}  # Should be string
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("name" in err.lower() for err in errors)

    def test_invalid_structure_type(self):
        """Test validator with invalid structure type"""
        template_data = {"name": "Test", "structure": "not a list"}  # Should be list
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("structure" in err.lower() for err in errors)

    def test_invalid_files_type(self):
        """Test validator with invalid files type"""
        template_data = {"name": "Test", "structure": [], "files": "not a dict"}  # Should be dict
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("files" in err.lower() for err in errors)

    def test_invalid_variables_type(self):
        """Test validator with invalid variables type"""
        template_data = {
            "name": "Test",
            "structure": [],
            "variables": "not a dict",  # Should be dict
        }
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("variables" in err.lower() for err in errors)

    def test_empty_string_in_structure(self):
        """Test validator with empty string in structure"""
        template_data = {"name": "Test", "structure": ["", "valid.py"]}
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("empty" in err.lower() for err in errors)

    def test_nested_structure_validation(self):
        """Test validator with nested structure"""
        template_data = {
            "name": "Test",
            "structure": ["folder/", {"folder": ["file.py", {"subfolder": ["nested.py"]}]}],
        }
        is_valid, errors = TemplateValidator.validate(template_data)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_nested_structure(self):
        """Test validator with invalid nested structure"""
        template_data = {"name": "Test", "structure": [{123: ["file.py"]}]}  # Invalid key type
        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid


# ============================================================================
# TEMPLATE ENGINE TESTS
# ============================================================================


class TestTemplateEngine:
    """Tests for TemplateEngine"""

    def test_list_templates(self, template_engine):
        """Test listing available templates"""
        templates = template_engine.list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "clean_architecture" in templates
        assert "fastapi_basic" in templates

    def test_load_template(self, template_engine):
        """Test loading existing template"""
        template = template_engine.load_template("clean_architecture")
        assert isinstance(template, ProjectTemplate)
        assert template.name == "Clean Architecture"
        assert template.version == "1.0.0"
        assert isinstance(template.variables, dict)
        assert isinstance(template.structure, list)
        assert isinstance(template.files, dict)

    def test_load_nonexistent_template(self, template_engine):
        """Test loading non-existent template"""
        with pytest.raises(FileNotFoundError):
            template_engine.load_template("nonexistent_template")

    def test_load_custom_template_json(self, template_engine, sample_template_file):
        """Test loading custom JSON template"""
        template = template_engine.load_custom_template(sample_template_file)
        assert isinstance(template, ProjectTemplate)
        assert template.name == "Test Template"
        assert template.description == "Test description"
        assert "PYTHON_VERSION" in template.variables

    def test_load_custom_template_yaml(self, template_engine, temp_dir):
        """Test loading custom YAML template"""
        try:
            yaml_content = """
name: YAML Test
description: Test YAML template
version: 1.0.0
author: Test
variables:
  TEST_VAR: test_value
structure:
  - src/
  - README.md
files:
  README.md: "# Test"
"""
            yaml_file = temp_dir / "test.yaml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            template = template_engine.load_custom_template(yaml_file)
            assert template.name == "YAML Test"
            assert "TEST_VAR" in template.variables

        except ImportError:
            pytest.skip("PyYAML not installed")

    def test_load_invalid_json(self, template_engine, temp_dir):
        """Test loading invalid JSON"""
        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        with pytest.raises(ValueError):
            template_engine.load_custom_template(invalid_file)

    def test_load_unsupported_format(self, template_engine, temp_dir):
        """Test loading unsupported file format"""
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.touch()

        with pytest.raises(ValueError):
            template_engine.load_custom_template(unsupported_file)

    def test_replace_variables(self, template_engine):
        """Test variable replacement"""
        content = "Project: {{PROJECT_NAME}}, Author: {{AUTHOR}}"
        variables = {"PROJECT_NAME": "TestProject", "AUTHOR": "TestAuthor"}

        result = template_engine.replace_variables(content, variables)
        assert "TestProject" in result
        assert "TestAuthor" in result
        assert "{{" not in result

    def test_replace_variables_with_user_override(self, template_engine):
        """Test variable replacement with user override"""
        content = "Version: {{VERSION}}"
        default_vars = {"VERSION": "1.0.0"}
        user_vars = {"VERSION": "2.0.0"}

        result = template_engine.replace_variables(content, default_vars, user_vars)
        assert "2.0.0" in result
        assert "1.0.0" not in result


# ============================================================================
# FILE GENERATOR TESTS
# ============================================================================


class TestFileGenerator:
    """Tests for FileGenerator"""

    def test_generate_simple_project(self, file_generator, temp_dir):
        """Test generating simple project"""
        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=["src/", "README.md"],
            files={"README.md": "# {{PROJECT_NAME}}"},
            variables={},
        )

        file_generator.generate_project(template, "test_project")

        project_path = temp_dir / "test_project"
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "README.md").exists()

    def test_generate_project_with_nested_structure(self, file_generator, temp_dir):
        """Test generating project with nested structure"""
        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=["src/", {"src": ["__init__.py", {"core": ["main.py"]}]}],
            files={},
            variables={},
        )

        file_generator.generate_project(template, "nested_project")

        project_path = temp_dir / "nested_project"
        assert (project_path / "src").exists()
        assert (project_path / "src" / "__init__.py").exists()
        assert (project_path / "src" / "core").exists()
        assert (project_path / "src" / "core" / "main.py").exists()

    def test_generate_project_with_file_content(self, file_generator, temp_dir):
        """Test generating project with file content"""
        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="TestAuthor",
            structure=["README.md"],
            files={"README.md": "# {{PROJECT_NAME}}\n\nBy {{AUTHOR}}"},
            variables={},
        )

        file_generator.generate_project(template, "content_project")

        readme_path = temp_dir / "content_project" / "README.md"
        assert readme_path.exists()

        content = readme_path.read_text(encoding="utf-8")
        assert "content_project" in content
        assert "TestAuthor" in content

    def test_generate_project_with_custom_variables(self, file_generator, temp_dir):
        """Test generating project with custom variables"""
        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=["config.py"],
            files={"config.py": "VERSION = '{{VERSION}}'\nDEBUG = {{DEBUG}}"},
            variables={"VERSION": "1.0.0", "DEBUG": "True"},
        )

        user_vars = {"VERSION": "2.0.0", "DEBUG": "False"}
        file_generator.generate_project(template, "var_project", user_vars)

        config_path = temp_dir / "var_project" / "config.py"
        content = config_path.read_text(encoding="utf-8")
        assert "2.0.0" in content
        assert "False" in content

    def test_generate_project_already_exists(self, file_generator, temp_dir):
        """Test generating project that already exists"""
        project_path = temp_dir / "existing_project"
        project_path.mkdir()

        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=[],
            files={},
            variables={},
        )

        with pytest.raises(FileExistsError):
            file_generator.generate_project(template, "existing_project")

    def test_replace_vars_in_paths(self, file_generator):
        """Test variable replacement in file paths"""
        variables = {"MODULE_NAME": "mymodule"}
        result = file_generator._replace_vars("src/{{MODULE_NAME}}/main.py", variables)
        assert result == "src/mymodule/main.py"


# ============================================================================
# CONFIG TESTS
# ============================================================================


class TestBuilderConfig:
    """Tests for BuilderConfig"""

    def test_default_config(self):
        """Test default configuration"""
        config = BuilderConfig()
        assert config.templates_dir.exists()
        assert config.output_dir == Path.cwd()
        assert "json" in config.supported_formats
        assert config.default_python_version == "3.11"

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        data = {"overwrite_existing": True, "verbose": True, "default_author": "TestAuthor"}
        config = BuilderConfig.from_dict(data)
        assert config.overwrite_existing is True
        assert config.verbose is True
        assert config.default_author == "TestAuthor"

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = BuilderConfig()
        data = config.to_dict()
        assert isinstance(data, dict)
        assert "templates_dir" in data
        assert "supported_formats" in data

    def test_default_config_instance(self):
        """Test DEFAULT_CONFIG instance"""
        assert isinstance(DEFAULT_CONFIG, BuilderConfig)
        assert DEFAULT_CONFIG.default_version == "1.0.0"


# ============================================================================
# CLI TESTS
# ============================================================================


class TestBuilderCLI:
    """Tests for BuilderCLI"""

    @pytest.fixture
    def cli(self):
        """CLI instance"""
        return BuilderCLI()

    def test_cli_initialization(self, cli):
        """Test CLI initialization"""
        assert isinstance(cli.engine, TemplateEngine)
        assert cli.parser is not None

    def test_cli_no_command(self, cli, capsys):
        """Test CLI without command"""
        result = cli.run([])
        assert result == 1

    def test_cli_list_command(self, cli, capsys):
        """Test list command"""
        with patch("tentypy.builder.cli.console") as mock_console:
            result = cli.run(["list"])
            assert result == 0
            assert mock_console.print.called

    def test_cli_info_command(self, cli):
        """Test info command"""
        with patch("tentypy.builder.cli.console") as mock_console:
            result = cli.run(["info", "clean_architecture"])
            assert result == 0
            assert mock_console.print.called

    def test_cli_info_nonexistent_template(self, cli):
        """Test info command with non-existent template"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["info", "nonexistent"])
            assert result == 1

    def test_cli_validate_command(self, cli, sample_template_file):
        """Test validate command"""
        with patch("tentypy.builder.cli.console") as mock_console:
            result = cli.run(["validate", str(sample_template_file)])
            assert result == 0
            assert mock_console.print.called

    def test_cli_validate_nonexistent_file(self, cli):
        """Test validate command with non-existent file"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", "nonexistent.json"])
            assert result == 1

    def test_cli_create_command(self, cli, temp_dir):
        """Test create command"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["create", "test_project", "-t", "fastapi_basic", "-o", str(temp_dir)])
            assert result == 0
            assert (temp_dir / "test_project").exists()

    def test_cli_create_with_variables(self, cli, temp_dir):
        """Test create command with custom variables"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(
                [
                    "create",
                    "var_project",
                    "-t",
                    "fastapi_basic",
                    "-o",
                    str(temp_dir),
                    "-v",
                    "AUTHOR=TestAuthor",
                    "-v",
                    "PYTHON_VERSION=3.12",
                ]
            )
            assert result == 0

    def test_cli_create_with_custom_template(self, cli, temp_dir, sample_template_file):
        """Test create command with custom template"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(
                ["create", "custom_project", "-c", str(sample_template_file), "-o", str(temp_dir)]
            )
            assert result == 0

    def test_cli_keyboard_interrupt(self, cli):
        """Test CLI handling keyboard interrupt"""
        with patch.object(cli, "_handle_create", side_effect=KeyboardInterrupt):
            with patch("tentypy.builder.cli.console"):
                result = cli.run(["create", "test"])
                assert result == 1

    def test_cli_exception_handling(self, cli):
        """Test CLI exception handling"""
        with patch.object(cli, "_handle_create", side_effect=Exception("Test error")):
            with patch("tentypy.builder.cli.console"):
                result = cli.run(["create", "test"])
                assert result == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self, temp_dir):
        """Test complete workflow: load template -> generate project"""
        # Load template
        engine = TemplateEngine()
        template = engine.load_template("fastapi_basic")

        # Generate project
        generator = FileGenerator(temp_dir)
        generator.generate_project(template, "integration_test")

        # Verify structure
        project_path = temp_dir / "integration_test"
        assert project_path.exists()
        assert (project_path / "app").exists()
        assert (project_path / "requirements.txt").exists()
        assert (project_path / "README.md").exists()

    def test_custom_template_workflow(self, temp_dir):
        """Test workflow with custom template"""
        # Create custom template
        template_data = {
            "name": "Custom",
            "description": "Custom template",
            "version": "1.0.0",
            "author": "Test",
            "structure": ["src/", "README.md"],
            "files": {"README.md": "# {{PROJECT_NAME}}"},
            "variables": {},
        }

        template_file = temp_dir / "custom.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f)

        # Load and generate
        engine = TemplateEngine()
        template = engine.load_custom_template(template_file)

        generator = FileGenerator(temp_dir)
        generator.generate_project(template, "custom_project")

        # Verify
        assert (temp_dir / "custom_project").exists()
        assert (temp_dir / "custom_project" / "README.md").exists()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tentypy", "--cov-report=html"])
