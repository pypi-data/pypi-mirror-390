import glob
import os
from typing import Annotated, Dict, List, Set

import pytest
from pydantic import AfterValidator, BaseModel, ValidationError

from config_core import load_config

__author__ = "jarneamerlinck-do"
__copyright__ = "jarneamerlinck-do"
__license__ = "Proprietary"

current_file = os.path.abspath(__file__)
current_folder = os.path.dirname(current_file)
config_root = f"{current_folder}/configs/nesting_service"


def get_config_files_in_folder(path: str) -> List[str]:
    return glob.glob(os.path.join(path, "*.yaml")) + glob.glob(
        os.path.join(path, "*.yml")
    )


# Config Example
DEFAULT_NODE_NAME: str = "NestingService"

key_replacement: Dict = {DEFAULT_NODE_NAME: "node_config"}


def is_even(value: int) -> int:
    """Validate if int is even."""
    if value % 2 == 1:
        raise ValueError(f"{value} is not an even number")
    return value


class NestingConfig(BaseModel):
    """Main config for node."""

    int_even_set: Set[Annotated[int, AfterValidator(is_even)]] = []
    example_boolean: bool = False


class ConfigFile(BaseModel):
    """Top config level."""

    # Required top-level field: parsing should fail if missing
    service_id: int

    node_config: NestingConfig


# End config example


def validate_config(config: ConfigFile):
    assert isinstance(config, ConfigFile)
    assert isinstance(config.service_id, int)
    assert isinstance(config.node_config, NestingConfig)
    assert isinstance(config.node_config.int_even_set, Set)


VALID_CONFIGS: List[str] = get_config_files_in_folder(f"{config_root}/valid")
ENV_ENABLED_CONFIGS: List[str] = get_config_files_in_folder(f"{config_root}/valid/env")
CHANGED_NODE_NAME_CONFIGS: List[str] = get_config_files_in_folder(
    f"{config_root}/valid/node_name"
)

EMPTY_CONFIGS: List[str] = [f"{config_root}/empty.yaml"]
INVALID_CONFIGS: List[str] = get_config_files_in_folder(f"{config_root}/invalid")


@pytest.mark.parametrize("config_path", VALID_CONFIGS)
def test_load_valid_configs(config_path: str):
    """Load valid configs"""
    config = load_config(config_path, key_replacement, ConfigFile)
    validate_config(config)


@pytest.mark.parametrize("config_path", ENV_ENABLED_CONFIGS)
def test_load_env_configs(config_path: str):
    """Load valid env configs"""

    os.environ["STRING_FROM_ENV"] = "service"
    os.environ["FLOAT_FROM_ENV"] = "3.141592"
    os.environ["KEY_FROM_ENV"] = "example"

    config = load_config(config_path, key_replacement, ConfigFile)
    validate_config(config)

    os.environ.pop("STRING_FROM_ENV", None)
    os.environ.pop("FLOAT_FROM_ENV", None)
    os.environ.pop("KEY_FROM_ENV", None)


@pytest.mark.parametrize("config_path", CHANGED_NODE_NAME_CONFIGS)
def test_load_node_name_configs(config_path: str):
    """Load valid env configs"""

    os.environ["NODE_NAME"] = "new_node_name"
    os.environ["STRING_FROM_ENV"] = "service"
    os.environ["FLOAT_FROM_ENV"] = "3.141592"
    os.environ["KEY_FROM_ENV"] = "example"

    config = load_config(
        config_path, {os.environ["NODE_NAME"]: "node_config"}, ConfigFile
    )
    validate_config(config)

    os.environ.pop("NODE_NAME", None)
    os.environ.pop("STRING_FROM_ENV", None)
    os.environ.pop("FLOAT_FROM_ENV", None)
    os.environ.pop("KEY_FROM_ENV", None)


@pytest.mark.parametrize("config_path", EMPTY_CONFIGS)
def test_load_empty_configs(config_path: str):
    """Load valid env configs"""

    with pytest.raises(ValidationError):
        load_config(config_path, key_replacement, ConfigFile)


@pytest.mark.parametrize("config_path", INVALID_CONFIGS)
def test_load_invalid_configs(config_path: str):
    """Load valid env configs"""

    with pytest.raises(Exception):
        load_config(config_path, key_replacement, ConfigFile)
