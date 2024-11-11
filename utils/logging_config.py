# utils/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
import os
import json
from pythonjsonlogger import jsonlogger  # Install python-json-logger

def setup_logging(log_file: str = "logs/app.log"):
    """
    Configures logging for the application with JSON formatting.
    
    Args:
        log_file (str): Path to the log file.
    """
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create a custom logger
    logger = logging.getLogger("secureapi")
    logger.setLevel(logging.INFO)  # Set the minimum log level

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)  # 5MB per file, keep 5 backups

    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create JSON formatter
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    json_format = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    c_handler.setFormatter(json_format)
    f_handler.setFormatter(json_format)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    # Optionally, prevent log messages from being propagated to the root logger
    logger.propagate = False

    return logger
