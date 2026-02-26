import logging

from slack_bolt import Ack, Complete, Fail
from slack_sdk import WebClient

from listeners.sample_data_service import SlackResponseError, fetch_sample_data


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

        complete(outputs={"search_results": samples})
    except SlackResponseError as e:
        logger.error(f"Failed to fetch or parse sample data. Error details: {e}", exc_info=e)
        fail(
            error="We encountered an issue processing your search results. "
            "Please try again or contact the app owner if the problem persists."
        )
    except Exception as e:
        logger.error(f"Unexpected error processing search request: {type(e).__name__} - {e}", exc_info=e)
    finally:
        ack()
