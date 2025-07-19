# tests/test_cli.py
import pytest
from click.testing import CliRunner
# Assuming your main CLI app is imported like this due to src/git_template_cli/cli.py
from git_template_cli.cli import cli

def test_cli_welcome_page():
    runner = CliRunner()
    result = runner.invoke(cli, [], input='\n')
    assert result.exit_code == 0
    assert "Welcome to the Git Template CLI Tool! 🚀" in result.output # More reliable text
    assert "Available Commands:" in result.output
    # You can also check for part of the ASCII art lines if you want,
    # but exact matches are brittle with colors/formatting.
    # For example:
    # assert "██████╗" in result.output
# ...
def test_list_templates_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "Available templates:" in result.output
    assert "basic" in result.output # Check for a template you know exists
    assert "react-component" in result.output
    assert "python-service" in result.output

# Add more tests here for your 'create' command etc.
