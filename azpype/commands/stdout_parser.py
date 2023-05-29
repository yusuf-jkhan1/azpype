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
