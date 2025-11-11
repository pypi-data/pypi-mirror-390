import logging
import subprocess

import google.auth
from google.api_core import exceptions
from google.auth.transport import requests
from google.cloud import resourcemanager_v3
from google.iam.v1 import iam_policy_pb2  # type: ignore

from .config import (
    METRIC_WRITER_IAM_ROLE,
    MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION,
    MONITORING_TARGET_GCP_PROJECT_ID,
)

LOGGER = logging.getLogger(__name__)


def get_principal_email() -> str | None:
    """
    Get the email of the principal running the code.

    Returns:
        The email of the principal running the code, or None if it cannot be determined.
    """
    try:
        # First try to get credentials from Google Auth
        credentials, _ = google.auth.default()
        credentials.refresh(requests.Request())

        # Check for service account email
        if hasattr(credentials, "service_account_email") and credentials.service_account_email:
            return credentials.service_account_email

        # Check for user account email in ID token
        if (
            hasattr(credentials, "id_token")
            and credentials.id_token
            and "email" in credentials.id_token
        ):
            return credentials.id_token["email"]

        # Check for user account email in token info
        if hasattr(credentials, "token") and credentials.token:
            try:
                # Try to get user info from the token
                import requests as http_requests

                response = http_requests.get(
                    f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={credentials.token}"  # noqa: E501
                )
                if response.status_code == 200:
                    user_info = response.json()
                    if "email" in user_info:
                        return user_info["email"]
            except Exception:
                pass

    except Exception:
        pass

    # Fallback: try to get email from gcloud config
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "account"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: try to get email from gcloud auth list
    try:
        result = subprocess.run(
            [
                "gcloud",
                "auth",
                "list",
                "--filter=status:ACTIVE",
                "--format=value(account)",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None


def principal_has_role(project_id: str, role: str) -> bool:
    """
    Checks if the active principal has a specific IAM role on a target project.

    Args:
        project_id: The ID of the GCP project to check.
        role: The full name of the IAM role (e.g., 'roles/storage.admin').

    Returns:
        True if the principal has the role, False otherwise.
    """
    principal_email = get_principal_email()
    if not principal_email:
        LOGGER.warning("Could not identify the principal running the code.")
        return False

    LOGGER.info(f"Checking if '{principal_email}' has role '{role}' on project '{project_id}'...")

    try:
        # Determine the member type prefix (user: or serviceAccount:)
        if principal_email.endswith(".gserviceaccount.com"):
            member = f"serviceAccount:{principal_email}"
        else:
            member = f"user:{principal_email}"

        client = resourcemanager_v3.ProjectsClient()
        request = iam_policy_pb2.GetIamPolicyRequest(resource=f"projects/{project_id}")
        policy = client.get_iam_policy(request=request)

        # Check each role binding in the policy
        for binding in policy.bindings:
            if binding.role == role:
                if member in binding.members:
                    return True

        return False

    except exceptions.PermissionDenied:
        LOGGER.warning(
            f"Permission Denied: The principal '{principal_email}' lacks the "
            f"'resourcemanager.projects.getIamPolicy' permission on project '{project_id}'."
        )
        return False
    except Exception as e:
        LOGGER.warning(f"An unexpected error occurred: {e}")
        return False


def can_write_metrics():
    """
    Check if the user has write access to the Google Cloud Monitoring API.
    """
    if not principal_has_role(
        project_id=MONITORING_TARGET_GCP_PROJECT_ID, role=METRIC_WRITER_IAM_ROLE
    ):
        if MONITORING_INIT_FAIL_SHOULD_RAISE_EXCEPTION:
            raise ValueError("User does not have write access to the Google Cloud Monitoring API")
        else:
            LOGGER.warning(
                "User does not have write access to the Google Cloud Monitoring API. "
                "Monitoring will be disabled."
            )
            return False

    LOGGER.info(
        "User has write access to the Google Cloud Monitoring API. Monitoring will be enabled."
    )
    return True
