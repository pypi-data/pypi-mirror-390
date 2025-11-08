from .OmnissiahPrayer import prayer

__version__ = "1.0.1"
__all__ = ["prayer", "pray"]

def pray(*args, **kwargs):
    """Convenience function: directly invokes the prayer."""
    return prayer(*args, **kwargs).pray()