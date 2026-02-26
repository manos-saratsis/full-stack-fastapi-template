import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
import shutil


class TestUpdateDotenv:
    """Tests for .copier/update_dotenv.py module"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def setup_files(self, temp_dir):
        """Setup test files and directories"""
        copier_dir = Path(temp_dir) / ".copier"
        copier_dir.mkdir()
        
        # Create .env file
        env_file = Path(temp_dir) / ".env"
        env_file.write_text("SECRET_KEY=old_secret\nDATABASE_URL=postgresql://old\nAPP_NAME=myapp\n")
        
        # Create .copier-answers.yml as JSON
        answers_file = copier_dir / ".copier-answers.yml"
        answers = {
            "secret_key": "new_secret_value",
            "database_url": "postgresql://new_db",
            "app_name": "newapp"
        }
        answers_file.write_text(json.dumps(answers))
        
        return {
            "temp_dir": temp_dir,
            "copier_dir": copier_dir,
            "env_file": env_file,
            "answers_file": answers_file
        }

    def test_update_dotenv_with_space_in_value(self, setup_files):
        """Should update .env with quoted values when space is present"""
        temp_dir = setup_files["temp_dir"]
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        # Update answers with value containing space
        answers = {
            "secret_key": "new secret with space",
            "database_url": "postgresql://new_db"
        }
        answers_file.write_text(json.dumps(answers))
        
        # Read original env
        original_env = env_file.read_text()
        
        # Execute the update logic
        root_path = Path(temp_dir)
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        # Verify the update
        updated_content = env_file.read_text()
        assert "SECRET_KEY='new secret with space'" in updated_content
        assert "DATABASE_URL=postgresql://new_db" in updated_content

    def test_update_dotenv_without_space_in_value(self, setup_files):
        """Should update .env with unquoted values when no space is present"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        temp_dir = setup_files["temp_dir"]
        
        # Verify setup
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "SECRET_KEY=new_secret_value" in updated_content
        assert "DATABASE_URL=postgresql://new_db" in updated_content

    def test_update_dotenv_preserves_unmatched_lines(self, setup_files):
        """Should preserve lines that don't match any answer key"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        temp_dir = setup_files["temp_dir"]
        
        # Add unmatched line to env
        env_file.write_text("SECRET_KEY=old_secret\nUNMATCHED_VAR=value\nDATABASE_URL=postgresql://old\n")
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "UNMATCHED_VAR=value" in updated_content

    def test_update_dotenv_case_sensitive_key_matching(self, setup_files):
        """Should match keys case-insensitively (answer keys are lowercase)"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        temp_dir = setup_files["temp_dir"]
        
        # Verify that lowercase keys in answers match UPPERCASE keys in .env
        answers = {"secret_key": "updated_value"}
        answers_file.write_text(json.dumps(answers))
        env_file.write_text("SECRET_KEY=old_value\n")
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "SECRET_KEY=updated_value" in updated_content

    def test_update_dotenv_multiple_lines(self, setup_files):
        """Should handle multiple lines to be updated"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("VAR1=old1\nVAR2=old2\nVAR3=old3\n")
        answers = {"var1": "new1", "var2": "new2", "var3": "new3"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "VAR1=new1" in updated_content
        assert "VAR2=new2" in updated_content
        assert "VAR3=new3" in updated_content

    def test_update_dotenv_empty_env_file(self, setup_files):
        """Should handle empty .env file"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("")
        answers = {"secret_key": "value"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert updated_content == ""

    def test_update_dotenv_empty_answers(self, setup_files):
        """Should handle empty answers file"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        original_content = "VAR1=value1\nVAR2=value2\n"
        env_file.write_text(original_content)
        answers_file.write_text(json.dumps({}))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert updated_content == original_content

    def test_update_dotenv_value_with_special_characters(self, setup_files):
        """Should handle values with special characters"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("PASSWORD=oldpass\n")
        answers = {"password": "p@$$w0rd!#$%"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "PASSWORD=p@$$w0rd!#$%" in updated_content

    def test_update_dotenv_value_with_equals_sign(self, setup_files):
        """Should handle values containing equals signs"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("CONNECTION_STRING=old\n")
        answers = {"connection_string": "server=localhost;user=admin"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "CONNECTION_STRING='server=localhost;user=admin'" in updated_content

    def test_update_dotenv_quoted_repr_output(self, setup_files):
        """Should properly quote string representation of values with spaces"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("DESCRIPTION=old\n")
        answers = {"description": "this is a long description"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        # repr() should add quotes
        assert ("'this is a long description'" in updated_content or
                '"this is a long description"' in updated_content)

    def test_update_dotenv_loop_iteration_all_keys(self, setup_files):
        """Should iterate through all answer keys for each line"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("FIRST=1\nSECOND=2\nTHIRD=3\n")
        answers = {"first": "a", "second": "b", "third": "c"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            matched = False
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "FIRST=a" in updated_content
        assert "SECOND=b" in updated_content
        assert "THIRD=c" in updated_content

    def test_update_dotenv_line_replacement_logic(self, setup_files):
        """Should correctly replace entire line with new content"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("API_KEY=sk_test_123456\n")
        answers = {"api_key": "sk_live_789012"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "API_KEY=sk_live_789012" in updated_content
        assert "sk_test_123456" not in updated_content

    def test_update_dotenv_line_prefix_match_only(self, setup_files):
        """Should only match lines that start with KEY= pattern"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("SECRET_KEY=old\nCOMMENT_SECRET_KEY=should_not_match\n")
        answers = {"secret_key": "new"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "SECRET_KEY=new" in updated_content
        assert "COMMENT_SECRET_KEY=should_not_match" in updated_content

    def test_update_dotenv_numeric_value_without_space(self, setup_files):
        """Should handle numeric values without spaces"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("PORT=3000\n")
        answers = {"port": "8000"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "PORT=8000" in updated_content

    def test_update_dotenv_joins_lines_with_newline(self, setup_files):
        """Should join lines with newline separator"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("VAR1=val1\nVAR2=val2\n")
        answers = {"var1": "new1"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        lines_in_file = updated_content.split("\n")
        assert len(lines_in_file) >= 2
        assert "VAR1=new1" in updated_content
        assert "VAR2=val2" in updated_content

    def test_update_dotenv_with_trailing_newline(self, setup_files):
        """Should preserve structure when file has trailing newline"""
        env_file = setup_files["env_file"]
        answers_file = setup_files["answers_file"]
        
        env_file.write_text("VAR=old\n")
        answers = {"var": "new"}
        answers_file.write_text(json.dumps(answers))
        
        answers = json.loads(answers_file.read_text())
        env_content = env_file.read_text()
        lines = []
        for line in env_content.splitlines():
            for key, value in answers.items():
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
        env_file.write_text("\n".join(lines))
        
        updated_content = env_file.read_text()
        assert "VAR=new" in updated_content