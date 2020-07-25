"""wait_for_it cli test module"""
from click.testing import CliRunner
from .wait_for_it import cli


# https://click.palletsprojects.com/en/7.x/testing/
def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert 'Usage:' in result.output
    assert result.exit_code == 0
