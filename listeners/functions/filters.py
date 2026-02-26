import logging

from slack_bolt import Ack, Complete, Fail

from listeners.filters import LANGUAGES_FILTER, SAMPLES_FILTER, TEMPLATES_FILTER


def filters_step_callback(ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger):
    try:
        user_context = inputs.get("user_context", {})
        logger.debug(f"User {user_context.get('id')} executing filter request")

        complete(outputs={"filters": [LANGUAGES_FILTER, TEMPLATES_FILTER, SAMPLES_FILTER]})
    except Exception as e:
        logger.error(
            f"Unexpected error occurred while processing filter request: {type(e).__name__} - {e}",
            exc_info=e,
        )
        fail(
            error="We encountered an issue processing filter results. "
            "Please try again or contact the app owner if the problem persists."
        )
    finally:
        ack()
