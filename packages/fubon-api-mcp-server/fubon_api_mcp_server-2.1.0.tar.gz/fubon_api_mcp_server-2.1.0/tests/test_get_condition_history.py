"""
Tests for get_condition_history MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import get_condition_history


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestGetConditionHistory:
    """Test get_condition_history function."""

    def test_get_condition_history_success(self, mock_server_globals, mock_sdk):
        """Test successful retrieval of condition history."""
        # Arrange two ConditionDetail-like records
        item1 = SimpleNamespace(
            guid="aaaa",
            batch_no="",
            order_level="0",
            last_time="2024-07-29 17:30:00",
            condition_type="多條件",
            parent_guid="",
            symbol="2330",
            order_amount="0",
            child_batch_no="",
            account="123456",
            condition_content="...",
            action="下單",
            condition_buy_sell="現股買",
            condition_symbol="台積電 (2330)",
            condition_price="市價(ROD)",
            condition_volume="2張",
            condition_filled_volume="0張",
            create_time="2024-07-29 11:01:49",
            start_date="2024/07/29",
            status="條件單中止(I)",
            error_message=None,
            detail_records_count="0",
            detail_records=[],
            TPSLCount="0",
            TPSLRecord=[],
        )
        item2 = SimpleNamespace(**{**vars(item1), "guid": "bbbb"})

        mock_sdk.stock.get_condition_history.return_value = make_result(True, [item1, item2])

        # Act
        result = get_condition_history(
            {
                "account": "123456",
                "start_date": "20240310",
                "end_date": "20240601",
            }
        )

        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["guid"] == "aaaa"
        assert "20240310" in result["message"] and "20240601" in result["message"]

    def test_get_condition_history_error(self, mock_server_globals, mock_sdk):
        """Test error handling in get_condition_history."""
        mock_sdk.stock.get_condition_history.return_value = make_result(False, None, "some error")

        result = get_condition_history(
            {
                "account": "123456",
                "start_date": "20240310",
                "end_date": "20240601",
                "condition_history_status": "InvalidStatus",
            }
        )

        # invalid status name is handled before SDK call
        assert result["status"] == "error"
        assert "不支援的歷史條件單狀態" in result["message"]
