from unittest.mock import MagicMock, patch

from slack_sdk import WebClient

from listeners.events.entity_details_requested import entity_details_requested_callback
from listeners.sample_data_fetcher import SlackResponseError


class TestEntityDetailsRequested:
    def setup_method(self):
        self.mock_client = MagicMock(spec=WebClient)
        self.mock_logger = MagicMock()

        self.mock_sample_data = {
            "ok": True,
            "samples": [
                {
                    "title": "Sample 1",
                    "description": "Description 1",
                    "link": "https://example.com/1",
                    "date_updated": "2023-01-01",
                    "external_ref": {"id": "sample1"},
                },
                {
                    "title": "Sample 2",
                    "description": "Description 2",
                    "link": "https://example.com/2",
                    "date_updated": "2023-01-02",
                    "external_ref": {"id": "sample2"},
                    "content": "Full content here",
                },
            ],
        }

        self.event_payload = {
            "trigger_id": "123.456.abc",
            "link": {"url": "https://example.com/1"},
            "external_ref": {"id": "sample1"},
        }

    @patch("listeners.events.entity_details_requested.fetch_sample_data")
    def test_entity_details_requested_success(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = self.mock_sample_data

        entity_details_requested_callback(event=self.event_payload, client=self.mock_client, logger=self.mock_logger)

        mock_fetch_sample_data.assert_called_once_with(client=self.mock_client, logger=self.mock_logger)

        self.mock_client.api_call.assert_called_once()
        call_args = self.mock_client.api_call.call_args

        assert call_args.kwargs["api_method"] == "entity.presentDetails"

        assert call_args.kwargs["json"] == {
            "trigger_id": "123.456.abc",
            "metadata": {
                "entity_type": "slack#/entities/item",
                "url": "https://example.com/1",
                "external_ref": {"id": "sample1"},
                "entity_payload": {
                    "attributes": {"title": {"text": "Sample 1", "edit": {"enabled": False, "text": {"max_length": 50}}}},
                    "custom_fields": [
                        {"key": "description", "label": "Description of sample", "type": "string", "value": "Description 1"},
                        {"key": "date_updated", "label": "Last updated", "type": "string", "value": "2023-01-01"},
                    ],
                },
            },
        }

    @patch("listeners.events.entity_details_requested.fetch_sample_data")
    def test_entity_details_requested_with_content(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = self.mock_sample_data

        event_payload = dict(self.event_payload)
        event_payload["external_ref"]["id"] = "sample2"

        entity_details_requested_callback(event=event_payload, client=self.mock_client, logger=self.mock_logger)

        self.mock_client.api_call.assert_called_once()
        call_args = self.mock_client.api_call.call_args

        custom_fields = call_args.kwargs["json"]["metadata"]["entity_payload"]["custom_fields"]
        assert len(custom_fields) == 3  # Description, date_updated, and content

        content_fields = [field for field in custom_fields if field["key"] == "content"]
        assert len(content_fields) == 1
        assert content_fields[0]["value"] == "Full content here"

    @patch("listeners.events.entity_details_requested.fetch_sample_data")
    def test_entity_details_requested_sample_not_found(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = self.mock_sample_data

        event_payload = dict(self.event_payload)
        event_payload["external_ref"]["id"] = "nonexistent"

        entity_details_requested_callback(event=event_payload, client=self.mock_client, logger=self.mock_logger)

        self.mock_logger.warning.assert_called_once()
        self.mock_client.api_call.assert_not_called()

    @patch("listeners.events.entity_details_requested.fetch_sample_data")
    def test_entity_details_requested_slack_response_error(self, mock_fetch_sample_data):
        mock_fetch_sample_data.side_effect = SlackResponseError("API error")

        entity_details_requested_callback(event=self.event_payload, client=self.mock_client, logger=self.mock_logger)

        self.mock_logger.error.assert_called_once()
        self.mock_client.api_call.assert_not_called()

    @patch("listeners.events.entity_details_requested.fetch_sample_data")
    def test_entity_details_requested_unexpected_exception(self, mock_fetch_sample_data):
        mock_fetch_sample_data.side_effect = Exception("Unexpected error")

        entity_details_requested_callback(event=self.event_payload, client=self.mock_client, logger=self.mock_logger)

        self.mock_logger.error.assert_called_once()
        self.mock_client.api_call.assert_not_called()
