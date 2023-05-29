import os
import yaml
import json
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from azpype.retry import RetryPolicy
from azpype.logging_config import NullLogger
from azpype.validators import validate_azcopy_envs, validate_login_type, validate_network_available


class BaseCommand(ABC):
    def __init__(self, command_name: str, retry_policy=None):
        self.command_name = command_name
        self.retry_policy = retry_policy or RetryPolicy()
        self.azcopy_path = os.path.expanduser("~/.azpype/azcopy") #Executable
        self.logger = NullLogger(__name__)


    def build_flags(self, options: dict):
        config = {}  
        config_path = Path("~/.azpype/copy_config.yaml").expanduser() #Hardcoded for now
        with open(config_path,'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.logger.info(exc)

        # Delete keys with value of NULL
        config = {k: v for k, v in config.items() if v != 'NULL'}
            
        if options is not None:
            config.update(options)
        self.logger.info(f"\nFlag Config: {json.dumps(config, indent=4)}\n")
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
        command = self.build_command(args, options)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            self.logger.info(f"\n======Command=======\n {' '.join(command)}\n")
            self.logger.info(f"\n======Output======\n{result.stdout}")
            return result.returncode, result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.info(f"Execution failed: {str(e)}\nOutput: {e.output}\nError: {e.stderr}")
            return e.returncode, e.output

