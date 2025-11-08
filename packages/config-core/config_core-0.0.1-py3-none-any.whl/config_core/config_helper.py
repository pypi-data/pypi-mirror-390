import logging
import os
import re
from typing import Callable, Dict, Type, TypeVar

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel


def _apply_to_keys(dictionary: Dict, function_to_run: Callable) -> Dict:
    """Apply function on all the keys in a dict.

    Args:
        dictionary (Dict): Dict to change.
        function_to_run (Callable): Function to apply over the keys.
    """

    def _recurse(obj):
        """Recursive function to loop over a dict."""

        if isinstance(obj, dict):
            return {function_to_run(k): _recurse(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return type(obj)(_recurse(i) for i in obj)
        elif isinstance(obj, set):
            return {_recurse(i) for i in obj}
        return obj

    return _recurse(dictionary)


def _get_case_insensitive_key(dictionary: Dict, key: str, func: Callable) -> str:
    """Get a key from a dict in a case insensitive way."""
    for k in dictionary.keys():
        if k.lower() == key.lower():
            return dictionary[k]
    return func(key)


def _to_snake_case(name: str) -> str:
    """String to snake case.

    Args:
        name (str): String to parse.

    Returns:
        str: String in snake case.
    """

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


T = TypeVar("T", bound=BaseModel)


def load_config(path: str, key_replacements: Dict, ConfigModel: Type[T]) -> Type[T]:
    """Load config.

    Args:
        path (str): Path to config file.
        key_replacements (dict): Dict to replace keys.
        ConfigModel (Type[T]): BaseModel class to cast config with.

    Returns:
        Type[T]: Parsed config.
    """

    try:
        load_dotenv()
        # Load config and substitute env variables and load to yaml
        with open(path, "r") as f:
            formatted = f.read().format_map(os.environ)
            data = yaml.safe_load(formatted)

        transformed_data = _apply_to_keys(
            data,
            lambda name: _get_case_insensitive_key(
                key_replacements, name, _to_snake_case
            ),
        )
        # Parse yaml file.
        config: ConfigModel = ConfigModel.model_validate(transformed_data)

        return config
    except Exception as e:
        logging.error("Failed to load YAML config: " + str(e))
        raise e
