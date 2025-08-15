import os
import sys
from pathlib import Path
from loguru import logger


class AzpypeLogger:
    """
    Simplified logging configuration using loguru.
    
    Creates logs in ~/.azpype/ with daily rotation and compression.
    Sets up AzCopy environment variables for job plans and logs.
    """
    
    def __init__(self, command_name="azpype"):
        self.command_name = command_name
        self.base_dir = Path("~/.azpype").expanduser()
        self._setup_directories()
        self._configure_logger()
        self._set_azcopy_envs()
    
    def _setup_directories(self):
        """Create necessary directories for logging and AzCopy."""
        self.base_dir.mkdir(exist_ok=True)
        
        # Create azcopy logs directory (avoid conflict with existing azcopy binary file)
        azcopy_logs_dir = self.base_dir / "azcopy_logs"
        azcopy_logs_dir.mkdir(exist_ok=True, parents=True)
        
        (self.base_dir / "plans").mkdir(exist_ok=True, parents=True)
    
    def _configure_logger(self):
        """Configure loguru with file rotation and console output."""
        # Remove default handler
        logger.remove()
        
        # File handler with daily rotation and compression
        logger.add(
            self.base_dir / "azpype_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            compression="gz",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[command]} | {message}",
            level="INFO"
        )
        
        # Console handler with colors
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> [<level>{level}</level>] [<cyan>{extra[command]}</cyan>] {message}",
            colorize=True,
            level="INFO"
        )
    
    def _set_azcopy_envs(self):
        """Set AzCopy environment variables for job plans and logs."""
        os.environ['AZCOPY_JOB_PLAN_LOCATION'] = str(self.base_dir / "plans")
        os.environ['AZCOPY_LOG_LOCATION'] = str(self.base_dir / "azcopy_logs")
    
    def get_logger(self):
        """Return a bound logger with command context."""
        return logger.bind(command=self.command_name.upper())


# Legacy aliases for backward compatibility
class CopyLogger(AzpypeLogger):
    """Legacy alias for Copy commands."""
    def __init__(self, command_name):
        super().__init__(command_name)
    
    def get_logger(self):
        """Return logger in legacy format (run_name, run_log_directory, logger)."""
        bound_logger = super().get_logger()
        # Return simplified values - no more complex run directories
        return "simplified", str(self.base_dir), bound_logger


class JobsLogger(AzpypeLogger):
    """Legacy alias for Jobs commands."""  
    def __init__(self, command_name):
        super().__init__(command_name)


# Keep NullLogger for base_command compatibility
class NullLogger:
    """Null logger for cases where no logging is needed."""
    def __init__(self, name):
        _ = name  # Suppress unused parameter warning
    
    def info(self, msg): 
        _ = msg  # Suppress unused parameter warning
    def warning(self, msg): 
        _ = msg  # Suppress unused parameter warning
    def error(self, msg): 
        _ = msg  # Suppress unused parameter warning
    def debug(self, msg): 
        _ = msg  # Suppress unused parameter warning