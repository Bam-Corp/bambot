import pytest
import os
from click.testing import CliRunner
from bambot import cli


@pytest.fixture
def runner():
    return CliRunner()

def test_build(runner):
    with runner.isolated_filesystem():
        with open("bot.py", "w") as f:
            f.write("# Test bot file")

        result = runner.invoke(cli, ["build"])
        assert result.exit_code == 0
        assert "Deployment files generated successfully." in result.output
        assert "Dockerfile" in os.listdir()
        assert "Procfile" in os.listdir()
        assert "agent_readme.md" in os.listdir()

def test_run_without_docker(runner):
    result = runner.invoke(cli, ["run"])
    assert result.exit_code == 0
    assert "Docker daemon is not running." in result.output

def test_clean(runner):
    with runner.isolated_filesystem():
        with open("Dockerfile", "w") as f:
            f.write("# Test Dockerfile")
        with open("Procfile", "w") as f:
            f.write("# Test Procfile")
        with open("agent_readme.md", "w") as f:
            f.write("# Test agent_readme")
        os.mkdir("output.zip")

        result = runner.invoke(cli, ["clean"])
        assert result.exit_code == 0
        assert "Clean up completed successfully." in result.output
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("Procfile")
        assert not os.path.exists("agent_readme.md")
        assert not os.path.exists("output.zip")