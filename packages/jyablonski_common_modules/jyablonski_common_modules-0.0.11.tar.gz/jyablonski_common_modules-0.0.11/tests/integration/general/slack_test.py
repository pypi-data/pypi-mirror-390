import requests
import requests_mock
import pytest

from jyablonski_common_modules.general import write_to_slack  # adjust import path


def test_write_to_slack_success():
    webhook_url = "https://hooks.slack.com/services/T000/B000/XXX"
    message = "Hello, Slack!"

    with requests_mock.Mocker() as m:
        m.post(webhook_url, status_code=200)

        write_to_slack(message, webhook_url)

        assert m.called
        assert m.call_count == 1
        assert m.last_request.json() == {"text": message}


def test_write_to_slack_failure():
    webhook_url = "https://hooks.slack.com/services/T000/B000/XXX"
    message = "Slack is down"

    with requests_mock.Mocker() as m:
        m.post(webhook_url, status_code=500, text="Internal Server Error")

        with pytest.raises(requests.exceptions.HTTPError):
            write_to_slack(message, webhook_url)
