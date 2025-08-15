from rich.console import Console
from rich.table import Table

class AzCopyStdoutParser(object):
    def __init__(self, stdout):
        self.stdout = stdout
        self.job_id = None
        self.total_bytes_transferred = None
        self.final_job_status = None
        self.elapsed_time = None
        self.number_of_file_transfers = None
        self.number_of_folder_property_transfers = None
        self.number_of_symlink_transfers = None
        self.total_number_of_transfers = None
        self.number_of_file_transfers_completed = None
        self.number_of_folder_transfers_completed = None
        self.number_of_file_transfers_failed = None
        self.number_of_folder_transfers_failed = None
        self.number_of_file_transfers_skipped = None
        self.number_of_folder_transfers_skipped = None

        self._parse_stdout()

    def _parse_stdout(self):
        lines = self.stdout.split('\n')
        for line in lines:
            self._general_extract(line)

    def _general_extract(self, line):
        extract_info = {
            "Job": {"attr": "job_id", "type": str},
            "TotalBytesTransferred:": {"attr": "total_bytes_transferred", "type": int},
            "Final Job Status:": {"attr": "final_job_status", "type": str},
            "Elapsed Time (Minutes):": {"attr": "elapsed_time", "type": float},
            "Number of File Transfers:": {"attr": "number_of_file_transfers", "type": int},
            "Number of Folder Property Transfers:": {"attr": "number_of_folder_property_transfers", "type": int},
            "Number of Symlink Transfers:": {"attr": "number_of_symlink_transfers", "type": int},
            "Total Number of Transfers:": {"attr": "total_number_of_transfers", "type": int},
            "Number of File Transfers Completed:": {"attr": "number_of_file_transfers_completed", "type": int},
            "Number of Folder Transfers Completed:": {"attr": "number_of_folder_transfers_completed", "type": int},
            "Number of File Transfers Failed:": {"attr": "number_of_file_transfers_failed", "type": int},
            "Number of Folder Transfers Failed:": {"attr": "number_of_folder_transfers_failed", "type": int},
            "Number of File Transfers Skipped:": {"attr": "number_of_file_transfers_skipped", "type": int},
            "Number of Folder Transfers Skipped:": {"attr": "number_of_folder_transfers_skipped", "type": int}
        }

        for key, info in extract_info.items():
            if key in line:
                attr = info["attr"]
                value = line.split(":")[1].strip() if ":" in line else line.split()[1]
                setattr(self, attr, info["type"](value))

    def summary(self) -> str:
        """Return Rich-formatted summary of the transfer operation."""
        console = Console()
        
        # Determine status icon and color
        status_icon = "✅"
        status_color = "green"
        if self.final_job_status:
            if "Failed" in self.final_job_status:
                status_icon = "❌"
                status_color = "red"
            elif "Skipped" in self.final_job_status or "Error" in self.final_job_status:
                status_icon = "⚠️"
                status_color = "yellow"

        # Create summary table
        table = Table(title=f"{status_icon} Transfer Summary", title_style=status_color)
        table.add_column("Metric", style="cyan", min_width=20)
        table.add_column("Value", style="magenta")

        # Add rows with safe handling of None values
        table.add_row("Status", str(self.final_job_status or "Unknown"))
        table.add_row("Files Completed", str(self.number_of_file_transfers_completed or 0))
        table.add_row("Files Skipped", str(self.number_of_file_transfers_skipped or 0))
        table.add_row("Files Failed", str(self.number_of_file_transfers_failed or 0))
        
        if self.elapsed_time is not None:
            table.add_row("Elapsed Time", f"{self.elapsed_time} minutes")
        
        if self.total_bytes_transferred is not None:
            bytes_str = f"{self.total_bytes_transferred:,} bytes" if self.total_bytes_transferred > 0 else "0 bytes"
            table.add_row("Bytes Transferred", bytes_str)
        
        if self.job_id:
            # Truncate job ID for display
            job_display = self.job_id[:16] + "..." if len(self.job_id) > 16 else self.job_id
            table.add_row("Job ID", job_display)

        # Render to string using console
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()
