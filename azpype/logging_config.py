import os
from pathlib import Path
import logging
from haikunator import Haikunator
from datetime import datetime


ROOT_LOG_DIRECTORY = Path('~/.azpype/runs/')
LOGGING_LEVEL = logging.INFO

class NullLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def handle(self, record):
        pass

    def emit(self, record):
        pass

class CopyLogger:
    """
    Configures a logger with the specified name and log directory.

    Parameters
    ----------
    name : str
        The name of the logger.
    log_directory : Path, optional
        The directory to store the log files. Defaults to DEFAULT_LOG_DIRECTORY.
    log_level : int, optional
        The logging level. Defaults to LOGGING_LEVEL.

    Returns
    -------
    tuple of Path and logging.Logger
        A tuple containing the base run directory and the configured logger.

    Notes
    -----
    This function configures the logger by creating a unique run directory based on the current date and time,
    setting up the log and job plan directories within the run directory, and configuring the logger handlers.
    The run directory and the configured logger are returned as a tuple.

    The log files will be stored in the 'logs' subdirectory under the run directory,
    and the job plan files will be stored in the 'plans' subdirectory.

    The log directory and job plan directory paths are expanded to the actual home directory if '~' is used.

    The 'base_run_directory' in the returned tuple represents the top-level directory for the current run,
    while the 'logger' is an instance of the 'logging.Logger' class that is configured with the specified name,
    log level, and log handlers.

    Example
    -------
    >>> base_run_directory, logger = configure_logger('my_logger')
    >>> logger.info('This is a log message')
    >>> print(base_run_directory)
    '/path/to/root_log_directory/YYYY-mm-dd/HH-MM-SS--adjective-noun-1234'
    """


    def __init__(self, name, root_log_directory=ROOT_LOG_DIRECTORY, log_level=LOGGING_LEVEL):
        self.name = name
        self.root_log_directory = root_log_directory
        self.log_level = log_level
        self._configure()

    def _configure(self):
        # Create unique run directory name parts
        current_datetime = datetime.now()
        day = current_datetime.strftime("%Y-%m-%d")
        hms = current_datetime.strftime("%H-%M-%S")
        uid = Haikunator().haikunate()

        # Create run log and run job plan directories
        self.run_name = f"{hms}--{uid}"
        self.base_run_directory = Path(self.root_log_directory).expanduser() / day / self.run_name

        self.run_log_directory = self.base_run_directory / "logs"
        self.run_log_directory = self.run_log_directory.expanduser()
        self.run_log_directory.mkdir(parents=True, exist_ok=True)

        # Set rutime environment variables for AzCopy to register
        self._configure_path_envs()

        # Setup file and console logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        handler = logging.FileHandler(str(self.run_log_directory / 'azpype.log'))
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        handler_error = logging.StreamHandler()
        handler_error.setLevel(self.log_level)
        handler_error.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        self.logger.addHandler(handler)
        self.logger.addHandler(handler_error)

    def _configure_path_envs(self):
        """Sets the AZCOPY_JOB_PLAN_LOCATION and AZCOPY_LOG_LOCATION environment variables."""
        os.environ['AZCOPY_JOB_PLAN_LOCATION'] = (ROOT_LOG_DIRECTORY.expanduser() / 'plans').as_posix()
        os.environ['AZCOPY_LOG_LOCATION'] = self.run_log_directory.as_posix()

    def get_logger(self):
        return self.run_name, self.run_log_directory.as_posix(),self.logger
    
class JobsLogger():
    def __init__(self, name, root_log_directory=ROOT_LOG_DIRECTORY, log_level=LOGGING_LEVEL):
        self.name = name
        os.environ['AZCOPY_JOB_PLAN_LOCATION'] = (ROOT_LOG_DIRECTORY.expanduser() / 'plans').as_posix()
        self.root_log_directory = root_log_directory
        self.log_level = log_level
        self._configure()

    def _configure(self):
        # Create unique run directory name parts
        current_datetime = datetime.now()
        day = current_datetime.strftime("%Y-%m-%d")
        hms = current_datetime.strftime("%H-%M-%S")
        uid = Haikunator().haikunate()

        # Create run log and run job plan directories
        self.run_name = f"{hms}--{uid}"
        self.base_run_directory = Path(self.root_log_directory) / day / self.run_name

        self.run_log_directory = self.base_run_directory / "logs"
        self.run_log_directory = self.run_log_directory.expanduser()
        self.run_log_directory.mkdir(parents=True, exist_ok=True)

        self.job_plan_directory = ROOT_LOG_DIRECTORY.expanduser() / 'plans'

        # Set rutime environment variables for AzCopy to register
        #self._configure_path_envs()

        # Setup file and console logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # handler = logging.FileHandler(str(self.run_log_directory / 'azpype.log'))
        # handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        handler_error = logging.StreamHandler()
        handler_error.setLevel(self.log_level)
        handler_error.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        #self.logger.addHandler(handler)
        self.logger.addHandler(handler_error)
    def get_logger(self):
        return self.logger