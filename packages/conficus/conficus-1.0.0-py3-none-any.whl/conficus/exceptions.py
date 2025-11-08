class CoercionError(ValueError):
    """Raised when type coercion fails"""

    pass


class InheritanceError(ValueError):
    """Raised when inheritance configuration is invalid"""

    pass


class ConfigError(Exception):
    """Base exception for configuration errors"""

    pass
