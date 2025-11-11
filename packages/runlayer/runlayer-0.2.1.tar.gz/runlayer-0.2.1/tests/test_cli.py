"""Basic tests for the CLI."""

import re
from typer.testing import CliRunner

from runlayer_cli.main import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_help_command():
    """Test that the help command shows usage information."""
    # Test top-level help
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "Run MCP servers via HTTP transport" in plain_output
    assert "--version" in plain_output

    # Test run command help
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "Run an MCP server via HTTP transport" in plain_output
    assert "SERVER_UUID" in plain_output
    assert "--secret" in plain_output
    assert "--host" in plain_output


def test_version_command():
    """Test that the version command shows version information."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "runlayer version" in plain_output

    # Test short version flag
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    plain_output = strip_ansi(result.stdout)
    assert "runlayer version" in plain_output


def test_run_command_requires_arguments():
    """Test that run command requires server UUID and secret."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0
    # Should fail because required arguments are missing


def test_default_command_behavior():
    """Test that run command requires secret argument."""
    result = runner.invoke(app, ["run", "test-uuid"])
    assert result.exit_code != 0


def test_run_command_with_secret_requires_host():
    """Test that run command with server UUID and secret still requires host."""
    result = runner.invoke(app, ["run", "test-uuid", "--secret", "test-secret"])
    assert result.exit_code != 0
    # Should fail because --host is missing (or connection fails)
