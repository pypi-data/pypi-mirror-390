from typing import Optional

class ElasticConfig:
    """
    Configuration for an Elasticsearch instance.

    Args:
        host (str): The hostname or IP address of the Elasticsearch server.
        port (int): The port number for the Elasticsearch server.
        index (str): The name of the index where logs will be stored.
        username (str): The username for Basic Authentication.
        password (str): The password for Basic Authentication.
    """
    def __init__(
        self, host: str, port: int, index: str, username: str, password: str
    ) -> None: ...
    @classmethod
    def from_env(cls, local_only: Optional[bool] = False) -> "ElasticConfig":
        """
        Creates a new ElasticConfig instance by reading from environment variables.

        Reads from a `.env` file in the current directory or parent directories.
        Will raise a ValueError if any of the required ELASTIC_* variables are missing.

        Args:
            local_only (Optional[bool]): Search for a `.env` file only in a parent directory.
        """
        ...

class LoggerBuilder:
    """A fluent builder for creating and configuring a `Logger`."""

    def __init__(self) -> None: ...
    def with_batch_size(self, size: int) -> "LoggerBuilder":
        """
        Sets the maximum number of logs to buffer before a flush is triggered.

        Args:
            size (int): The number of log messages to hold in the buffer.
        """
        ...
    def with_channel_size(self, size: int) -> "LoggerBuilder":
        """
        Sets the maximum number of logs in channel.

        Args:
            size (int): The number of log messages to hold in the channel.
        """
        ...

    def with_flush_interval(self, interval_seconds: float) -> "LoggerBuilder":
        """
        Sets the maximum time to wait before flushing the buffer, even if not full.

        Args:
            interval_seconds (float): The flush interval in seconds.
        """
        ...

    def with_stdout(self, enabled: bool) -> "LoggerBuilder":
        """Enable or disable logging to standard output (default: enabled)."""
        ...

    def with_base_log(self, enabled: bool) -> "LoggerBuilder":
        """
        Enable or disable base logging prefix '[<event.timestamp>] <event.level>:' (default: disabled).
        """
        ...

    def with_file_output(self, session_name: Optional[str]) -> "LoggerBuilder":
        """
        Enable logging to a file in the 'log_records' directory.

        Args:
            session_name (str | None): A prefix for the log file name.
                                       Defaults to "log" if not provided.
        """
        ...

    def without_file_output(self) -> "LoggerBuilder":
        """Disable file logging."""
        ...

    def with_elastic_output(self, config: ElasticConfig) -> "LoggerBuilder":
        """
        Enable logging to Elasticsearch with the given configuration.

        Args:
            config (ElasticConfig): The configuration for the Elasticsearch instance.
        """
        ...

    def build(self) -> "Logger":
        """
        Builds the logger, spawning the background worker thread.

        Returns:
            Logger: A logger handle that can be used to send logs.
        """
        ...

class Logger:
    """
    A high-performance, non-blocking logger handle.

    Log calls on this handle are sent to a background thread and return immediately.
    The handle is cheap to clone and can be shared across multiple threads.
    """
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def flush(self) -> None:
        """
        Blocks until all previously queued log messages have been processed.
        Call this before your application exits to prevent losing logs.
        """
        ...
    def __del__(self) -> None: ...
