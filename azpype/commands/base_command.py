import os
import yaml
import json
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from azpype.retry import RetryPolicy
from azpype.resource_paths import get_azcopy_path, ensure_user_config
from azpype.logging_config import NullLogger
from azpype.validators import validate_azcopy_envs, validate_login_type, validate_network_available


class BaseCommand(ABC):
    def __init__(self, command_name: str, retry_policy=None):
        self.command_name = command_name
        self.retry_policy = retry_policy or RetryPolicy()
        self.azcopy_path = get_azcopy_path()
        self.logger = NullLogger(__name__)


    def build_flags(self, options: dict):
        config = {}
        config_path = ensure_user_config()
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.logger.info(exc)

        # Delete keys with value of NULL or None
        config = {k: v for k, v in config.items() if v not in ['NULL', None]}
            
        if options is not None:
            # Also filter None values from runtime options
            filtered_options = {k: v for k, v in options.items() if v is not None}
            config.update(filtered_options)
        
        # Log detailed config to file only (suppress console output since we have Rich table)
        # We'll skip the logger.info() call here to avoid duplication
        
        # Show pretty config on console if there are any flags
        if config:
            console = Console()
            from rich.table import Table
            
            table = Table(title="🏁 Configuration Flags", title_style="blue")
            table.add_column("Flag", style="cyan", min_width=15)
            table.add_column("Value", style="magenta")
            
            for key, value in config.items():
                table.add_row(f"--{key}", str(value))
            
            console.print(table)
        
        return config

        
    def run_prechecks(self):
        """
        Run prechecks to ensure that the command can be executed.
        """
        envs_exist = validate_azcopy_envs(['AZCOPY_SPA_CLIENT_SECRET', 'AZCOPY_SPA_APPLICATION_ID', 'AZCOPY_TENANT_ID', 'AZCOPY_AUTO_LOGIN_TYPE'], self.logger)
        login_spn = validate_login_type(self.logger)
        network_available = validate_network_available(self.logger)
        return all ([envs_exist, login_spn, network_available])


    def build_command(self, args: list, options: dict):
        """
        Build a command to be executed using azcopy.

        Parameters
        ----------
        args : list
            List of arguments for the azcopy command.
        options : dict
            Dictionary of options for the azcopy command.

        Returns
        -------
        list
            A list containing the command parts to be executed.
        """
        cmd_parts = [self.azcopy_path, self.command_name] + args
        for option, value in options.items():
            if isinstance(value, bool) and value:
                cmd_parts.append(f"--{option}=true")
            elif value is not None:
                cmd_parts.append(f"--{option}={value}")
        return cmd_parts

    def _format_command_readable(self, args: list, options: dict) -> str:
        """Format command in a readable multi-line format."""
        lines = ["azcopy " + self.command_name + " \\"]
        
        # Add positional arguments with labels
        if len(args) >= 1:
            lines.append(f"  source: {args[0]} \\")
        if len(args) >= 2:
            lines.append(f"  destination: {args[1]} \\")
        if len(args) > 2:
            for i, arg in enumerate(args[2:], start=3):
                lines.append(f"  arg{i}: {arg} \\")
        
        # Add options
        for option, value in options.items():
            if isinstance(value, bool) and value:
                lines.append(f"  --{option}=true \\")
            elif value is not None:
                lines.append(f"  --{option}={value} \\")
        
        # Remove trailing backslash from last line
        if lines[-1].endswith(" \\"):
            lines[-1] = lines[-1][:-2]
        
        return "\n".join(lines)

    def execute(self, args: list, options: dict):
        """
        Execute the built command and handle any exceptions.

        Parameters
        ----------
        args : list
            List of arguments for the azcopy command.
        options : dict
            Dictionary of options for the azcopy command.

        Returns
        -------
        tuple
            A tuple containing the exit code and output of the command execution.
        """
        console = Console()
        command = self.build_command(args, options)
        
        # Pretty command display with readable format
        readable_cmd = self._format_command_readable(args, options)
        syntax = Syntax(readable_cmd, "bash", theme="monokai", word_wrap=True)
        console.print(Panel(syntax, title="🚀 Executing Command", border_style="blue"))
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            # Log to file with original format (detailed logging) - suppress console to avoid duplication
            # Skip these logger.info() calls since we now have Rich panels
            
            # Pretty console output (Rich panels only, no duplication)
            if result.stdout:
                console.print(Panel(result.stdout, title="📋 Command Output", border_style="green"))
            if result.stderr:
                console.print(Panel(f"[yellow]{result.stderr}[/yellow]", title="⚠️ Warning Output", border_style="yellow"))
            
            return result.returncode, result.stdout
            
        except subprocess.CalledProcessError as e:
            # Log to file with original format (detailed logging) - suppress console to avoid duplication
            # Skip logger.info() call since we now have Rich panels
            
            # Pretty console error display (Rich panels only)
            error_content = []
            if e.stdout:
                error_content.append(f"[white]Stdout:[/white]\n{e.stdout}")
            if e.stderr:
                error_content.append(f"[white]Stderr:[/white]\n{e.stderr}")
            
            error_text = "\n\n".join(error_content) if error_content else str(e)
            console.print(Panel(f"[red]{error_text}[/red]", title="❌ Command Failed", border_style="red"))
            
            return e.returncode, e.stdout

