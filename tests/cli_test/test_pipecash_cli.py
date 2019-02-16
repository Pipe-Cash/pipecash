#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pipecash` package."""


import unittest
from click.testing import CliRunner

from pipecash import cli


class TestPipecash(unittest.TestCase):

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pipecash.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
