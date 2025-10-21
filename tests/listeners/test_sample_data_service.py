from unittest.mock import MagicMock
import pytest

from slack_sdk import WebClient

from listeners.filters import LANGUAGES_FILTER, SAMPLES_FILTER, TEMPLATES_FILTER
from listeners.sample_data_service import API_METHOD, SlackResponseError, fetch_sample_data


class TestSampleDataService:
    def setup_method(self):
        self.mock_client = MagicMock(spec=WebClient)
        self.mock_logger = MagicMock()
        
        self.mock_response = {
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
        
        self.mock_client.api_call.return_value = self.mock_response

    def test_fetch_sample_data_no_filters(self):
        result = fetch_sample_data(client=self.mock_client, logger=self.mock_logger)
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": None}
        )
        assert result == self.mock_response

    def test_fetch_sample_data_with_query(self):
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            logger=self.mock_logger
        )
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query"}
        )
        assert result == self.mock_response

    def test_fetch_sample_data_with_languages_filter(self):
        filters = {LANGUAGES_FILTER.name: ["python", "javascript"]}
        
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            filters=filters,
            logger=self.mock_logger
        )

        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query", "filters": filters}
        )
        
        assert result == self.mock_response

    def test_fetch_sample_data_with_templates_filter(self):
        filters = {TEMPLATES_FILTER.name: True}
        
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            filters=filters,
            logger=self.mock_logger
        )
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query", "filters": {"type": TEMPLATES_FILTER.name}}
        )
        
        assert result == self.mock_response

    def test_fetch_sample_data_with_samples_filter(self):
        filters = {SAMPLES_FILTER.name: True}
        
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            filters=filters,
            logger=self.mock_logger
        )
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query", "filters": {"type": SAMPLES_FILTER.name}}
        )
        
        assert result == self.mock_response

    def test_fetch_sample_data_with_combined_filters(self):
        filters = {
            LANGUAGES_FILTER.name: ["python"],
            TEMPLATES_FILTER.name: True
        }
        
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            filters=filters,
            logger=self.mock_logger
        )
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query", "filters": {LANGUAGES_FILTER.name: ["python"], "type": TEMPLATES_FILTER.name}}
        )
        
        assert result == self.mock_response

    def test_fetch_sample_data_with_both_template_and_sample(self):
        filters = {
            TEMPLATES_FILTER.name: True,
            SAMPLES_FILTER.name: True
        }
        
        result = fetch_sample_data(
            client=self.mock_client, 
            query="test query",
            filters=filters,
            logger=self.mock_logger
        )
        
        self.mock_client.api_call.assert_called_once_with(
            API_METHOD, params={"query": "test query"}
        )
        
        assert result == self.mock_response

    def test_fetch_sample_data_api_error(self):
        error_response = {"ok": False, "error": "invalid_auth"}
        self.mock_client.api_call.return_value = error_response
        
        with pytest.raises(SlackResponseError) as excinfo:
            fetch_sample_data(
                client=self.mock_client,
                query="test query",
                logger=self.mock_logger
            )
        
        # Verify error was logged
        self.mock_logger.error.assert_called_once()
        
        # Verify exception message
        assert f"Failed to fetch sample data from Slack API: ok=false for method={API_METHOD}" in str(excinfo.value)
