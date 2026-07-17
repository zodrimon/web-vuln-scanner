
_SCANNERS: list[type] = []


def register_scanner(cls: type) -> type:
    """Decorator to register a scanner class."""
    _SCANNERS.append(cls)
    return cls


def get_registered_scanners() -> list[type]:
    """Return all registered scanner classes."""
    return list(_SCANNERS)
