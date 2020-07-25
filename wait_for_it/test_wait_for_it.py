"""wait_for_it cli test module"""
from unittest import TestCase

from click.testing import CliRunner
from .wait_for_it import cli


class CliTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # https://click.palletsprojects.com/en/7.x/testing/
        cls._runner = CliRunner()

    def test_help(self):
        result = self._runner.invoke(cli, ["--help"])
        assert 'Usage:' in result.output
        assert result.exit_code == 0
