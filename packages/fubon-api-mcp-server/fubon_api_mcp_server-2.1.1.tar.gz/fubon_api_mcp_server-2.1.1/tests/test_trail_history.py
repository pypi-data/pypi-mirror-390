"""
Tests for get_trail_history MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import get_trail_history


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestGetTrailHistory:
    """Test get_trail_history function."""

    def test_get_trail_history_success(self, mock_server_globals, mock_sdk):
        """Test successful retrieval of trail history."""
        # Arrange: mock SDK response
        detail_item = SimpleNamespace(
            guid="abc-123",
            batch_no="",
            order_level="0",
            last_time="2024-08-02 16:45:01",
            parent_guid=None,
            symbol="2330",
            order_amount="0",
            child_batch_no="",
            account="123456",
            condition_content="...",
            action="下單",
            condition_buy_sell="現股買",
            condition_symbol="台積電 (2330)",
            condition_price="成交價(1) 檔(ROD)",
            condition_volume="2張",
            condition_filled_volume="0張",
            create_time="2024-08-02 10:07:31",
            start_date="2024/08/02",
            status="條件單中止(I)",
            error_message=None,
            detail_records_count="0",
            detail_records=[],
            TPSLCount="0",
            TPSLRecord=[],
        )
        mock_sdk.stock.get_trail_history.return_value = make_result(True, [detail_item])

        # Act
        result = get_trail_history(
            {
                "account": "123456",
                "start_date": "20240310",
                "end_date": "20240601",
            }
        )

        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], list)
        assert result["data"][0]["guid"] == "abc-123"
        assert "20240310" in result["message"] and "20240601" in result["message"]

    def test_get_trail_history_error(self, mock_server_globals, mock_sdk):
        """Test error handling in get_trail_history."""
        mock_sdk.stock.get_trail_history.return_value = make_result(False, None, "some error")

        result = get_trail_history(
            {
                "account": "123456",
                "start_date": "20240310",
                "end_date": "20240601",
            }
        )

        assert result["status"] == "error"
        assert "查詢失敗" in result["message"]
