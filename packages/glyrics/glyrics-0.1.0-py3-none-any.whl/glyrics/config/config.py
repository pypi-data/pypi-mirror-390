from importlib import resources
from typing import Any, Optional
import json


CONFIG = json.loads(resources.read_text('glyrics.config', 'config.json'))


def get(key: str, default: Optional[Any] = None) -> Any:
    if not key:
        raise KeyError(f'Invalid key: {key!r}')
    config = CONFIG
    path = key.split('.')
    for path_key in path[:-1]:
        config = config.get(path_key, {})
    return config.get(path[-1], default)

