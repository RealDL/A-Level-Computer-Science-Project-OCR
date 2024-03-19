import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the base logging level

# Create a logger instance
logger = logging.getLogger(__name__)
logger.propagate = False  # Disable propagation to parent logger

# Create a formatter for the log messages
class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[1;34m",    # Blue for DEBUG
        logging.INFO: "\033[1;29m",     # Grey for INFO
        logging.WARNING: "\033[1;33m",  # Yellow for WARNING
        logging.ERROR: "\033[1;91m",    # Orange for ERROR
        logging.CRITICAL: "\033[1;31m"  # Red for CRITICAL
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "\033[0m")  # Default to no color
        log_level = record.levelname
        timestamp = self.formatTime(record, self.datefmt)
        message = log_color + log_level + "\033[0m" + " - " + record.msg
        return f"{timestamp} - {message}"

# Create a handler for console output with the colored formatter
colored_console_handler = logging.StreamHandler()
colored_console_handler.setFormatter(ColoredFormatter())

# Add the colored handler to the logger
logger.addHandler(colored_console_handler)

logger.info("RealDL Logger Code.")
