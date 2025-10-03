import json
import logging
import os
from enum import Enum
from typing import TypedDict, List, Optional, NotRequired

from slack_bolt import Ack, App, Complete, Fail
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

logging.basicConfig(level=logging.INFO)

#----------------------
# MODELS
#----------------------

class FilterType(Enum):
    MULTI_SELECT = "multi_select"
    TOGGLE = "toggle"

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


class FilterOptions(TypedDict):
    name: str
    value: str


class SearchFilter(TypedDict):
    name: str
    display_name: str
    filter_type: FilterType
    options: Optional[List[FilterOptions]]


client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"), base_url="https://slack.com/api/")
app = App(client=client)


@app.function("search", auto_acknowledge=False)
def handle_search_step_event(
    ack: Ack, inputs: dict, body: dict, fail: Fail, complete: Complete, logger: logging.Logger
):

    try:
        query = inputs.get("query")
        languages_filter = inputs.get("filters", {}).get("languages", [])
        type_filter = inputs.get("filters", {}).get("type", [])

        filters_payload = {}
        if languages_filter:
            filters_payload["languages"] = languages_filter
        if type_filter:
            if len(type_filter) == 1:
                filters_payload["type"] = type_filter[0]

        params = {
            "filters": json.dumps(filters_payload)
        }
        if query:
            params["query"] = query

        logger.info(f"Calling developer.sampleData.get with filters: {filters_payload}")

        response = client.api_call(
            api_method="developer.sampleData.get",
            params=params
        )

        if not response.get("ok"):
            logger.error(f"API error: {response}")
            fail(error="Failed to fetch sample data")
            return

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
        logger.error(f"Error in search step: {str(e)}")
        fail(error=str(e))
    finally:
        ack()


@app.function("filters", auto_acknowledge=False)
def handle_filters_step_event(
    ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger
):
    try:
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
    finally:
        ack()

@app.event("entity_details_requested")
def handle_flexpane_event(event, body, client, logger):
    sample_id = event["external_ref"]["id"]

    response = client.api_call(api_method="developer.sampleData.get")

    if not response.get("ok"):
        logger.error(f"Failed to fetch samples: {response}")
        return

    samples = response.get("samples", [])

    sample = next((s for s in samples if s["external_ref"]["id"] == sample_id), None)

    if not sample:
        logger.warning(f"No matching sample found for id={sample_id}")
        return


    custom_fields = [
        {
            "key": "description",
            "label": "Description of sample",
            "type": "string",
            "value": sample["description"],
        },
        {
            "key": "date_updated",
            "label": "Last updated",
            "type": "string",
            "value": sample["date_updated"],
        },
    ]

    if "content" in sample:
        custom_fields.append({
            "key": "content",
            "label": "Details of sample",
            "type": "string",
            "value": sample["content"],
        })

    payload = {
        "trigger_id": event["trigger_id"],
        "metadata": {
            "entity_type": "slack#/entities/item",
            "url": event["link"]["url"],
            "external_ref": {"id": sample_id},
            "entity_payload": {
                "attributes": {
                    "title": {
                        "text": sample["title"],
                        "edit": {
                            "enabled": False,
                            "text": {
                                "max_length": 50
                            }
                        }
                    },
                },
                "custom_fields": custom_fields,
            },
        },
    }

    try:
        client.api_call(
            api_method="entity.presentDetails",
            json=payload,
        )
    except Exception as e:
        logger.error(f"Error calling entity.presentDetails: {str(e)}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
