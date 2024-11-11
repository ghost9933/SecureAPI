# logging_config.py

import logging

def setup_logging():
    logging.basicConfig(
        filename='audit.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_action(action: str, detail: str):
    logging.info(f"{action}: {detail}")
