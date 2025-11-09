from pathlib import Path

import pytest

from firefly_reports.config import get_config


def test_get_config():
    config = get_config(Path.cwd() / "example_config.toml")

    assert config["email"]["user"] == "your_email_address@gmail.com"
    assert config["firefly"]["url"] == "http://firefly_instance:8085"
