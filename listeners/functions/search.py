import logging
from typing import List, NotRequired, Optional, TypedDict

from slack_bolt import Ack, Complete, Fail
from slack_sdk import WebClient

from listeners.sample_data_service import SlackResponseError, fetch_sample_data

SEARCH_PROCESSING_ERROR_MSG = (
    "We encountered an issue processing your search results. "
    "Please try again or contact the app owner if the problem persists."
)


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


def search_step_callback(
    ack: Ack,
    inputs: dict,
    fail: Fail,
    complete: Complete,
    client: WebClient,
    logger: logging.Logger,
):
    try:
        query = inputs.get("query")
        filters = inputs.get("filters")

        response = fetch_sample_data(client=client, query=query, filters=filters, logger=logger)

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
    except Exception as e:
        if isinstance(e, SlackResponseError):
            logger.error(f"Failed to fetch or parse sample data. Error details: {str(e)}", exc_info=e)
            fail(error=SEARCH_PROCESSING_ERROR_MSG)
        else:
            logger.error(
                f"Unexpected error occurred while processing search request: {type(e).__name__} - {str(e)}",
                exc_info=e,
            )
    finally:
        ack()
