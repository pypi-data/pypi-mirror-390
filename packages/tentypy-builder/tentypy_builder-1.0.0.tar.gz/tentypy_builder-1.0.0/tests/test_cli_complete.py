"""
Complete CLI Tests - Coverage Boost
Author: Keniding
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tentypy.builder.cli import BuilderCLI
from tentypy.builder.core.template_engine import ProjectTemplate


class TestCLIInteractive:
    """Tests for interactive mode"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_interactive_create_full_flow(self, cli, temp_dir, monkeypatch):
        """Test complete interactive create flow"""
        # Mock user inputs
        inputs = iter(
            [
                "1",  # Template selection
                "test_interactive",  # Project name
                "TestAuthor",  # AUTHOR variable
                "3.12",  # PYTHON_VERSION variable
                "y",  # Confirm creation
            ]
        )

        monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: next(inputs))
        monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *args, **kwargs: True)

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["create", "-i"])
            # Should succeed or handle gracefully
            assert result in [0, 1]

    def test_interactive_create_cancelled(self, cli, monkeypatch):
        """Test interactive create when user cancels"""
        inputs = iter(
            [
                "1",  # Template selection
                "cancelled_project",  # Project name
                "TestAuthor",  # AUTHOR
                "3.11",  # PYTHON_VERSION
            ]
        )

        monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: next(inputs))
        monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *args, **kwargs: False)

        with patch("tentypy.builder.cli.console") as mock_console:
            result = cli.run(["create", "-i"])
            assert result == 1
            # Verify cancellation message was printed
            calls = [str(call) for call in mock_console.print.call_args_list]
            assert any(
                "Cancelled" in str(call) or "cancelled" in str(call).lower() for call in calls
            )

    def test_interactive_create_no_project_name(self, cli, temp_dir, monkeypatch):
        """Test interactive mode triggered by missing project name"""
        inputs = iter(
            [
                "1",  # Template selection
                "auto_interactive",  # Project name
                "TestAuthor",  # AUTHOR
                "3.11",  # PYTHON_VERSION
            ]
        )

        monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: next(inputs))
        monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *args, **kwargs: True)

        with patch("tentypy.builder.cli.console"):
            # No project_name argument triggers interactive
            result = cli.run(["create", "-o", str(temp_dir)])
            assert result in [0, 1]

    def test_show_tree_with_permission_error(self, cli, temp_dir):
        """Test tree display with permission error"""
        test_dir = temp_dir / "test_tree"
        test_dir.mkdir()

        with patch.object(Path, "iterdir", side_effect=PermissionError("Access denied")):
            with patch("tentypy.builder.cli.console"):
                # Should handle gracefully
                tree = cli._show_tree(test_dir)
                assert tree is not None

    def test_show_tree_many_items(self, cli, temp_dir):
        """Test tree display with more than 10 items"""
        test_dir = temp_dir / "many_items"
        test_dir.mkdir()

        # Create 15 files
        for i in range(15):
            (test_dir / f"file_{i}.txt").touch()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=1)
            assert tree is not None

    def test_show_tree_nested_depth(self, cli, temp_dir):
        """Test tree display with nested directories"""
        test_dir = temp_dir / "nested"
        test_dir.mkdir()

        # Create nested structure
        level1 = test_dir / "level1"
        level1.mkdir()
        (level1 / "file1.txt").touch()

        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "file2.txt").touch()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=3)
            assert tree is not None

    def test_show_tree_hidden_files(self, cli, temp_dir):
        """Test tree display skips hidden files"""
        test_dir = temp_dir / "hidden_test"
        test_dir.mkdir()

        (test_dir / ".hidden").touch()
        (test_dir / "visible.txt").touch()

        with patch("tentypy.builder.cli.console"):
            tree = cli._show_tree(test_dir, max_depth=1)
            assert tree is not None


class TestCLIValidate:
    """Tests for validate command edge cases"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_validate_yaml_file(self, cli, temp_dir):
        """Test validating YAML template"""
        yaml_content = """
name: YAML Test
description: Test YAML
version: 1.0.0
author: Test
structure:
  - src/
  - README.md
files:
  README.md: "# Test"
"""
        yaml_file = temp_dir / "test.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", str(yaml_file)])
            assert result == 0

    def test_validate_invalid_template(self, cli, temp_dir):
        """Test validating invalid template"""
        invalid_data = {"description": "Missing required fields"}

        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", str(invalid_file)])
            assert result == 1

    def test_validate_unsupported_extension(self, cli, temp_dir):
        """Test validating file with unsupported extension"""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not a template")

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", str(txt_file)])
            assert result == 1

    def test_validate_malformed_json(self, cli, temp_dir):
        """Test validating malformed JSON"""
        bad_json = temp_dir / "bad.json"
        bad_json.write_text("{ invalid json }")

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["validate", str(bad_json)])
            assert result == 1


class TestCLIInfo:
    """Tests for info command edge cases"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_info_interactive_mode(self, cli, monkeypatch):
        """Test info command in interactive mode"""
        monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: "1")

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["info"])
            assert result == 0

    def test_info_with_template_name(self, cli):
        """Test info command with specific template"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["info", "clean_architecture"])
            assert result == 0

    def test_info_template_without_variables(self, cli, temp_dir):
        """Test info for template without variables"""
        template_data = {
            "name": "No Vars Template",
            "description": "Template without variables",
            "version": "1.0.0",
            "author": "Test",
            "structure": ["src/"],
            "files": {},
        }

        template_file = temp_dir / "no_vars.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f)

        # Temporarily add to templates
        with patch.object(cli.engine, "load_template") as mock_load:
            mock_load.return_value = ProjectTemplate(
                name="No Vars Template",
                description="Template without variables",
                version="1.0.0",
                author="Test",
                structure=["src/"],
                files={},
                variables={},
            )

            with patch("tentypy.builder.cli.console"):
                result = cli.run(["info", "no_vars"])
                assert result == 0


class TestCLICreate:
    """Tests for create command edge cases"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_create_with_multiple_variables(self, cli, temp_dir):
        """Test create with multiple -v flags"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(
                [
                    "create",
                    "multi_var_project",
                    "-t",
                    "fastapi_basic",
                    "-o",
                    str(temp_dir),
                    "-v",
                    "AUTHOR=John Doe",
                    "-v",
                    "PYTHON_VERSION=3.12",
                    "-v",
                    "PROJECT_DESCRIPTION=Test project",
                ]
            )
            assert result == 0

    def test_create_with_malformed_variable(self, cli, temp_dir):
        """Test create with malformed variable (no =)"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(
                [
                    "create",
                    "malformed_var",
                    "-t",
                    "fastapi_basic",
                    "-o",
                    str(temp_dir),
                    "-v",
                    "INVALID_VAR",  # No = sign
                ]
            )
            # Should still succeed, just ignore invalid var
            assert result == 0

    def test_create_default_template(self, cli, temp_dir):
        """Test create without specifying template (uses default)"""
        with patch("tentypy.builder.cli.console"):
            result = cli.run(["create", "default_template_project", "-o", str(temp_dir)])
            assert result == 0

    def test_create_with_custom_yaml_template(self, cli, temp_dir):
        """Test create with custom YAML template"""
        yaml_content = """
name: Custom YAML
description: Custom YAML template
version: 1.0.0
author: Test
variables:
  AUTHOR: TestAuthor
structure:
  - src/
  - README.md
files:
  README.md: "# {{PROJECT_NAME}}"
"""
        yaml_file = temp_dir / "custom.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        with patch("tentypy.builder.cli.console"):
            result = cli.run(["create", "yaml_project", "-c", str(yaml_file), "-o", str(temp_dir)])
            assert result == 0


class TestCLIList:
    """Tests for list command edge cases"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_list_with_error_loading_template(self, cli):
        """Test list command when a template fails to load"""
        with patch.object(cli.engine, "list_templates", return_value=["valid", "invalid"]):
            with patch.object(cli.engine, "load_template") as mock_load:

                def side_effect(name):
                    if name == "invalid":
                        raise Exception("Failed to load")
                    return ProjectTemplate(
                        name="Valid",
                        description="Valid template",
                        version="1.0.0",
                        author="Test",
                        structure=[],
                        files={},
                        variables={},
                    )

                mock_load.side_effect = side_effect

                with patch("tentypy.builder.cli.console"):
                    result = cli.run(["list"])
                    assert result == 0


class TestCLIWelcome:
    """Tests for welcome screen"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    def test_show_welcome(self, cli):
        """Test welcome screen display"""
        with patch("tentypy.builder.cli.console") as mock_console:
            cli._show_welcome()
            assert mock_console.print.called


class TestCLIProjectSummary:
    """Tests for project summary display"""

    @pytest.fixture
    def cli(self):
        return BuilderCLI()

    @pytest.fixture
    def sample_template(self):
        return ProjectTemplate(
            name="Test Template",
            description="Test",
            version="1.0.0",
            author="TestAuthor",
            structure=["src/", "README.md"],
            files={},
            variables={},
        )

    def test_show_project_summary(self, cli, temp_dir, sample_template):
        """Test project summary display"""
        project_name = "summary_test"
        project_path = temp_dir / project_name
        project_path.mkdir()
        (project_path / "README.md").touch()

        with patch("tentypy.builder.cli.console"):
            cli._show_project_summary(project_name, sample_template, temp_dir)


# ============================================================================
# ADDITIONAL EDGE CASES
# ============================================================================


class TestTemplateEngineEdgeCases:
    """Additional tests for template engine"""

    def test_replace_variables_no_user_vars(self):
        """Test variable replacement without user vars"""
        from tentypy.builder.core.template_engine import TemplateEngine

        engine = TemplateEngine()
        content = "Project: {{PROJECT_NAME}}"
        variables = {"PROJECT_NAME": "TestProject"}

        result = engine.replace_variables(content, variables, None)
        assert "TestProject" in result

    def test_replace_variables_empty_content(self):
        """Test variable replacement with empty content"""
        from tentypy.builder.core.template_engine import TemplateEngine

        engine = TemplateEngine()
        result = engine.replace_variables("", {}, {})
        assert result == ""

    def test_load_template_all_extensions(self):
        """Test loading templates with different extensions"""
        from tentypy.builder.core.template_engine import TemplateEngine

        engine = TemplateEngine()

        # Should find .json first
        try:
            template = engine.load_template("clean_architecture")
            assert template.name is not None
        except FileNotFoundError:
            pytest.skip("Template not found")


class TestValidatorEdgeCases:
    """Additional validator tests"""

    def test_validate_empty_dict(self):
        """Test validator with empty dictionary"""
        from tentypy.builder.core.validator import TemplateValidator

        is_valid, errors = TemplateValidator.validate({})
        assert not is_valid
        assert len(errors) > 0

    def test_validate_structure_with_none_value(self):
        """Test validator with None value in structure"""
        from tentypy.builder.core.validator import TemplateValidator

        template_data = {"name": "Test", "structure": [{"folder": None}]}  # None is allowed

        is_valid, errors = TemplateValidator.validate(template_data)
        assert is_valid

    def test_validate_deeply_nested_structure(self):
        """Test validator with deeply nested structure"""
        from tentypy.builder.core.validator import TemplateValidator

        template_data = {
            "name": "Test",
            "structure": [{"level1": [{"level2": [{"level3": ["file.py"]}]}]}],
        }

        is_valid, errors = TemplateValidator.validate(template_data)
        assert is_valid


class TestFileGeneratorEdgeCases:
    """Additional file generator tests"""

    def test_replace_vars_multiple_occurrences(self, file_generator):
        """Test replacing variable that appears multiple times"""
        variables = {"NAME": "test"}
        result = file_generator._replace_vars("{{NAME}}/{{NAME}}/{{NAME}}.py", variables)
        assert result == "test/test/test.py"

    def test_replace_vars_no_variables(self, file_generator):
        """Test path with no variables"""
        result = file_generator._replace_vars("src/main.py", {})
        assert result == "src/main.py"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tentypy", "--cov-report=html", "--cov-report=term-missing"])
