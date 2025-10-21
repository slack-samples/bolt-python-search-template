import logging
from dataclasses import asdict

from slack_bolt import Ack, Complete, Fail

from listeners.filters import LANGUAGES_FILTER, SAMPLES_FILTER, TEMPLATES_FILTER

FILTER_PROCESSING_ERROR_MSG = (
    "We encountered an issue processing filter results. Please try again or contact the app owner if the problem persists."
)

filter_none = lambda items: {k: v for k, v in items if v is not None}

def filters_step_callback(ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger):
    try:
        user_context = inputs.get("user_context", {})
        logger.debug(f"User {user_context.get('id')} executing filter request")

        complete(
            outputs={
                "filters": [
                    asdict(LANGUAGES_FILTER, dict_factory=filter_none),
                    asdict(TEMPLATES_FILTER, dict_factory=filter_none),
                    asdict(SAMPLES_FILTER, dict_factory=filter_none),
                ]
            }
        )
    except Exception as e:
        logger.error(
            f"Unexpected error occurred while processing filter request: {type(e).__name__} - {str(e)}",
            exc_info=e,
        )
        fail(error=FILTER_PROCESSING_ERROR_MSG)
    finally:
        ack()
