import logging
from typing import List

from google.api.metric_pb2 import MetricDescriptor  # type: ignore
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3.types import (
    GetMetricDescriptorRequest,
    ListMetricDescriptorsRequest,
)
from google.api_core.exceptions import (
    NotFound,
    PermissionDenied,
    InvalidArgument,
    GoogleAPIError,
)

from .config import METRIC_DESCRIPTOR_TYPE_PREFIX, MONITORING_TARGET_GCP_PROJECT_ID
from .decorators import monitoring_enabled

LOGGER = logging.getLogger(__name__)


@monitoring_enabled
def get_available_metric_descriptors() -> List[MetricDescriptor]:
    """
    Retrieve all active custom metric descriptors from Google Cloud Monitoring.

    Returns:
        List[MetricDescriptor]: List of custom metric descriptors that are currently active.

    Raises:
        Exception: If there's an error accessing the Google Cloud Monitoring API.
    """
    try:
        # Initialize the monitoring client
        client = monitoring_v3.MetricServiceClient()

        # Construct the project path
        project_name = f"projects/{MONITORING_TARGET_GCP_PROJECT_ID}"

        LOGGER.info(f"Fetching metric descriptors from project: {MONITORING_TARGET_GCP_PROJECT_ID}")

        request = ListMetricDescriptorsRequest(
            name=project_name,
            filter=rf'metric.type = starts_with("{METRIC_DESCRIPTOR_TYPE_PREFIX}")',
        )

        # List all metric descriptors for the project
        metric_descriptors_pager = client.list_metric_descriptors(request=request)

        # Convert pager to list
        metric_descriptors = list(metric_descriptors_pager)

        LOGGER.info(f"Found {len(metric_descriptors)} custom metric descriptors")
        return metric_descriptors

    except Exception as e:
        LOGGER.error(f"Error fetching metric descriptors: {str(e)}")
        raise


@monitoring_enabled
def get_metric_descriptor_by_type(metric_type: str) -> MetricDescriptor:
    """
    Get a metric descriptor by its type (e.g., 'custom.googleapis.com/...').

    Args:
        metric_type: The metric type (e.g., 'custom.googleapis.com/contextual-data-monitoring/...')

    Returns:
        MetricDescriptor: The metric descriptor
    """
    try:
        client = monitoring_v3.MetricServiceClient()
        request = GetMetricDescriptorRequest(
            name=f"projects/{MONITORING_TARGET_GCP_PROJECT_ID}/metricDescriptors/{metric_type}"
        )
        return client.get_metric_descriptor(request=request)
    except NotFound:
        LOGGER.error(f"Metric descriptor not found: {metric_type}")
        raise
    except PermissionDenied as e:
        LOGGER.error(f"Permission denied when fetching metric descriptor: {str(e)}")
        raise
    except InvalidArgument as e:
        LOGGER.error(f"Invalid argument when fetching metric descriptor: {str(e)}")
        raise
    except GoogleAPIError as e:
        LOGGER.error(f"Google API error when fetching metric descriptor: {str(e)}")
        raise
    except Exception as e:
        LOGGER.error(f"Unexpected error fetching metric descriptor: {str(e)}")
        raise
