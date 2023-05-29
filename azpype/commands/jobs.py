import pathlib
from .base_command import BaseCommand
from azpype.logging_config import JobsLogger


class Jobs(BaseCommand):
    def __init__(self, job_id=None, **options):
        super().__init__('jobs')
        self.logger = JobsLogger(self.command_name).get_logger()
        self.job_id = job_id
        self.options = options
        
    def list(self):
        """
        List the jobs.

        Returns
        -------
        tuple
            A tuple containing the exit code and output of the command execution.
        """
        args = ['list']
        return super().execute(args, self.options)
    
    def _resume_from_run_id(self, run):
        """
        Takes a run ID and returns the corresponding job ID.

        Parameters
        ----------
        run_id : str: Looks like this: 2023-05-26/11-12-32--snowy-dawn-3904/
        """
        full_path = pathlib.Path("~/.azpype/runs").expanduser() / run / "logs"
    
        log_file = list(full_path.glob('*.log'))[0]

        # Check if a log file exists
        if not log_file:
            raise FileNotFoundError(f"No log file found in {full_path}")

        # Return the name without extension
        return log_file.stem


    def resume(self, job_id=None, run_id=None):
        """
        Resume a specific job.

        Returns
        -------
        tuple
            A tuple containing the exit code and output of the command execution.
        """
        if run_id is not None:
            job_id = self._resume_from_run_id(run_id)
        args = ['resume', job_id]
        return super().execute(args, self.options)
    
    # TODO: Update this to use stdout_parser    
    def last_failed(self):
        """
        Return the last failed job.

        Notes
        -----
            Notice the failure modes are:
            'Failed', 'Cancelled', 'CompletedwithErrors','CompletedWithFailures','CompletedWithErrorsAndSkipped'

        Returns
        -------
        str
            The Job ID of the last failed job.
        """
        exit_code, output = self.list()
        if exit_code != 0:
            raise Exception("Failed to list jobs")

        failure_modes = ['Failed', 'Cancelled', 'CompletedwithErrors','CompletedWithFailures','CompletedWithErrorsAndSkipped']

        # Split the output into lines
        lines = output.split('\n')
        
        current_job_id = None
        for line in lines:
            # New job starts
            if 'JobId' in line:
                current_job_id = line.split(":")[1].strip()

            # Job Status
            elif 'Status' in line:
                current_status = line.split(":")[1].strip()
                if current_status in failure_modes:
                    return current_job_id

        # No failed jobs found
        return None
        
    def recover_last_failed(self):
        """
        Recover the last failed job by resuming it.

        Returns
        -------
        tuple
            A tuple containing the exit code and output of the command execution.
        """
        last_failed_job = self.last_failed()
        if last_failed_job is None:
            raise Exception("No failed jobs to recover")
            
        return self.resume(last_failed_job)
