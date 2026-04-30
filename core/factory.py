from typing import Type

from core.base import HecUnit
from core.config import sync_yaml, resolve
from core.exceptions import HecSetupError
from core.registry import lookup


async def hec(cls, unit: str, *, config: dict | None = None) -> HecUnit:
    """instantiate and return a HecUnit subclass"""
    unit_name, _ , alias = unit.partition(":")
    instance_name = alias or unit_name

    unit_class: Type[HecUnit] = lookup(unit_name)

    sync_yaml(unit_name, unit_class)

    merged_config = resolve(unit_name, overrides=config)

    instance: HecUnit = unit_class(instance_name, merged_config)

    try:
        await instance.setup()
    except Exception as e:
        raise HecSetupError(
            f"Unit '{unit}' failed during _setup(): {e}"
        ) from e

    instance._ready = True
    instance.log(f"ready (v{instance.UNIT_VERSION}, api_version={instance.UNIT_API_VERSION})")
    return instance

