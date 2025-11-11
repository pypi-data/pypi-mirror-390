import os

# Whether to enable monitoring.
# Set to False via environment variable to disable monitoring.
# Accepts truthy values: 'true', '1', 'yes', 'on' (case-insensitive).
# Default: True
MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "True").lower() in ("true", "1", "yes", "on")

# Whether to raise an exception when monitoring initialization fails.
# Set to True via environment variable to enable strict error handling.
# Accepts truthy values: 'true', '1', 'yes', 'on' (case-insensitive).
# Default: False
MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION = os.getenv(
    "MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION", "False"
).lower() in ("true", "1", "yes", "on")

# IAM role name for metric writing permissions.
# Used to grant the service account permission to write monitoring metrics.
# Default: "roles/monitoring.metricWriter"
METRIC_WRITER_IAM_ROLE = os.getenv("METRIC_WRITER_IAM_ROLE", "roles/monitoring.metricWriter")

# Google Cloud project ID where the metric writer IAM role is defined.
# This project contains the service account with monitoring permissions.
# Default: "uc-contextual-data-monitoring"
MONITORING_TARGET_GCP_PROJECT_ID = os.getenv(
    "MONITORING_TARGET_GCP_PROJECT_ID", "uc-contextual-data-monitoring"
)

# This is the prefix of the metric descriptor type that is managed by this project.
# DO NOT CHANGE THIS VALUE.
# If the value is changed, all the metric descriptors in GCM will become unsupported.
METRIC_DESCRIPTOR_TYPE_PREFIX = "custom.googleapis.com/contextual-data-monitoring/"
