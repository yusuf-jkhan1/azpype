import sys
sys.path.append('../')
import unittest
from unittest.mock import patch, Mock
from azpype.commands.base_command import BaseCommand
import subprocess
from pathlib import Path


class TestBaseCommand(unittest.TestCase):
    def setUp(self):
        self.command = BaseCommand("test_command")

    def test_build_command(self):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        expected_command = [str(Path("~/.azpype/azcopy").expanduser()), "test_command", "arg1", "arg2", "--option1=value1", "--option2=true"]
        self.assertEqual(self.command.build_command(args, options), expected_command)

    @patch("subprocess.run")
    def test_execute_success(self, mock_run):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        mock_run.return_value = Mock(returncode=0, stdout="Success")
        expected_output = (0, "Success")
        self.assertEqual(self.command.execute(args, options), expected_output)

    @patch("subprocess.run")
    def test_execute_failure(self, mock_run):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        mock_run.side_effect = subprocess.CalledProcessError(1, "test_command", "Error")
        expected_output = (1, "Error")
        self.assertEqual(self.command.execute(args, options), expected_output)


if __name__ == "__main__":
    unittest.main()