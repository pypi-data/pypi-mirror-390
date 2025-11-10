"""
Tests for get_time_slice_order MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import get_time_slice_order


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestGetTimeSliceOrder:
    """Test get_time_slice_order function."""

    def test_get_time_slice_order_success(self, mock_server_globals, mock_sdk):
        """Test successful retrieval of time slice orders."""
        # Arrange
        item1 = SimpleNamespace(
            guid="c4dc90c1-4277-42ea-b585-085dc347eac0",
            batch_no="",
            order_level="0",
            last_time="2024-07-23 17:30:01",
            condition_type="分時分量",
            parent_guid="",
            symbol="2881",
            order_amount="0",
            child_batch_no="",
            account="123456",
            condition_content="...",
            action="下單",
            condition_buy_sell="現股買",
            condition_symbol="富邦金 現股買",
            condition_price="66元(ROD)",
            condition_volume="1張",
            condition_filled_volume="0張",
            create_time="2024-07-22 17:30:03",
            start_date="2024/07/23",
            status="條件單中止(I)",
            error_message=None,
            detail_records_count="0",
            detail_records=[],
            TPSLCount="0",
            TPSLRecord=[],
        )
        item2 = SimpleNamespace(**{**vars(item1), "guid": "2975702e-f36f-4da4-bab6-1310344ec05d"})
        mock_sdk.stock.get_time_slice_order.return_value = make_result(True, [item1, item2])

        # Act
        result = get_time_slice_order({"account": "123456", "batch_no": "123456"})

        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["guid"] == "c4dc90c1-4277-42ea-b585-085dc347eac0"
        assert "batch_no=123456" in result["message"]

    def test_get_time_slice_order_error(self, mock_server_globals, mock_sdk):
        """Test error handling in get_time_slice_order."""
        mock_sdk.stock.get_time_slice_order.return_value = make_result(False, None, "some error")

        result = get_time_slice_order({"account": "123456", "batch_no": "999"})

        assert result["status"] == "error"
        assert "查詢失敗" in result["message"]
