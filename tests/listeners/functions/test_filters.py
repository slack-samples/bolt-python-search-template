from unittest.mock import MagicMock

from slack_bolt import Ack, Complete, Fail

from listeners.functions.filters import FILTER_PROCESSING_ERROR_MSG, filters_step_callback


class TestFilters:
    def setup_method(self):
        self.mock_ack = MagicMock(spec=Ack)
        self.mock_fail = MagicMock(spec=Fail)
        self.mock_complete = MagicMock(spec=Complete)
        self.mock_logger = MagicMock()

        self.expected_filters = [
            {
                "name": "languages",
                "display_name": "Languages",
                "type": "multi_select",
                "options": [
                    {"name": "Python", "value": "python"},
                    {"name": "Java", "value": "java"},
                    {"name": "JavaScript", "value": "javascript"},
                    {"name": "TypeScript", "value": "typescript"},
                ],
            },
            {
                "name": "template",
                "display_name": "Templates",
                "type": "toggle",
            },
            {
                "name": "sample",
                "display_name": "Samples",
                "type": "toggle",
            },
        ]

    def test_filters_step_callback_success(self):
        inputs = {"user_context": {"id": "U123456"}}

        filters_step_callback(
            ack=self.mock_ack,
            inputs=inputs,
            fail=self.mock_fail,
            complete=self.mock_complete,
            logger=self.mock_logger,
        )

        self.mock_complete.assert_called_once()
        call_args = self.mock_complete.call_args
        outputs = call_args.kwargs["outputs"]
        assert outputs["filters"] == self.expected_filters

        self.mock_ack.assert_called_once()
        self.mock_fail.assert_not_called()

    def test_filters_step_callback_empty_user_context(self):
        filters_step_callback(
            ack=self.mock_ack,
            inputs={},
            fail=self.mock_fail,
            complete=self.mock_complete,
            logger=self.mock_logger,
        )

        self.mock_complete.assert_called_once()
        call_args = self.mock_complete.call_args
        outputs = call_args.kwargs["outputs"]
        assert outputs["filters"] == self.expected_filters

        self.mock_ack.assert_called_once()

    def test_filters_step_callback_unexpected_exception(self):
        self.mock_complete.side_effect = Exception("Unexpected error")

        filters_step_callback(
            ack=self.mock_ack,
            inputs={},
            fail=self.mock_fail,
            complete=self.mock_complete,
            logger=self.mock_logger,
        )

        self.mock_fail.assert_called_once()
        call_args = self.mock_fail.call_args
        print(FILTER_PROCESSING_ERROR_MSG)
        assert call_args.kwargs["error"] == FILTER_PROCESSING_ERROR_MSG

        self.mock_ack.assert_called_once()
