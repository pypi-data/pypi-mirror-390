"""
Tests for place_time_slice_order MCP tool.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fubon_api_mcp_server.server import place_time_slice_order


def make_result(success: bool, data=None, message: str | None = None):
    res = Mock()
    res.is_success = success
    res.data = data
    res.message = message
    return res


class TestPlaceTimeSliceOrder:
    """Test place_time_slice_order function."""

    def test_place_time_slice_order_success(self, mock_server_globals, mock_sdk):
        """Test successful placement of time slice order."""
        # Arrange
        mock_sdk.stock.time_slice_order.return_value = make_result(True, SimpleNamespace(guid="24080500000002"))

        payload = {
            "account": "123456",
            "start_date": "20240427",
            "end_date": "20240516",
            "stop_sign": "Full",
            "split": {
                "method": "Type1",
                "interval": 300,
                "single_quantity": 1000,
                "total_quantity": 10000,
                "start_time": "083000",
            },
            "order": {
                "buy_sell": "Buy",
                "symbol": "2881",
                "price": "66",
                "quantity": 1000,
                "market_type": "Common",
                "price_type": "Limit",
                "time_in_force": "ROD",
                "order_type": "Stock",
            },
        }

        # Act
        result = place_time_slice_order(payload)

        # Assert
        assert result["status"] == "success"
        assert result["data"]["guid"] == "24080500000002"
        assert result["data"]["symbol"] == "2881"
        assert result["data"]["method"] == "Type1"
        assert "分時分量條件單已成功建立" in result["message"]

    def test_place_time_slice_order_error(self, mock_server_globals, mock_sdk):
        """Test error handling in place_time_slice_order."""
        mock_sdk.stock.time_slice_order.return_value = make_result(False, None, "some error")

        payload = {
            "account": "123456",
            "start_date": "20240427",
            "end_date": "20240516",
            "stop_sign": "Full",
            "split": {
                "method": "Type1",
                "interval": 300,
                "single_quantity": 1000,
                "total_quantity": 10000,
                "start_time": "083000",
            },
            "order": {
                "buy_sell": "Buy",
                "symbol": "2881",
                "price": "66",
                "quantity": 1000,
                "market_type": "Common",
                "price_type": "Limit",
                "time_in_force": "ROD",
                "order_type": "Stock",
            },
        }

        result = place_time_slice_order(payload)

        assert result["status"] == "error"
        assert "分時分量條件單建立失敗" in result["message"]
