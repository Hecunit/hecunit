class HecUnitError(Exception):
    """Base exception for all HecUnit errors."""


class HecUnitNotFound(HecUnitError):
    """Raised when a requested unit is not installed."""


class HecConfigError(HecUnitError):
    """Raised when config loading or validation fails."""


class HecVersionError(HecUnitError):
    """Raised when a unit's API version is incompatible with core."""


class HecSetupError(HecUnitError):
    """Raised when unit._setup() fails."""


class HecOperationError(HecUnitError):
    """Raised when a unit operation fails at runtime."""