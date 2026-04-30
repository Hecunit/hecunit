from email.policy import default
from pathlib import Path

import yaml

from core.exceptions import HecConfigError

YAML_FILENAME = "hecunit.yaml"
USER_CONFIG_DIR = Path.home() / ".hecunit"
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.yaml"


def _find_project_yaml() -> Path:
    """search for a project.yaml file in the current directory and parent directories"""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / YAML_FILENAME
        if candidate.exists():
            return candidate
    return cwd / YAML_FILENAME


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

def _log_yaml_update(path: Path, unit_name: str) -> None:
    import logging
    logging.getLogger("hecunit.config").info(
        f"hecunit.yaml %s at %s - unit '%s' section added", "created", path, unit_name
    )

def _save_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def sync_yaml(unit_name: str, unit_class) -> None:
    """Auto-create or update hecunit.yaml file with unit's defaults"""
    yaml_path = _find_project_yaml()
    existing_yaml = _load_project_yaml(yaml_path)

    changed = False

    if "hecunit" not in existing_yaml:
        existing_yaml["hecunit"] = {
            "log_level": "INFO",
            "api_version": 1,
        }
        changed = True
        
    existing_yaml.setdefault("units", {})
    
    if unit_name not in existing_yaml["units"]:
        defaults = dict(getattr(unit_class, "DEFAULT_CONFIG", {}))
        secrets = getattr(unit_class, "SECRETS", {})

        for secret_key, meta in secrets.items():
            env_var = meta.get("env", secret_key.upper())
            defaults[f"# {secret_key}"] = f"Set via env: {env_var} or override here"

        existing_yaml["units"][unit_name] = defaults
        changed = True

    if changed:
        _save_yaml(yaml_path, existing_yaml)
        _log_yaml_update(yaml_path, unit_name)

def resolve(unit_name: str, overrides: dict | None = None) -> dict:
    """build final config for a unit instance"""
    project_cfg = _load_project_yaml(_find_project_yaml())
    user_cfg = _load_project_yaml(USER_CONFIG_PATH)

    unit_project = project_cfg.get("units", {}).get(unit_name, {})
    unit_user = user_cfg.get("units", {}).get(unit_name, {})

    merged_config = _deep_merge(project_cfg, user_cfg)
    if overrides:
        merged_config = _deep_merge(merged_config, overrides)
    return merged_config