from unittest.mock import MagicMock, patch

from slack_bolt import Ack, Complete, Fail
from slack_sdk import WebClient

from listeners.functions.search import search_step_callback, SEARCH_PROCESSING_ERROR_MSG
from listeners.sample_data_fetcher import SlackResponseError


class TestSearch:
    def setup_method(self):
        self.mock_ack = MagicMock(spec=Ack)
        self.mock_fail = MagicMock(spec=Fail)
        self.mock_complete = MagicMock(spec=Complete)
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

    @patch("listeners.functions.search.fetch_sample_data")
    def test_search_step_callback_success(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = self.mock_sample_data

        inputs = {"query": "test query", "filters": {"languages": ["python"], "type": ["code"]}}

        search_step_callback(
            ack=self.mock_ack,
            inputs=inputs,
            fail=self.mock_fail,
            complete=self.mock_complete,
            client=self.mock_client,
            logger=self.mock_logger,
        )

        mock_fetch_sample_data.assert_called_once_with(
            client=self.mock_client,
            query="test query",
            filters={"languages": ["python"], "type": "code"},
            logger=self.mock_logger,
        )

        self.mock_complete.assert_called_once()
        call_args = self.mock_complete.call_args
        outputs = call_args.kwargs["outputs"]
        assert outputs["search_result"] == self.mock_sample_data["samples"]

        self.mock_ack.assert_called_once()
        self.mock_fail.assert_not_called()

    @patch("listeners.functions.search.fetch_sample_data")
    def test_search_step_callback_no_filters(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = {"samples": []}

        search_step_callback(
            ack=self.mock_ack,
            inputs={"query": "test query"},
            fail=self.mock_fail,
            complete=self.mock_complete,
            client=self.mock_client,
            logger=self.mock_logger,
        )

        mock_fetch_sample_data.assert_called_once_with(
            client=self.mock_client, query="test query", filters={}, logger=self.mock_logger
        )

        self.mock_complete.assert_called_once()
        call_args = self.mock_complete.call_args
        outputs = call_args.kwargs["outputs"]
        assert outputs["search_result"] == []

        self.mock_ack.assert_called_once()

    @patch("listeners.functions.search.fetch_sample_data")
    def test_search_step_callback_slack_response_error(self, mock_fetch_sample_data):
        mock_fetch_sample_data.side_effect = SlackResponseError("API error")

        search_step_callback(
            ack=self.mock_ack,
            inputs={"query": "test query"},
            fail=self.mock_fail,
            complete=self.mock_complete,
            client=self.mock_client,
            logger=self.mock_logger,
        )

        self.mock_fail.assert_called_once()
        call_args = self.mock_fail.call_args
        assert call_args.kwargs["error"] == SEARCH_PROCESSING_ERROR_MSG

        self.mock_complete.assert_not_called()
        self.mock_ack.assert_called_once()

    @patch("listeners.functions.search.fetch_sample_data")
    def test_search_step_callback_unexpected_exception(self, mock_fetch_sample_data):
        mock_fetch_sample_data.side_effect = Exception("Unexpected error")

        search_step_callback(
            ack=self.mock_ack,
            inputs={"query": "test query"},
            fail=self.mock_fail,
            complete=self.mock_complete,
            client=self.mock_client,
            logger=self.mock_logger,
        )

        self.mock_fail.assert_called_once()
        call_args = self.mock_fail.call_args
        assert call_args.kwargs["error"] == SEARCH_PROCESSING_ERROR_MSG

        self.mock_complete.assert_not_called()
        self.mock_ack.assert_called_once()

    @patch("listeners.functions.search.fetch_sample_data")
    def test_search_step_callback_multiple_type_filters(self, mock_fetch_sample_data):
        mock_fetch_sample_data.return_value = {"samples": []}

        inputs = {"query": "test query", "filters": {"type": ["code", "document"]}}

        search_step_callback(
            ack=self.mock_ack,
            inputs=inputs,
            fail=self.mock_fail,
            complete=self.mock_complete,
            client=self.mock_client,
            logger=self.mock_logger,
        )

        mock_fetch_sample_data.assert_called_once_with(
            client=self.mock_client, query="test query", filters={}, logger=self.mock_logger
        )

        self.mock_complete.assert_called_once()
