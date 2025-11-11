import os
import logging
import inspect
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Flag to toggle context information in console output
# Options: "none", "function", "class_function", "full"
CONTEXT_DISPLAY = os.getenv("CONTEXT_DISPLAY", "none")

# ------------------------------------------------------
#                 Define the FINE level
# ------------------------------------------------------
FINE_LEVEL = 15
logging.addLevelName(FINE_LEVEL, "FINE")

def fine(self, message, *args, **kwargs):
    if self.isEnabledFor(FINE_LEVEL):
        self._log(FINE_LEVEL, message, args, **kwargs)

logging.Logger.fine = fine

# ------------------------------------------------------
#              Define the SUCCESS level
# ------------------------------------------------------
SUCCESS_LEVEL = 22
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

logging.Logger.success = success

# ------------------------------------------------------
#              Define the STEP level
# ------------------------------------------------------
STEP_LEVEL = 25
logging.addLevelName(STEP_LEVEL, "STEP")

def step(self, message, *args, **kwargs):
    if self.isEnabledFor(STEP_LEVEL):
        self._log(STEP_LEVEL, message, args, **kwargs)

logging.Logger.step = step

# ------------------------------------------------------
#         Define custom log format for terminal
# ------------------------------------------------------
class ConsoleFormatter(logging.Formatter):
    level_formats = {
        logging.DEBUG: "\x1b[38;21mDEBUG\x1b[0m:\t  %(message)s",  # Grey Level
        FINE_LEVEL: "\x1b[34mFINE\x1b[0m:\t  %(message)s",  # Blue Level
        logging.INFO: "\x1b[32mINFO\x1b[0m:\t  %(message)s",  # Green Level
        SUCCESS_LEVEL: "\x1b[32m★ SUCCESS\x1b[0m:  \x1b[32m%(message)s\x1b[0m",  # Green Level and Message with star
        STEP_LEVEL: "\x1b[35mSTEP\x1b[0m:\t  \x1b[35m%(message)s\x1b[0m",  # Purple Level and Message
        logging.WARNING: "\x1b[33mWARNING\x1b[0m:  %(message)s",  # Yellow Level
        logging.ERROR: "\x1b[31mERROR\x1b[0m:\t  %(message)s",  # Red Level
        logging.CRITICAL: "\x1b[31;1mCRITICAL\x1b[0m: %(message)s",  # Bold Red Level
    }

    def get_context_info(self, record):
        """
        Extract context information (file, class, function) for the log record.
        
        Returns formatted context string based on CONTEXT_DISPLAY setting.
        """
        # Default - no context
        if CONTEXT_DISPLAY == "none":
            return ""
            
        # Start with empty context parts
        context_parts = []
        
        # Get the calling frame
        frame = inspect.currentframe()
        # Go back through the call stack to find the actual logging call
        # Skip logging internal functions
        found_logging_call = False
        while frame:
            frame_info = inspect.getframeinfo(frame)
            frame_name = frame_info.function
            frame_module = frame_info.filename
            
            # Skip logging module frames
            if 'logging' in frame_module and frame_name in ('_log', 'debug', 'info', 'warning', 'error', 'critical', 'fine', 'step', 'success'):
                found_logging_call = True
            elif found_logging_call:
                # This is likely the actual calling frame
                break
                
            frame = frame.f_back
            
        if not frame:
            return ""  # Couldn't determine context
            
        # Extract context information from the frame
        frame_info = inspect.getframeinfo(frame)
        module_path = frame_info.filename
        module_name = Path(module_path).name
        function_name = frame_info.function
        line_number = frame_info.lineno
        
        # Try to determine class name if it's a method call
        class_name = None
        if 'self' in frame.f_locals:
            try:
                class_name = frame.f_locals['self'].__class__.__name__
            except (AttributeError, KeyError):
                pass
                
        # Format context based on display setting
        if CONTEXT_DISPLAY == "function":
            if function_name != "<module>":
                context_parts.append(f"{function_name}()")
                
        elif CONTEXT_DISPLAY == "class_function":
            if class_name:
                context_parts.append(f"{class_name}.{function_name}()")
            elif function_name != "<module>":
                context_parts.append(f"{function_name}()")
                
        elif CONTEXT_DISPLAY == "full":
            if class_name:
                context_parts.append(f"{class_name}.{function_name}() in {module_name}:{line_number}")
            elif function_name != "<module>":
                context_parts.append(f"{function_name}() in {module_name}:{line_number}")
            else:
                context_parts.append(f"{module_name}:{line_number}")
        
        # Combine the context parts
        if context_parts:
            return f"\x1b[90m[{' '.join(context_parts)}]\x1b[0m"  # Grey color for context
        return ""

    def format(self, record):
        log_fmt = self.level_formats.get(record.levelno, "%(levelname)s: %(message)s")
        if record.levelno == SUCCESS_LEVEL:
            # Add a separator line before SUCCESS messages
            log_fmt = "\n\x1b[32m" + "─" * 80 + "\x1b[0m\n" + log_fmt + "\n"
            
        # Format the main message
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        formatted_message = formatter.format(record)
        
        # Get context info if enabled
        if CONTEXT_DISPLAY != "none":
            context_info = self.get_context_info(record)
            if context_info:
                # Get terminal width
                try:
                    terminal_width = shutil.get_terminal_size().columns
                except (AttributeError, ValueError):
                    terminal_width = 80  # Default if can't determine
                
                # Format with context info right-aligned
                message_length = len(formatted_message.strip('\x1b[]0123456789;m'))  # Strip ANSI codes
                padding = max(1, terminal_width - message_length - len(context_info.strip('\x1b[]0123456789;m')) - 2)
                formatted_message = f"{formatted_message}{' ' * padding}{context_info}"
                
        return formatted_message

# ------------------------------------------------------
#              Define detailed log format
# ------------------------------------------------------
class LogFileFormatter(logging.Formatter):
    detail_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)"

    def __init__(self, fmt=detail_format, datefmt="%Y-%m-%d %H:%M:%S"):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        return super().format(record)

# Function to configure logging
def configure_logging(logger_name="root", log_level=None, keep_logs=False, log_dir="logs"):
    """
    Configures the logging for the application.

    Args:
        logger_name (str): The name of the logger to be configured. Defaults to "root".
        log_level (int, optional): The level of logging to be used. If None, reads from environment.
        keep_logs (bool): If set to True, logs will be kept in a file. Defaults to False.
        log_dir (str): Directory where log files will be stored. Defaults to "logs".
    """
    # Dynamically read the environment variable if log_level not provided
    if log_level is None:
        default_log_level = 15  # Default level if LOG_LEVEL is not set
        log_level = int(os.getenv("LOG_LEVEL", default_log_level))
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Check if handlers already exist to prevent duplication
    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(ConsoleFormatter())
        logger.addHandler(console_handler)

        if keep_logs:
            # Create log directory if it doesn't exist
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True, parents=True)
            
            # File Handler with detailed messages
            log_file = log_path / "logs.log"
            file_handler = RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=3
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(LogFileFormatter())
            logger.addHandler(file_handler)

    # Prevent logging from propagating to the root logger
    logger.propagate = False
    
    return logger