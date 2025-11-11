# Modeled Metrics Monitoring Library

A Python library for monitoring modeled metrics with Google Cloud Monitoring.

## Overview

This library provides a Python interface for working with Google Cloud Monitoring metric descriptors and writing metrics. It queries the Google Cloud Monitoring API to retrieve metric descriptors.

![High level overview](img/modeled-metrics-monitoring-overview.png)

## Key Features

- **Direct API Integration**: Queries Google Cloud Monitoring API for metric descriptors
- **Type Safety**: Uses Google's protobuf `MetricDescriptor` objects
- **Flexible Metric Writing**: Supports all metric value types (BOOL, INT64, DOUBLE, STRING, DISTRIBUTION)
- **Error Handling**: Comprehensive exception handling for Google Cloud API errors

## Usage

### Development

```bash
# Install in development mode
pip install -e .

# Run the example
python -m modeled_metrics_monitoring.run
```

### Building and Distribution

```bash
# Build the package
./build.sh

# Install the built package
pip install dist/*.whl
```

### Using the Library

```python
from modeled_metrics_monitoring import get_metric_descriptor_by_type, write_metric

# Get a metric descriptor by type
descriptor = get_metric_descriptor_by_type(
    "custom.googleapis.com/contextual-data-monitoring/modeled-metrics-ml-ops/vertex_pipeline/foot_traffic/feature_null_ratio"
)

# Write a metric
write_metric(
    descriptor,
    0.1,
    metric_labels={
        "feature_group_id": "temporal",
        "feature_group_revision": "r0_1",
        "feature_id": "is_weekend"
    }
)

# Or write a metric using the type string directly
write_metric(
    "custom.googleapis.com/contextual-data-monitoring/modeled-metrics-ml-ops/vertex_pipeline/foot_traffic/feature_null_ratio",
    0.1,
    metric_labels={
        "feature_group_id": "temporal",
        "feature_group_revision": "r0_1",
        "feature_id": "is_weekend"
    }
)
```

## Configuration

The library can be configured using environment variables. All configuration values are defined in `modeled-metrics-monitoring/src/modeled_metrics_monitoring/config.py`.

### Environment Variables

#### `MONITORING_ENABLED`
- **Description**: Whether to enable monitoring functionality.
- **Type**: Boolean (via environment variable)
- **Default**: `True`
- **Accepted Values**: `'true'`, `'1'`, `'yes'`, `'on'` (case-insensitive). Any other value disables monitoring.
- **Usage**: Set to `False` to disable all monitoring operations without modifying code.

```bash
export MONITORING_ENABLED=False
```

#### `MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION`
- **Description**: Whether to raise an exception when monitoring initialization fails (e.g., when the principal lacks required IAM permissions).
- **Type**: Boolean (via environment variable)
- **Default**: `False`
- **Accepted Values**: `'true'`, `'1'`, `'yes'`, `'on'` (case-insensitive). Any other value disables exception raising.
- **Usage**: Set to `True` to enable strict error handling. When `False`, initialization failures result in warnings and monitoring is disabled gracefully.

```bash
export MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION=True
```

#### `METRIC_WRITER_IAM_ROLE`
- **Description**: The IAM role name required for writing monitoring metrics.
- **Type**: String
- **Default**: `"roles/monitoring.metricWriter"`
- **Usage**: Override if using a custom IAM role for metric writing permissions.

```bash
export METRIC_WRITER_IAM_ROLE=roles/monitoring.metricWriter
```

#### `MONITORING_TARGET_GCP_PROJECT_ID`
- **Description**: The Google Cloud project ID where metric descriptors are stored and where the service account has monitoring permissions.
- **Type**: String
- **Default**: `"uc-contextual-data-monitoring"`
- **Usage**: Set to the target GCP project ID where your metric descriptors are managed.

```bash
export MONITORING_TARGET_GCP_PROJECT_ID=your-project-id
```

### Internal Configuration

#### `METRIC_DESCRIPTOR_TYPE_PREFIX`
- **Description**: The prefix for all metric descriptor types managed by this project.
- **Type**: String
- **Default**: `"custom.googleapis.com/contextual-data-monitoring/"`
- **Warning**: **DO NOT CHANGE THIS VALUE**. Changing this will cause all existing metric descriptors in Google Cloud Monitoring to become unsupported.
- **Note**: This is an internal constant and should not be modified.

## Architecture

- **Terraform**: Uses YAML files from `monitoring-metrics-definitions/metric-descriptors/*.yaml` to create metric descriptors in Google Cloud Monitoring
- **Python Library**: Queries Google Cloud Monitoring API directly to retrieve metric descriptors
- **Separation of Concerns**: Terraform handles infrastructure (creating metric descriptors), Python library handles runtime operations (querying and writing metrics)

This approach ensures that the Python library is always working with the current state of metric descriptors in Google Cloud Monitoring, while Terraform manages the infrastructure definitions.
