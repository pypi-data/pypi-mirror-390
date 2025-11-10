from typing import Any

import json

from botocore.client import BaseClient


def get_secret_value(client: BaseClient, secret: str) -> dict[str, Any]:
    """
    Function to grab a Secret from AWS Secrets Manager

    Args:
        client (botocore.Client): S3 Secrets Manager Client

        secret (str): The Name of the Secret in Secrets Manager

    Returns:
        The Requested Secret Value
    """
    try:
        secret = json.loads(client.get_secret_value(SecretId=secret)["SecretString"])
        return secret
    except Exception:
        raise
