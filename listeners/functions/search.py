import logging
from ast import List
from typing import NotRequired, Optional, TypedDict

from slack_bolt import Ack, Complete, Fail
from slack_sdk import WebClient

from listeners.sample_data_fetcher import SlackResponseError, fetch_sample_data

SEARCH_PROCESSING_ERROR_MSG = (
    "We encountered an issue processing your search results. "
    "Please try again or contact the app owner if the problem persists."
)

print(SEARCH_PROCESSING_ERROR_MSG)


class EntityReference(TypedDict):
    id: str
    type: Optional[str]


class SearchResult(TypedDict):
    title: str
    description: str
    link: str
    date_updated: str
    external_ref: EntityReference
    content: NotRequired[str]


def search_step_callback(ack: Ack, inputs: dict, fail: Fail, complete: Complete, client: WebClient, logger: logging.Logger):
    try:
        query = inputs.get("query")
        filters = inputs.get("filters", {})
        languages_filter = filters.get("languages", [])
        type_filter = filters.get("type", [])

        filters_payload = {}
        if languages_filter:
            filters_payload["languages"] = languages_filter
        if type_filter:
            if len(type_filter) == 1:
                filters_payload["type"] = type_filter[0]

        response = fetch_sample_data(client=client, query=query, filters=filters_payload, logger=logger)

        samples = response.get("samples", [])

        results: List[SearchResult] = [
            {
                "title": sample["title"],
                "description": sample["description"],
                "link": sample["link"],
                "date_updated": sample["date_updated"],
                "external_ref": sample["external_ref"],
                **({"content": sample["content"]} if "content" in sample else {}),
            }
            for sample in samples
        ]

        complete(outputs={"search_result": results})
    except SlackResponseError as e:
        logger.error(f"Failed to fetch or parse sample data. Error details: {str(e)}", exc_info=e)
        fail(error=SEARCH_PROCESSING_ERROR_MSG)
    except Exception as e:
        logger.error(f"Unexpected error occurred while processing search request: {type(e).__name__} - {str(e)}", exc_info=e)
        fail(error=SEARCH_PROCESSING_ERROR_MSG)
    finally:
        ack()
