from datetime import datetime
import CONFIG

class Logger:
    """
    Simple logger class that prints formatted log messages to the console.

    Logs messages with timestamp, level, and component information.
    """

    def log(self, component, *args, level="INFO", **kwargs):
        """
        Log a message with a specified component and level.

        Args:
            component (str): Name of the component generating the log.
            *args: Positional arguments to include in the log message.
            level (str, optional): Log level (e.g., "INFO", "DEBUG", "ERROR"). Defaults to "INFO".
            **kwargs: Keyword arguments to include in the log message.
        """
        log_message = f"[{datetime.now().isoformat()}] [{level}] [{component}] -> "
        log_part = [str(arg) for arg in args] + [f"{key}: {value}" for key, value in kwargs.items()]
        log_message += " | ".join(log_part)
        
        print(log_message)


logger = Logger()
