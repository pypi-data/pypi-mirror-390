"""
Coverage Boost Tests - Target 98%+
Author: Keniding
"""

import json
from unittest.mock import patch

import pytest

from tentypy.builder.cli import BuilderCLI
from tentypy.builder.core.file_generator import FileGenerator
from tentypy.builder.core.template_engine import ProjectTemplate, TemplateEngine
from tentypy.builder.core.validator import TemplateValidator


class TestCLICoverageMissing:
    """Cover missing lines in cli.py"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_validate_with_yaml_load_error(self, cli, temp_dir):
        """Test validate with YAML load error (line 202-203)"""
        yaml_file = temp_dir / "bad.yaml"
        yaml_file.write_text("invalid: yaml: content: [")

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", str(yaml_file)])
            assert result == 1

    def test_interactive_mode_no_templates(self, cli):
        """Test interactive mode when no templates available"""
        with patch.object(cli.engine, "list_templates", return_value=[]):
            with patch("tentypy.builder.cli.console"):
                result = cli.run(["info"])
                assert result == 1

    def test_show_tree_current_depth_exceeds_max(self, cli, temp_dir):
        """Test tree display when current_depth >= max_depth"""
        test_dir = temp_dir / "deep"
        test_dir.mkdir()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=1, current_depth=1)
            assert tree is not None

    def test_show_tree_item_count_limit(self, cli, temp_dir):
        """Test tree display with item count > 10"""
        test_dir = temp_dir / "many"
        test_dir.mkdir()

        # Create 11 items to trigger limit
        for i in range(11):
            (test_dir / f"file_{i}.txt").touch()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=1)
            assert tree is not None

    def test_create_interactive_no_template_selected(self, cli, monkeypatch):
        """Test interactive create when selection fails"""
        # Mock empty choice
        with patch.object(cli.engine, "list_templates", return_value=["template1"]):
            with patch("rich.prompt.Prompt.ask", side_effect=IndexError("Invalid choice")):
                with patch("tentypy.builder.cli.console"):
                    result = cli.run(["create", "-i"])
                    assert result == 1


class TestTemplateEngineCoverageMissing:
    """Cover missing lines in template_engine.py"""

    def test_load_template_with_yaml_error(self, temp_dir):
        """Test loading template with YAML parsing error"""
        engine = TemplateEngine()

        # Create invalid YAML
        yaml_file = temp_dir / "bad_template.yaml"
        yaml_file.write_text("invalid: yaml: [[[")

        with patch.object(engine, "templates_dir", temp_dir):
            with pytest.raises(Exception):
                engine.load_template("bad_template")

    def test_load_custom_template_json_decode_error(self, temp_dir):
        """Test loading custom template with JSON decode error"""
        engine = TemplateEngine()

        # Create invalid JSON
        json_file = temp_dir / "bad_template.json"
        json_file.write_text("{ invalid json }")

        # Use load_custom_template directly
        with pytest.raises(ValueError, match="Invalid template format"):
            engine.load_custom_template(json_file)

    def test_load_custom_template_missing_fields(self, temp_dir):
        """Test loading custom template with missing fields - covers line 96"""
        engine = TemplateEngine()

        # Create valid JSON but missing fields (will use defaults)
        # This tests the .get() calls with defaults on lines 96-102
        minimal_template = {}

        json_file = temp_dir / "minimal_template.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(minimal_template, f)

        # Should succeed with defaults
        template = engine.load_custom_template(json_file)
        assert template.name == "minimal_template"  # Uses stem as default
        assert template.description == ""
        assert template.version == "1.0.0"
        assert template.author == "Unknown"
        assert template.structure == []
        assert template.files == {}
        assert template.variables == {}


class TestValidatorCoverageMissing:
    """Cover missing lines in validator.py"""

    def test_validate_structure_invalid_nested_type(self):
        """Test validation with invalid nested structure type"""
        template_data = {
            "name": "Test",
            "structure": [{"folder": 123}],  # Should be list or None, not int
        }

        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert len(errors) > 0

    def test_validate_files_with_non_dict(self):
        """Test validation with files as non-dict - covers line 94"""
        template_data = {"name": "Test", "structure": [], "files": "not a dict"}  # Should be dict

        is_valid, errors = TemplateValidator.validate(template_data)
        assert not is_valid
        assert any("files" in err.lower() for err in errors)


class TestFileGeneratorBranchCoverage:
    """Improve branch coverage for file_generator.py"""

    def test_generate_with_existing_directory(self, temp_dir):
        """Test generating when directory already exists"""
        file_generator = FileGenerator(temp_dir)

        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=["src/"],
            files={},
            variables={},
        )

        project_name = "existing_project"
        project_path = temp_dir / project_name
        project_path.mkdir()  # Pre-create directory

        # Note: Signature is generate_project(template, project_name, user_vars)
        with pytest.raises(FileExistsError):
            file_generator.generate_project(template, project_name, {})

    def test_generate_project_success(self, temp_dir):
        """Test successful project generation"""
        file_generator = FileGenerator(temp_dir)

        template = ProjectTemplate(
            name="Test",
            description="Test",
            version="1.0.0",
            author="Test",
            structure=[{"src": ["main.py"]}],
            files={"src/main.py": "# Test"},
            variables={},
        )

        project_name = "success_project"

        # Generate project
        file_generator.generate_project(template, project_name, {})

        # Verify
        assert (temp_dir / project_name / "src" / "main.py").exists()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegrationCoverage:
    """Integration tests for full coverage"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_validate_then_create_workflow(self, cli, temp_dir):
        """Test validating a template then creating project with it"""
        template_data = {
            "name": "Custom Test",
            "description": "Test template",
            "version": "1.0.0",
            "author": "Test",
            "structure": ["src/", "tests/"],
            "files": {"README.md": "# {{PROJECT_NAME}}"},
            "variables": {"PROJECT_NAME": "MyProject"},
        }

        template_file = temp_dir / "custom_template.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2)

        with patch("tentypy.builder.cli.console"):
            # Validate
            result1 = cli.run(["validate", str(template_file)])
            assert result1 == 0

            # Create
            result2 = cli.run(
                ["create", "validated_project", "-c", str(template_file), "-o", str(temp_dir)]
            )
            assert result2 == 0

    def test_list_then_info_then_create(self, cli, temp_dir):
        """Test complete workflow"""
        with patch("tentypy.builder.cli.console"):
            result1 = cli.run(["list"])
            assert result1 == 0

            result2 = cli.run(["info", "fastapi_basic"])
            assert result2 == 0

            result3 = cli.run(
                ["create", "workflow_test", "-t", "fastapi_basic", "-o", str(temp_dir)]
            )
            assert result3 == 0


# ============================================================================
# ERROR HANDLING
# ============================================================================


class TestErrorHandlingCoverage:
    """Test error handling paths"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_create_with_permission_error(self, cli, temp_dir):
        """Test create when permission denied"""
        with patch("pathlib.Path.mkdir", side_effect=PermissionError("Access denied")):
            with patch("tentypy.builder.cli.console"):
                result = cli.run(
                    ["create", "permission_test", "-t", "fastapi_basic", "-o", str(temp_dir)]
                )
                assert result == 1

    def test_validate_with_file_not_found(self, cli):
        """Test validate with non-existent file"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", "/nonexistent/file.json"])
            assert result == 1


# ============================================================================
# ADDITIONAL EDGE CASES
# ============================================================================


class TestAdditionalEdgeCases:
    """Additional edge cases"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_info_with_empty_template_list(self, cli):
        """Test info when no templates"""
        with patch.object(cli.engine, "list_templates", return_value=[]):
            with patch("tentypy.builder.cli.console"):
                result = cli.run(["info"])
                assert result == 1

    def test_tree_display_with_nested_structure(self, cli, temp_dir):
        """Test tree with nested directories"""
        test_dir = temp_dir / "nested"
        test_dir.mkdir()

        level1 = test_dir / "level1"
        level1.mkdir()
        (level1 / "file1.txt").touch()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=2)
            assert tree is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tentypy", "--cov-report=html", "--cov-report=term-missing"])
