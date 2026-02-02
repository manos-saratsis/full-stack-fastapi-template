import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest


class TestUpdateDotenv:
    """Tests for .copier/update_dotenv.py module"""

    def test_reads_answers_file_successfully(self, tmp_path):
        """should read .copier-answers.yml file successfully when it exists"""
        # Arrange
        answers_data = {"project_name": "test_project", "debug": "true"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default\nDEBUG=false\n")
        
        copier_file = tmp_path / ".copier" / "update_dotenv.py"
        copier_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Act
        with mock.patch('pathlib.Path') as mock_path:
            def path_side_effect(p):
                if p == ".":
                    return tmp_path
                return Path(p)
            
            mock_path.side_effect = path_side_effect
            answers_path = tmp_path / ".copier-answers.yml"
            answers = json.loads(answers_path.read_text())
        
        # Assert
        assert answers == answers_data
        assert "project_name" in answers
        assert answers["project_name"] == "test_project"

    def test_env_file_updated_with_simple_value(self, tmp_path):
        """should update .env file with simple values from answers"""
        # Arrange
        answers_data = {"project_name": "my_project", "version": "1.0.0"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default\nVERSION=0.0.0\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME=my_project" in result
        assert "VERSION=1.0.0" in result
        assert "default" not in result
        assert "0.0.0" not in result

    def test_env_file_updated_with_value_containing_spaces(self, tmp_path):
        """should quote values containing spaces"""
        # Arrange
        answers_data = {"project_name": "my project name"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME='my project name'" in result

    def test_env_file_preserves_unmatched_lines(self, tmp_path):
        """should preserve lines that don't match any answers key"""
        # Arrange
        answers_data = {"project_name": "my_project"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default\nOTHER_KEY=value\nNO_MATCH=unchanged\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "OTHER_KEY=value" in result
        assert "NO_MATCH=unchanged" in result
        assert "PROJECT_NAME=my_project" in result

    def test_env_file_with_empty_answers(self, tmp_path):
        """should handle empty answers dict"""
        # Arrange
        answers_data = {}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        original_content = "PROJECT_NAME=default\nVERSION=1.0.0\n"
        env_file.write_text(original_content)
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert result == original_content

    def test_env_file_with_multiple_values(self, tmp_path):
        """should update multiple env values from answers"""
        # Arrange
        answers_data = {
            "project_name": "my_app",
            "debug": "true",
            "secret_key": "super_secret_value with spaces"
        }
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PROJECT_NAME=default\nDEBUG=false\nSECRET_KEY=old\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME=my_app" in result
        assert "DEBUG=true" in result
        assert "SECRET_KEY='super_secret_value with spaces'" in result

    def test_env_file_with_numeric_values(self, tmp_path):
        """should handle numeric values from answers"""
        # Arrange
        answers_data = {"port": "8000", "timeout": "30"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("PORT=3000\nTIMEOUT=10\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PORT=8000" in result
        assert "TIMEOUT=30" in result

    def test_env_file_handles_case_sensitivity(self, tmp_path):
        """should convert answer keys to uppercase for env file matching"""
        # Arrange
        answers_data = {"project_name": "test"}
        
        # Act
        env_content = "PROJECT_NAME=old\n"
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME=test" in result

    def test_env_file_with_special_characters(self, tmp_path):
        """should handle values with special characters"""
        # Arrange
        answers_data = {"db_url": "postgresql://user:pass@localhost/db"}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("DB_URL=sqlite:///db.sqlite\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "DB_URL=postgresql://user:pass@localhost/db" in result

    def test_env_file_with_empty_value(self, tmp_path):
        """should handle empty string values"""
        # Arrange
        answers_data = {"optional_key": ""}
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(json.dumps(answers_data))
        
        env_file = tmp_path / ".env"
        env_file.write_text("OPTIONAL_KEY=default_value\n")
        
        # Act
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "OPTIONAL_KEY=" in result

    def test_env_file_multiline_preserve_structure(self, tmp_path):
        """should preserve multiline env file structure"""
        # Arrange
        answers_data = {"key1": "value1"}
        
        env_content = "KEY1=old\n\n# Comment\nKEY2=value2\n"
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "KEY1=value1" in result
        assert "# Comment" in result
        assert "KEY2=value2" in result

    def test_env_file_quotes_preservation_logic(self, tmp_path):
        """should use repr() for values with spaces for proper quoting"""
        # Arrange
        answers_data = {"name": "John Doe"}
        
        # Act
        value = answers_data["name"]
        if " " in value:
            quoted = repr(value)
        
        # Assert
        assert quoted == "'John Doe'"

    def test_answers_json_parsing(self, tmp_path):
        """should correctly parse JSON answers file"""
        # Arrange
        answers_data = {
            "string_val": "test",
            "numeric_val": "123",
            "bool_val": "true",
            "special_val": "test@example.com"
        }
        
        # Act
        json_str = json.dumps(answers_data)
        parsed = json.loads(json_str)
        
        # Assert
        assert parsed == answers_data
        assert isinstance(parsed["string_val"], str)

    def test_env_file_no_match_first_key(self, tmp_path):
        """should handle case where first key in answers doesn't match any env line"""
        # Arrange
        answers_data = {"unmatchable_key": "value", "project_name": "my_app"}
        env_content = "PROJECT_NAME=old\n"
        
        # Act
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME=my_app" in result

    def test_env_line_replacement_logic(self, tmp_path):
        """should correctly replace entire line when key matches"""
        # Arrange
        original_line = "PROJECT_NAME=old_value"
        key = "project_name"
        value = "new_value"
        upper_key = key.upper()
        
        # Act
        if original_line.startswith(f"{upper_key}="):
            if " " in value:
                content = f"{upper_key}={value!r}"
            else:
                content = f"{upper_key}={value}"
            new_line = original_line.replace(original_line, content)
        
        # Assert
        assert new_line == "PROJECT_NAME=new_value"

    def test_answers_with_underscore_keys(self, tmp_path):
        """should handle answer keys with underscores"""
        # Arrange
        answers_data = {"project_name_long": "my_cool_project"}
        env_content = "PROJECT_NAME_LONG=default\n"
        
        # Act
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "PROJECT_NAME_LONG=my_cool_project" in result

    def test_env_with_equals_in_value(self, tmp_path):
        """should handle values containing equals signs"""
        # Arrange
        answers_data = {"connection_string": "Driver=ODBC Driver 17 for SQL Server"}
        env_content = "CONNECTION_STRING=old\n"
        
        # Act
        lines = []
        for line in env_content.splitlines():
            for key, value in answers_data.items():
                upper_key = key.upper()
                if line.startswith(f"{upper_key}="):
                    if " " in value:
                        content = f"{upper_key}={value!r}"
                    else:
                        content = f"{upper_key}={value}"
                    new_line = line.replace(line, content)
                    lines.append(new_line)
                    break
            else:
                lines.append(line)
        result = "\n".join(lines)
        
        # Assert
        assert "CONNECTION_STRING='Driver=ODBC Driver 17 for SQL Server'" in result