from typing import Type

from core.base import HecUnit
from core.config import sync_yaml
from core.registry import lookup


def hec(cls, unit: str, *, config: str) -> HecUnit:
    """instantiate and return a HecUnit subclass"""
    unit_name, _ , alias = unit.partition(":")
    instance_name = alias or unit_name

    unit_class: Type[HecUnit] = lookup(unit_name)

    sync_yaml(unit_name, unit_class)

