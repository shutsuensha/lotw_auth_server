import logging.config
from pathlib import Path

import yaml


def setup_logging(config_path: str = "logging-config.yaml") -> None:
    config_file = Path(config_path)
    if config_file.exists():
        with config_file.open("r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)
