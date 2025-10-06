import json
import logging

from slack_sdk import WebClient


class SlackResponseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.name = "SlackResponseError"


def fetch_sample_data(client: WebClient, query: str = None, filters: dict = None, logger: logging.Logger = None):
    method = "developer.sampleData.get"
    params = {}
    if query:
        params["query"] = query
    if filters:
        params["filters"] = json.dumps(filters)

    response = client.api_call(method, params=params)

    if not response.get("ok", False):
        logger.error(f"Search API request failed with error: {response.get('error', 'no error found')}")
        raise SlackResponseError(f"Failed to fetch sample data from Slack API: ok=false for method={method}")

    if "samples" not in response:
        logger.error(f"Failed to parse API response as sample data. Received: {json.dumps(response)}")
        raise SlackResponseError(f"Invalid response format from Slack API from {method}")

    return response
