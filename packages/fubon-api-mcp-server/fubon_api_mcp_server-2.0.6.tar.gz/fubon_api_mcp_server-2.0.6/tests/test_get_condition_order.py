"""
Tests for get_condition_order MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import get_condition_order


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestGetConditionOrder:
    """Test get_condition_order function."""

    def test_get_condition_order_success(self, mock_server_globals, mock_sdk):
        """Test successful retrieval of condition orders."""
        # Arrange
        item1 = SimpleNamespace(
            guid="8ff3472b-185a-488c-be5a-b478deda080c",
            batch_no="",
            order_level="1",
            last_time="2024-03-14 12:39:02",
            condition_type="多條件",
            parent_guid="",
            symbol="2330",
            order_amount="0",
            child_batch_no="",
            account="123456",
            condition_content="...",
            action="下單",
            condition_buy_sell="現股賣",
            condition_symbol="台積電 現股賣",
            condition_price="580元(ROD)",
            condition_volume="5張",
            condition_filled_volume="0張",
            creat_time="2024-03-14 12:39:22",
            start_date="2024/03/14",
            status="未生效(W)",
            error_message=None,
            detail_records_count="0",
            detail_records=[],
            tpslCount="0",
            tpslRecord=[],
        )
        item2 = SimpleNamespace(**{**vars(item1), "guid": "ec757279-bcb3-46f4-80ac-fccfc786bc8d"})
        mock_sdk.stock.get_condition_order.return_value = make_result(True, [item1, item2])

        # Act
        result = get_condition_order({"account": "123456"})

        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["guid"] == "8ff3472b-185a-488c-be5a-b478deda080c"

    def test_get_condition_order_error(self, mock_server_globals, mock_sdk):
        """Test error handling in get_condition_order."""
        mock_sdk.stock.get_condition_order.return_value = make_result(False, None, "some error")

        result = get_condition_order({"account": "123456", "condition_status": "InvalidStatus"})

        # 因為先做狀態名稱檢查，這裡會在 mapping 階段就回錯
        assert result["status"] == "error"
        assert "不支援的條件單狀態" in result["message"]
