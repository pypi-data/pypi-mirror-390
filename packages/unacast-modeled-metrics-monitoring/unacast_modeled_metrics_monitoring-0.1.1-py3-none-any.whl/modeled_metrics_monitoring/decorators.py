import logging
from functools import wraps

LOGGER = logging.getLogger(__name__)


# Import the monitoring flag from the main module
# Use a function to get the current state to avoid circular imports
def _get_monitoring_enabled():
    """Get the current monitoring enabled state."""
    from . import _MONITORING_ENABLED

    return _MONITORING_ENABLED


def monitoring_enabled(func):
    """
    Decorator that checks if monitoring is enabled before executing the function.
    If monitoring is disabled, logs a message and skips execution.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _get_monitoring_enabled():
            LOGGER.info(f"Monitoring is disabled. Skipping execution of {func.__name__}")
            return None
        return func(*args, **kwargs)

    return wrapper
