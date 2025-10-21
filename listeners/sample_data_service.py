import json
import logging

from slack_sdk import WebClient

from listeners.filters import LANGUAGES_FILTER, SAMPLES_FILTER, TEMPLATES_FILTER

API_METHOD = "developer.sampleData.get"


class SlackResponseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.name = "SlackResponseError"


def fetch_sample_data(client: WebClient, query: str = None, filters: dict = None, logger: logging.Logger = None):
    params = {"query": query}

    if filters:
        selected_filters = {}

        languages = filters.get(LANGUAGES_FILTER.name, [])
        templates = filters.get(TEMPLATES_FILTER.name, False)
        samples = filters.get(SAMPLES_FILTER.name, False)

        if languages:
            selected_filters[LANGUAGES_FILTER.name] = languages

        if templates ^ samples:
            if templates:
                selected_filters["type"] = TEMPLATES_FILTER.name
            elif samples:
                selected_filters["type"] = SAMPLES_FILTER.name

        if selected_filters:
            params["filters"] = selected_filters

    response = client.api_call(API_METHOD, params=params)

    if not response.get("ok", False):
        logger.error(f"Search API request failed with error: {response.get('error', 'no error found')}")
        raise SlackResponseError(f"Failed to fetch sample data from Slack API: ok=false for method={API_METHOD}")

    return response
