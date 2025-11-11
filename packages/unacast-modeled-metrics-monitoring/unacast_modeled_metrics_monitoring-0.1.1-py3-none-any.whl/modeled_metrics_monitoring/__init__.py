import logging

from .config import MONITORING_ENABLED
from .metric_descriptor import (
    get_available_metric_descriptors,
    get_metric_descriptor_by_type,
)
from .metric_writer import write_metric
from .utils import can_write_metrics

__version__ = "0.1.0"
__all__ = [
    "get_available_metric_descriptors",
    "get_metric_descriptor_by_type",
    "write_metric",
]

LOGGER = logging.getLogger(__name__)

_MONITORING_ENABLED = MONITORING_ENABLED and can_write_metrics()
