"""
Tests for get_condition_order_by_id MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import get_condition_order_by_id


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestGetConditionOrderById:
    """Test get_condition_order_by_id function."""

    def test_get_condition_order_by_id_success(self, mock_server_globals, mock_sdk):
        """Test successful retrieval of condition order by ID."""
        # Arrange a single ConditionDetail-like object
        detail = SimpleNamespace(
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
        mock_sdk.stock.get_condition_order_by_id.return_value = make_result(True, detail)

        # Act
        result = get_condition_order_by_id({"account": "123456", "guid": "8ff3472b-185a-488c-be5a-b478deda080c"})

        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], dict)
        assert result["data"]["guid"] == "8ff3472b-185a-488c-be5a-b478deda080c"
        assert "查詢成功" in result["message"]

    def test_get_condition_order_by_id_error(self, mock_server_globals, mock_sdk):
        """Test error handling in get_condition_order_by_id."""
        mock_sdk.stock.get_condition_order_by_id.return_value = make_result(False, None, "some error")

        result = get_condition_order_by_id({"account": "123456", "guid": "bad-guid"})

        assert result["status"] == "error"
        assert "查詢失敗" in result["message"]
