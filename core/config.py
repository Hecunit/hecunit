from pathlib import Path

import yaml

from core.exceptions import HecConfigError


YAML_FILENAME = "hecunit.yaml"

def _find_project_yaml(cls) -> Path:
    """search for a project.yaml file in the current directory and parent directories"""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / cls.YAML_FILENAME
        if candidate.exists():
            return candidate
    return cwd / cls.YAML_FILENAME

def _load_project_yaml(path: Path) -> dict:
    """load the hecunit.yaml file and return its contents as a dict"""
    if not path.exists():
        return {}

    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise HecConfigError(f"failed to parse {path}: {e}")

def _deep_merge(base: dict, override: dict) -> dict:
    """recursively merge two dictionaries, with values from override taking precedence"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def sync_yaml(unit_name: str, unit_class) -> None:
    """Auto-create or update hecunit.yaml file with unit's defaults"""
    yaml_path = _find_project_yaml()
    existing_config = _load_project_yaml(yaml_path)

    changed = False