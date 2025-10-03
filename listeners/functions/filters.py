from enum import Enum
import logging
from typing import List, Optional, TypedDict

from slack_bolt import Ack, Complete, Fail

FILTER_PROCESSING_ERROR_MSG = (
    "We encountered an issue processing filter results. Please try again or contact the app owner if the problem persists."
)


class FilterType(Enum):
    MULTI_SELECT = "multi_select"
    TOGGLE = "toggle"


class FilterOptions(TypedDict):
    name: str
    value: str


class SearchFilter(TypedDict):
    name: str
    display_name: str
    filter_type: FilterType
    options: Optional[List[FilterOptions]]


def filters_step_callback(ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger):
    try:
        user_context = inputs.get("user_context", {})
        logger.debug(f"User {user_context.get('id')} executing filter request")

        filters: List[SearchFilter] = [
            {
                "name": "languages",
                "display_name": "Languages",
                "type": FilterType.MULTI_SELECT.value,
                "options": [
                    {"name": "Python", "value": "python"},
                    {"name": "Java", "value": "java"},
                    {"name": "JavaScript", "value": "javascript"},
                    {"name": "TypeScript", "value": "typescript"},
                ],
            },
            {
                "name": "type",
                "display_name": "Type",
                "type": FilterType.MULTI_SELECT.value,
                "options": [
                    {"name": "Template", "value": "template"},
                    {"name": "Sample", "value": "sample"},
                ],
            },
        ]

        complete(outputs={"filters": filters})
    except Exception as e:
        logger.error(f"Unexpected error occurred while processing filter request: {type(e).__name__} - {str(e)}", exc_info=e)
        fail(error=FILTER_PROCESSING_ERROR_MSG)
    finally:
        ack()
