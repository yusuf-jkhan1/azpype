from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import time
from .base_command import BaseCommand
from azpype.logging_config import CopyLogger
from azpype.validators import validate_azcopy_envs, validate_login_type, validate_azure_blob_url, validate_local_path, validate_network_available

class Copy(BaseCommand):
    def __init__(self, source: str, destination: str, sas_token:str = None, **options):
        """
        Initialize a new instance of the Copy class.

        Parameters
        ----------
        source : str
            The source URL or path for the copy operation.
        destination : str
            The destination URL or path for the copy operation.
        **options : dict
            Optional arguments for the copy operation. Available options include:

            - as-subdir : bool
                Places folder sources as subdirectories under the destination. (default: True)
            - block-size-mb : float
                Use this block size (specified in MiB) when uploading to Azure Storage, and downloading from Azure Storage. The default value is automatically calculated based on file size. Decimal fractions are allowed.
            - check-length : bool
                Check the length of a file on the destination after the transfer. If there's a mismatch between source and destination, the transfer is marked as failed. (default: True)
            - dry-run : bool
                Prints the file paths that would be copied by this command. This flag doesn't copy the actual files.
            - exclude-path : str
                Exclude these paths when copying. This option doesn't support wildcard characters (*). Checks relative path prefix.
            - exclude-pattern : str
                Exclude these files when copying. This option supports wildcard characters (*).
            - exclude-regex : str
                Exclude all the relative path of the files that align with regular expressions. Separate regular expressions with ';'.
            - follow-symlinks : bool
                Follow symbolic links when uploading from local file system.
            - force-if-read-only : bool
                When overwriting an existing file on Windows or Azure Files, force the overwrite to work even if the existing file has its read-only attribute set.
            - include-after : str
                Include only those files modified on or after the given date/time. The value should be in ISO8601 format.
            - include-before : str
                Include only those files modified before or on the given date/time. The value should be in ISO8601 format.
            - include-path : str
                Include only these paths when copying. This option doesn't support wildcard characters (*). Checks relative path prefix.
            - include-pattern : str
                Include only these files when copying. This option supports wildcard characters (*). Separate files by using a ';'.
            - include-regex : str
                Include only the relative path of the files that align with regular expressions. Separate regular expressions with ';'.
            - log-level : str
                Define the log verbosity for the log file, available levels: INFO(all requests/responses), WARNING(slow responses), ERROR(only failed requests), and NONE(no output logs). (default: "INFO")
            - metadata : str
                Upload to Azure Storage with these key-value pairs as metadata.
            - overwrite : str
                Overwrite the conflicting files and blobs at the destination if this flag is set to true. Possible values include 'true', 'false', 'prompt', and 'ifSourceNewer'. (default: "true")
            - put-md5 : bool
                Create an MD5 hash of each file, and save the hash as the Content-MD5 property of the destination blob or file. Only available when uploading.
            - recursive : bool
                Look into subdirectories recursively when uploading from local file system.

        """
        super().__init__('copy')
        self.run_name, self.run_log_directory, self.logger = CopyLogger(self.command_name).get_logger()
        self.logger.info(f"Run name: {self.run_name}")
        self.logger.info(f"Run log directory: {self.run_log_directory}")

        self.source = source
        self.sas_token = sas_token
        if self.sas_token:
            self.destination = f"{destination}?{self.sas_token}"
        else:
            self.destination = destination
        valid, failed_checks = self.prevalidation()
        if valid:
            self.options = self.build_flags(options)
        else:
            self.logger.info(f"Invalid options passed to Copy command. Failed checks: {failed_checks}")
            raise Exception(f"Invalid options passed to Copy command. Failed checks: {failed_checks}")
        self.logger.info(f"Preliminary checks passed: {self.run_prechecks()}")

    def prevalidation(self):
        validation_results = {
            "is_valid_local_path": validate_local_path(self.source, self.logger),
            "is_valid_blob_url_format": validate_azure_blob_url(self.destination, self.logger)
        }

        failed_checks = [check for check, result in validation_results.items() if not result]

        return not failed_checks, failed_checks

        
    def execute(self):
        """
        Execute the copy command with the given source, destination, and options.

        Returns
        -------
        tuple
            A tuple containing the exit code and output of the command execution.
        """
        args = [self.source, self.destination]
        return super().execute(args, self.options)



class MonitoredCopy(Copy):
    def __init__(self, source: str, destination: str, **options):
        super().__init__(source, destination, **options)
        self.source = source
        self.destination = destination
        self.observer = Observer()

    def _is_network_filesystem(self):
        if platform.system() == 'Windows' and self.source.startswith('\\\\'):
            return True

        elif platform.system() in ('Linux', 'Darwin'):
            try:
                df_output = subprocess.check_output(['df', self.source]).decode().split("\n")
                fs_type = df_output[1].split()[-1]
                return fs_type in ('nfs', 'smbfs', 'cifs')
            except:
                pass
            return False

    def _set_observer(self):
        if _is_network_filesystem:
            self.observer = PollingObserver()
        else:
            self.observer = Observer()

    class CopyHandler(FileSystemEventHandler):
        def __init__(self, monitored_copy):
            self.monitored_copy = monitored_copy

        def on_any_event(self, event):
            if not event.is_directory:
                self.monitored_copy.execute()
                
    def execute_with_monitoring(self):
        event_handler = self.CopyHandler(self)
        self.observer.schedule(event_handler, path=self.source, recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()