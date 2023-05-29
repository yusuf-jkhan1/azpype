import time

class RetryPolicy:
    def __init__(self, max_retries=3, initial_wait_time=15, backoff_factor=2):
        """
        Initializes a new instance of the RetryPolicy class.

        Parameters
        ----------
        max_retries : int, optional
            The maximum number of times to retry the operation. Default is 3.
        initial_wait_time : float, optional
            The initial amount of time to wait before retrying the operation. Default is 1.
        backoff_factor : float, optional
            The factor by which to increase the wait time between retries. Default is 2.
        """
        self.max_retries = max_retries
        self.initial_wait_time = initial_wait_time
        self.backoff_factor = backoff_factor

    def should_retry(self, result_code, result_output, retry_count):
        """
        Determines whether the operation should be retried.

        Parameters
        ----------
        result_code : int
            The result code of the operation.
        result_output : str
            The output of the operation.
        retry_count : int
            The number of times the operation has been retried.

        Returns
        -------
        bool
            True if the operation should be retried, False otherwise.
        """
        if retry_count >= self.max_retries:
            return False
        return result_code != 0

    def wait_before_retry(self, retry_count):
        """
        Waits for a certain amount of time before retrying the operation.

        Parameters
        ----------
        retry_count : int
            The number of times the operation has been retried.
        """
        wait_time = self.initial_wait_time * (self.backoff_factor ** (retry_count - 1))
        time.sleep(wait_time)