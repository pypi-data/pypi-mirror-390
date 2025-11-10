"""
Tests for callback functions.
"""

from unittest.mock import Mock, patch

import pytest

from fubon_api_mcp_server.server import (
    on_event,
    on_filled,
    on_order,
    on_order_changed,
)


class TestCallbacks:
    """Test callback functions."""

    @patch("fubon_api_mcp_server.server.latest_order_reports")
    def test_on_order(self, mock_reports):
        """Test on_order callback."""
        mock_reports.__iter__ = lambda: iter([])
        mock_reports.append = Mock()
        mock_reports.__len__ = lambda: 0

        test_data = {"order_no": "12345", "symbol": "2330"}

        on_order(test_data)

        mock_reports.append.assert_called_once()
        args = mock_reports.append.call_args[0][0]
        assert args["data"] == test_data
        assert "timestamp" in args

    @patch("fubon_api_mcp_server.server.latest_order_changed_reports")
    def test_on_order_changed(self, mock_reports):
        """Test on_order_changed callback."""
        mock_reports.__iter__ = lambda: iter([])
        mock_reports.append = Mock()
        mock_reports.__len__ = lambda: 0

        test_data = {"order_no": "12345", "new_price": 505.0}

        on_order_changed(test_data)

        mock_reports.append.assert_called_once()
        args = mock_reports.append.call_args[0][0]
        assert args["data"] == test_data
        assert "timestamp" in args

    @patch("fubon_api_mcp_server.server.latest_filled_reports")
    def test_on_filled(self, mock_reports):
        """Test on_filled callback."""
        mock_reports.__iter__ = lambda: iter([])
        mock_reports.append = Mock()
        mock_reports.__len__ = lambda: 0

        test_data = {"order_no": "12345", "filled_qty": 100}

        on_filled(test_data)

        mock_reports.append.assert_called_once()
        args = mock_reports.append.call_args[0][0]
        assert args["data"] == test_data
        assert "timestamp" in args

    @patch("fubon_api_mcp_server.server.latest_event_reports")
    def test_on_event(self, mock_reports):
        """Test on_event callback."""
        mock_reports.__iter__ = lambda: iter([])
        mock_reports.append = Mock()
        mock_reports.__len__ = lambda: 0

        test_data = {"event_type": "market_open", "message": "Market opened"}

        on_event(test_data)

        mock_reports.append.assert_called_once()
        args = mock_reports.append.call_args[0][0]
        assert args["data"] == test_data
        assert "timestamp" in args

    @patch("fubon_api_mcp_server.server.latest_order_reports")
    def test_on_order_limit_reports(self, mock_reports):
        """Test that on_order limits reports to 10."""
        # Initialize with 11 items to test limiting
        mock_reports.__iter__ = lambda self: iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        mock_reports.__len__ = Mock(return_value=11)
        mock_reports.append = Mock()
        mock_reports.pop = Mock()

        test_data = {"order_no": "12346", "symbol": "2454"}

        on_order(test_data)

        # Should maintain only 10 most recent reports
        mock_reports.append.assert_called_once()
        mock_reports.pop.assert_called_once()

    @patch("fubon_api_mcp_server.server.latest_order_changed_reports")
    def test_on_order_changed_limit_reports(self, mock_reports):
        """Test that on_order_changed limits reports to 10."""
        # Initialize with 11 items to test limiting
        mock_reports.__iter__ = lambda self: iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        mock_reports.__len__ = Mock(return_value=11)
        mock_reports.append = Mock()
        mock_reports.pop = Mock()

        test_data = {"order_no": "12345", "new_quantity": 1500}

        on_order_changed(test_data)

        mock_reports.append.assert_called_once()
        mock_reports.pop.assert_called_once()

    @patch("fubon_api_mcp_server.server.latest_filled_reports")
    def test_on_filled_limit_reports(self, mock_reports):
        """Test that on_filled limits reports to 10."""
        # Initialize with 11 items to test limiting
        mock_reports.__iter__ = lambda self: iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        mock_reports.__len__ = Mock(return_value=11)
        mock_reports.append = Mock()
        mock_reports.pop = Mock()

        test_data = {"order_no": "12345", "filled_price": 500.0}

        on_filled(test_data)

        mock_reports.append.assert_called_once()
        mock_reports.pop.assert_called_once()

    @patch("fubon_api_mcp_server.server.latest_event_reports")
    def test_on_event_limit_reports(self, mock_reports):
        """Test that on_event limits reports to 10."""
        # Initialize with 11 items to test limiting
        mock_reports.__iter__ = lambda self: iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        mock_reports.__len__ = Mock(return_value=11)
        mock_reports.append = Mock()
        mock_reports.pop = Mock()

        test_data = {"event_type": "disconnected"}

        on_event(test_data)

        mock_reports.append.assert_called_once()
        mock_reports.pop.assert_called_once()

    @patch("fubon_api_mcp_server.server.print")
    def test_on_order_with_exception(self, mock_print):
        """Test on_order handles exceptions gracefully."""
        # This will test the exception handling in the callback
        # Since latest_order_reports is patched to a list that might not support append
        with patch("fubon_api_mcp_server.server.latest_order_reports", Mock()) as mock_reports:
            mock_reports.append.side_effect = Exception("Test exception")

            test_data = {"order_no": "12345"}
            on_order(test_data)

            # Should not raise exception, just print error
            mock_print.assert_called()

    @patch("fubon_api_mcp_server.server.print")
    def test_on_order_changed_with_exception(self, mock_print):
        """Test on_order_changed handles exceptions gracefully."""
        with patch("fubon_api_mcp_server.server.latest_order_changed_reports", Mock()) as mock_reports:
            mock_reports.append.side_effect = Exception("Test exception")

            test_data = {"order_no": "12345"}
            on_order_changed(test_data)

            mock_print.assert_called()

    @patch("fubon_api_mcp_server.server.print")
    def test_on_filled_with_exception(self, mock_print):
        """Test on_filled handles exceptions gracefully."""
        with patch("fubon_api_mcp_server.server.latest_filled_reports", Mock()) as mock_reports:
            mock_reports.append.side_effect = Exception("Test exception")

            test_data = {"order_no": "12345"}
            on_filled(test_data)

            mock_print.assert_called()

    @patch("fubon_api_mcp_server.server.print")
    def test_on_event_with_exception(self, mock_print):
        """Test on_event handles exceptions gracefully."""
        with patch("fubon_api_mcp_server.server.latest_event_reports", Mock()) as mock_reports:
            mock_reports.append.side_effect = Exception("Test exception")

            test_data = {"event_type": "error"}
            on_event(test_data)

            mock_print.assert_called()
