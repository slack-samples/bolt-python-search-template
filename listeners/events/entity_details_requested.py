import logging

from slack_sdk import WebClient

from listeners.sample_data_fetcher import SlackResponseError, fetch_sample_data


def entity_details_requested_callback(event: dict, client: WebClient, logger: logging.Logger):
    try:
        sample_id = event["external_ref"]["id"]
        response = fetch_sample_data(client=client, logger=logger)
        samples = response.get("samples", [])

        sample = next((s for s in samples if s["external_ref"]["id"] == sample_id), None)

        if not sample:
            logger.warning(f"Unable to find sample with ID '{sample_id}' in the fetched samples data")
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
            custom_fields.append(
                {
                    "key": "content",
                    "label": "Details of sample",
                    "type": "string",
                    "value": sample["content"],
                }
            )

        payload = {
            "trigger_id": event["trigger_id"],
            "metadata": {
                "entity_type": "slack#/entities/item",
                "url": event["link"]["url"],
                "external_ref": {"id": sample_id},
                "entity_payload": {
                    "attributes": {
                        "title": {"text": sample["title"], "edit": {"enabled": False, "text": {"max_length": 50}}},
                    },
                    "custom_fields": custom_fields,
                },
            },
        }
        client.api_call(
            api_method="entity.presentDetails",
            json=payload,
        )
    except SlackResponseError as e:
        logger.error(f"Failed to fetch or parse sample data. Error details: {str(e)}", exc_info=e)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred handling entity_details_requested event: {type(e).__name__} - {str(e)}",
            exc_info=e,
        )
