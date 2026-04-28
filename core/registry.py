from importlib.metadata import entry_points
from typing import Type

from core.base import HecUnit, HECUNIT_API_VERSION
from core.exceptions import HecUnitNotFound, HecVersionError



ENTRY_POINT_GROUP = "hecunit.units"

    
def lookup(unit_name) -> Type[HecUnit]:
    """
    Discover and return a registered HecUnit subclass

    Units register via pyproject.toml entry_points:
        [project.entry-points."hecunit.units"]
        gdrive = "hecunit_gdrive:GDriveUnit"
    """
    eps = entry_points(group=ENTRY_POINT_GROUP)

    for ep in eps:
        if ep.name == unit_name:
            unit_class: Type[HecUnit] = ep.load()
            _check_version(unit_name, unit_class)
            return unit_class

    available = [ep.name for ep in eps]
    hint = (
        f"Available: {', '.join(available)}" if available
        else "No units installed. Try: pip install hecunit-<name>"
    )
    raise HecUnitNotFound(
        f"Unit '{unit_name}' not found."
        f"Install with: pip install hecunit-<name>\n{hint}"
)


def list_units(cls) -> dict[str, Type[HecUnit]]:
    """Return all registered units as a dict of {name: class}"""
    eps = entry_points(group=ENTRY_POINT_GROUP)
    result = {}
    for ep in eps:
        try:
            unit_class = ep.load()
            _check_version(ep.name, unit_class)
            result[ep.name] = unit_class
        except (HecVersionError, Exception) as e:
            print(f"Warning: Skipping unit '{ep.name}': {e}")
    return result


def _check_version(unit_name: str, unit_class: Type) -> None:
    unit_api_version = getattr(unit_class, "UNIT_API_VERSION", None)

    if unit_api_version is None:
        raise HecVersionError(
            f"Unit '{unit_name}' ({unit_class.__module__}) does not specify UNIT_API_VERSION.\n"
            f"UNIT_API_VERSION is required to ensure compatibility with the current Hecunit framework."
        )

    if unit_api_version != HECUNIT_API_VERSION:
        raise HecVersionError(
            f"Unit '{unit_name}' ({unit_class.__module__}) has incompatible UNIT_API_VERSION {unit_api_version}.\n"
            f"Expected: {HECUNIT_API_VERSION}. Please update the unit or use a compatible version of Hecunit."
        )


