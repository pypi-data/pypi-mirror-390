import logging
from typing import cast
from datetime import datetime
from datetime import timezone

from google.cloud import monitoring_v3

from .config import MONITORING_TARGET_GCP_PROJECT_ID
from .decorators import monitoring_enabled
from .metric_descriptor import MetricDescriptor, get_metric_descriptor_by_type

LOGGER = logging.getLogger(__name__)


@monitoring_enabled
def write_metric(
    metric_descriptor: MetricDescriptor | str,
    metric_value: bool | int | float | str | dict,
    metric_labels: dict | None = None,
    resource_attributes: dict | None = None,
):
    """
    Write a metric to Google Cloud Monitoring.

    Args:
        metric_descriptor: The metric descriptor to write. Can be a MetricDescriptor object or a
            string (type of the metric descriptor).
        metric_value: The value of the metric.
        metric_labels: The labels of the metric.
        resource_attributes: The attributes of the resource.
    """
    if isinstance(metric_descriptor, str):
        metric_descriptor = get_metric_descriptor_by_type(metric_descriptor)  # type: ignore

    # Shut up linter with this
    assert isinstance(metric_descriptor, MetricDescriptor)

    time_series = monitoring_v3.TimeSeries()

    # Set metric type
    time_series.metric.type = metric_descriptor.type

    # Set metric labels
    metric_labels = metric_labels or {}
    for label in metric_descriptor.labels:
        key = label.key
        if key in metric_labels:
            time_series.metric.labels[key] = metric_labels[key]
        else:
            raise ValueError(f"Label '{key}' must be provided in 'metric_labels'")

    # Set resource attributes
    if resource_attributes is not None:
        if "type" in resource_attributes and resource_attributes["type"] != "global":
            raise ValueError("Resource type must be 'global'")

        for key, value in resource_attributes.items():
            time_series.resource.labels[key] = value

    # For now, we only support global resources
    time_series.resource.type = "global"

    # Set metric value
    point = monitoring_v3.Point()

    if metric_descriptor.value_type == metric_descriptor.ValueType.BOOL:
        if type(metric_value) is not bool:
            raise ValueError("Metric value type must be BOOL")
        point.value.bool_value = metric_value
    elif metric_descriptor.value_type == metric_descriptor.ValueType.INT64:
        if type(metric_value) is not int:
            raise ValueError("Metric value type must be INT64")
        point.value.int64_value = metric_value
    elif metric_descriptor.value_type == metric_descriptor.ValueType.DOUBLE:
        if type(metric_value) not in (int, float):
            raise ValueError("Metric value type must be DOUBLE")
        point.value.double_value = float(cast(int | float, metric_value))
    elif metric_descriptor.value_type == metric_descriptor.ValueType.STRING:
        if type(metric_value) is not str:
            raise ValueError("Metric value type must be STRING")
        point.value.string_value = metric_value
    elif metric_descriptor.value_type == metric_descriptor.ValueType.DISTRIBUTION:
        if type(metric_value) is not dict:
            raise ValueError("Metric value type must be DISTRIBUTION")
        point.value.distribution_value = metric_value
    else:
        raise ValueError(f"Unsupported metric value type: {metric_descriptor.value_type}")

    # Set metric interval
    point.interval.end_time = datetime.now(timezone.utc)

    # Set metric points
    time_series.points = [point]

    # Push metric to Google Cloud Monitoring
    client = monitoring_v3.MetricServiceClient()
    client.create_time_series(
        name=f"projects/{MONITORING_TARGET_GCP_PROJECT_ID}", time_series=[time_series]
    )

    LOGGER.info(f"Metric '{metric_descriptor.name}' pushed successfully. Value: '{metric_value}'")
