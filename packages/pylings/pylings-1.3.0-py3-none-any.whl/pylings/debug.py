"""
logging_setup.py: Configures logging for the Pylings application.

This module defines the `setup_logging` function, which enables file-based
logging when the application is run in debug mode. Logs are written to a
predefined file path (`DEBUG_PATH`) and include timestamps, severity levels,
source modules, and message content.

Usage:
    Call `setup_logging(debug=True)` early in the application to enable
    debug-level logging to file.

Intended for use by CLI entry points and debugging support.
"""
import logging
from pylings.constants import DEBUG_PATH

def setup_logging(debug: bool):
    """Configure application-wide logging based on debug flag.

    If debug mode is enabled, logs are written to a file defined by `DEBUG_PATH`.
    The log format includes timestamps, log level, module, and message.

    Args:
        debug (bool): Whether to enable detailed logging to file.
    """
    handlers = []

    if debug:
        handlers.append(logging.FileHandler(DEBUG_PATH, mode="w"))

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=handlers
        )
# End-of-file (EOF)
