
from enum import Enum
import logging
from typing import Optional, TypedDict, List

from slack_bolt import Ack, Complete, Fail

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

def handle_filters_event(
    ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger
):
    # logger.info("Function inputs received:")
    # logger.info(f"inputs: {json.dumps(inputs, indent=2)}")

    try:

        filters: List[SearchFilter] = []

        complete(outputs={"filters": filters})
    except Exception as e:
        logger.exception(f"Error in handle_filters_step_event: {e}")
    finally:
        ack()
