"""Test CLI functionality."""

import pytest
from click.testing import CliRunner

from devagent.cli import main


def test_cli_starts():
    """Test that the CLI starts without errors."""
    runner = CliRunner()
    result = runner.invoke(main)
    
    assert result.exit_code == 0
    assert "DevAgent" in result.output
    assert "coding assistant" in result.output