import json
import logging
import requests

logger = logging.getLogger(__name__)


def write_to_slack(message: str, webhook_url: str) -> None:
    """
    Sends a message to Slack using the provided webhook URL.

    Args:
        message (str): The message to send.

        webhook_url (str): Slack webhook URL to send the message to.

    Returns:
        None
    """
    try:
        response = requests.post(
            url=webhook_url,
            data=json.dumps({"text": message}),
            headers={"Content-Type": "application/json"},
        )
        if not response.ok:
            logger.error(
                f"Write to Slack failed: {response.status_code} - {response.text}"
            )
            response.raise_for_status()
    except Exception as e:
        logger.exception(f"Error sending message to Slack: {e}")
        raise
