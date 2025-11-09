import tomllib
from pathlib import Path


def get_config(config_file: Path):
    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    return config
