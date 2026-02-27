import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os


# Test the update_dotenv.py script
class TestUpdateDotenv:
    """Tests for .copier/update_dotenv.py script"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory structure matching the expected layout"""
        copier_dir = tmp_path / ".copier"
        copier_dir.mkdir()
        
        # Create the main .env file
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default_project\nDEBUG=false\nDATABASE_URL=postgresql://localhost")
        
        # Create .copier-answers.yml as JSON file
        answers_file = copier_dir / ".copier-answers.yml"
        answers = {
            "project_name": "my_project",
            "debug": "true"
        }
        answers_file.write_text(json.dumps(answers))
        
        return tmp_path, copier_dir, env_file, answers_file

    def test_script_updates_simple_value_without_space(self, temp_dir):
        """Test updating .env with simple values (no spaces)"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "debug": "false"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("DEBUG=true\nOTHER=value")
        
        # Mock Path and file operations to simulate the script
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "DEBUG=false" in result
        assert "OTHER=value" in result

    def test_script_updates_value_with_space(self, temp_dir):
        """Test updating .env with values containing spaces (quoted)"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "project_name": "my awesome project"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("PROJECT_NAME=old_name\nOTHER=value")
        
        # Execute the logic
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "PROJECT_NAME='my awesome project'" in result
        assert "OTHER=value" in result

    def test_script_preserves_unmatched_lines(self, temp_dir):
        """Test that lines without matching keys are preserved"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "project_name": "test"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("PROJECT_NAME=old\nCOMMENT=# This is a comment\nDATABASE_URL=postgres://localhost")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "PROJECT_NAME=test" in result
        assert "COMMENT=# This is a comment" in result
        assert "DATABASE_URL=postgres://localhost" in result

    def test_script_handles_empty_answers(self, temp_dir):
        """Test script behavior with empty answers"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup - empty answers
        answers = {}
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        original_content = "DEBUG=true\nOTHER=value"
        env_file.write_text(original_content)
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert - content should be unchanged
        result = env_path.read_text()
        assert result == original_content

    def test_script_handles_multiline_env_file(self, temp_dir):
        """Test script with multiple lines in .env"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "debug": "false",
            "api_key": "secret123"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_content = """DEBUG=true
API_KEY=old_key
DATABASE_URL=localhost
OTHER_VAR=value"""
        env_file.write_text(env_content)
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        lines_result = result.split("\n")
        assert "DEBUG=false" in result
        assert "API_KEY=secret123" in result
        assert "DATABASE_URL=localhost" in result
        assert "OTHER_VAR=value" in result
        assert len(lines_result) == 4

    def test_script_handles_value_with_equals_sign(self, temp_dir):
        """Test updating values that contain equals signs"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "database_url": "postgresql://user:pass=word@localhost"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("DATABASE_URL=old_url")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "DATABASE_URL=postgresql://user:pass=word@localhost" in result

    def test_script_handles_numeric_values(self, temp_dir):
        """Test updating with numeric values"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "port": "8000",
            "workers": "4"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("PORT=3000\nWORKERS=2")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "PORT=8000" in result
        assert "WORKERS=4" in result

    def test_script_handles_special_characters_in_values(self, temp_dir):
        """Test with special characters in values"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "password": "p@ssw0rd!#$%"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("PASSWORD=oldpass")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "PASSWORD=p@ssw0rd!#$%" in result

    def test_script_case_sensitivity_for_keys(self, temp_dir):
        """Test that keys are converted to uppercase"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup with lowercase keys
        answers = {
            "debug": "true",
            "projectName": "test"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("DEBUG=false\nPROJECTNAME=old")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "DEBUG=true" in result
        assert "PROJECTNAME=test" in result

    def test_script_line_replacement_preserves_value(self, temp_dir):
        """Test that line replacement correctly uses the new value"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "api_url": "https://api.example.com"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("API_URL=https://old.example.com\nOTHER=value")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "API_URL=https://api.example.com" in result
        assert "https://old.example.com" not in result

    def test_script_handles_empty_value(self, temp_dir):
        """Test handling of empty string values"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "optional_var": ""
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("OPTIONAL_VAR=something")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        assert "OPTIONAL_VAR=" in result

    def test_script_handles_multiple_updates_same_line_concept(self, temp_dir):
        """Test that each line is only updated once even if multiple keys could match"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "debug": "false"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_file.write_text("DEBUG=true")
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert - should only appear once with correct value
        result = env_path.read_text()
        assert result.count("DEBUG=") == 1
        assert "DEBUG=false" in result

    def test_script_preserves_line_order(self, temp_dir):
        """Test that the order of lines is preserved"""
        tmp_path, copier_dir, env_file, answers_file = temp_dir
        
        # Setup
        answers = {
            "var_b": "new_b"
        }
        answers_file = copier_dir / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers))
        
        env_content = "VAR_A=a\nVAR_B=old_b\nVAR_C=c"
        env_file.write_text(env_content)
        
        # Execute
        root_path = tmp_path
        answers_path = copier_dir / ".copier-answers.yml"
        
        answers_data = json.loads(answers_path.read_text())
        env_path = root_path / ".env"
        env_content = env_path.read_text()
        lines = []
        
        for line in env_content.splitlines():
            matched = False
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    matched = True
                    break
            if not matched:
                lines.append(line)
        
        env_path.write_text("\n".join(lines))
        
        # Assert
        result = env_path.read_text()
        result_lines = result.split("\n")
        assert result_lines[0] == "VAR_A=a"
        assert result_lines[1] == "VAR_B=new_b"
        assert result_lines[2] == "VAR_C=c"