# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause


from pathlib import Path
from typing import Any

import yaml

from .model import Config


def read_config(file_path: Path) -> Config:
    """Reads in the yaml configuration file from the given path and parse it into Config
    object ensuring the validity of the configuration file.

    Args:
        file_path: File of the yaml configuration to parse

    Returns:
        parsed Config object

    Raises:
        :class:`pydantic.ValidationError`: If the configuration cannot be validated.
    """
    config_data = _read_config_yml(file_path)
    config = Config(**config_data)
    return config


# ------------------------------------------------------------------------------------ #
#                                       Internal                                       #
# ------------------------------------------------------------------------------------ #


def _read_config_yml(file_path: Path) -> Any:
    with open(str(file_path)) as config_file:
        return yaml.safe_load(config_file)
