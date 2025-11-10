"""
Tests for cancel_condition_order MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import cancel_condition_order


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestCancelConditionOrder:
    """Test cancel_condition_order function."""

    def test_cancel_condition_order_success(self, mock_server_globals, mock_sdk):
        """Test successful cancellation of condition order."""
        mock_sdk.stock.cancel_condition_orders.return_value = make_result(
            True, SimpleNamespace(advisory="成功筆數:1,失敗筆數:0!")
        )

        result = cancel_condition_order({"account": "123456", "guid": "c9df498a-3b28-4b50-a6f2-f7bd524e96df"})

        assert result["status"] == "success"
        assert isinstance(result["data"], dict)
        assert result["data"]["advisory"] == "成功筆數:1,失敗筆數:0!"
        assert "成功" in result["message"]

    def test_cancel_condition_order_error(self, mock_server_globals, mock_sdk):
        """Test error handling in cancel_condition_order."""
        mock_sdk.stock.cancel_condition_orders.return_value = make_result(False, None, "some error")

        result = cancel_condition_order({"account": "123456", "guid": "bad-guid"})

        assert result["status"] == "error"
        assert "取消失敗" in result["message"]
