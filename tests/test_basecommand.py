import sys
sys.path.append('../')
import unittest
from unittest.mock import patch, Mock, mock_open
from azpype.commands.base_command import BaseCommand
from azpype.resource_paths import get_azcopy_path
import subprocess
import yaml


# Create a concrete implementation for testing
class ConcreteCommand(BaseCommand):
    def __init__(self, command_name):
        super().__init__(command_name)


class TestBaseCommand(unittest.TestCase):
    def setUp(self):
        self.command = ConcreteCommand("test_command")

    def test_build_command(self):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        expected_command = [get_azcopy_path(), "test_command", "arg1", "arg2", "--option1=value1", "--option2=true"]
        self.assertEqual(self.command.build_command(args, options), expected_command)

    @patch("subprocess.run")
    def test_execute_success(self, mock_run):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        expected_output = (0, "Success")
        self.assertEqual(self.command.execute(args, options), expected_output)

    @patch("subprocess.run")
    def test_execute_failure(self, mock_run):
        args = ["arg1", "arg2"]
        options = {"option1": "value1", "option2": True}
        error = subprocess.CalledProcessError(1, "test_command", "Error")
        error.stdout = "Error"
        error.stderr = ""
        mock_run.side_effect = error
        expected_output = (1, "Error")
        self.assertEqual(self.command.execute(args, options), expected_output)

    def test_build_command_with_underscores(self):
        """Test that underscores in option names are preserved in build_command"""
        args = ["source", "dest"]
        options = {"put_md5": True, "check_length": True, "dry_run": False}
        # Note: build_command expects options already converted to hyphens
        # The conversion happens in build_flags
        options_with_hyphens = {"put-md5": True, "check-length": True, "dry-run": False}
        expected_command = [
            get_azcopy_path(), 
            "test_command", 
            "source", 
            "dest", 
            "--put-md5=true",
            "--check-length=true"
        ]
        actual_command = self.command.build_command(args, options_with_hyphens)
        # Check that the hyphenated options are in the command
        self.assertIn("--put-md5=true", actual_command)
        self.assertIn("--check-length=true", actual_command)
        self.assertNotIn("--dry-run", actual_command)  # False values should not be included

    @patch("builtins.open", new_callable=mock_open, read_data="key1: value1\nkey2: value2")
    @patch("azpype.resource_paths.ensure_user_config")
    def test_build_flags_underscore_to_hyphen(self, mock_ensure_config, mock_file):
        """Test that build_flags converts underscores to hyphens in option keys"""
        mock_ensure_config.return_value = "/fake/path/config.yaml"
        
        # Test with underscores in option names
        options = {
            "put_md5": True,
            "check_length": True,
            "as_subdir": False,
            "dry_run": None  # Should be filtered out
        }
        
        result = self.command.build_flags(options)
        
        # Check that underscores were converted to hyphens
        self.assertIn("put-md5", result)
        self.assertIn("check-length", result)
        self.assertIn("as-subdir", result)
        
        # Check that None values were filtered out
        self.assertNotIn("dry-run", result)
        self.assertNotIn("dry_run", result)
        
        # Check that values are preserved
        self.assertEqual(result["put-md5"], True)
        self.assertEqual(result["check-length"], True)
        self.assertEqual(result["as-subdir"], False)


if __name__ == "__main__":
    unittest.main()