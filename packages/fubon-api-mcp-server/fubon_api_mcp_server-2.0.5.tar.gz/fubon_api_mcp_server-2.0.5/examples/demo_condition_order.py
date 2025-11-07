#!/usr/bin/env python3
"""
條件單功能示範

此腳本示範如何使用富邦證券 MCP Server 的條件單功能：
1. 單一條件單（Simple Condition Order）
2. 停損停利條件單（TPSL - Take Profit Stop Loss）

注意：條件單目前不支援期權商品與現貨商品混用。
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from fubon_api_mcp_server.server import (
    place_condition_order,
    place_tpsl_condition_order,
    place_multi_condition_order,
    place_daytrade_condition_order,
    PlaceConditionOrderArgs,
    PlaceMultiConditionOrderArgs,
    PlaceDayTradeConditionOrderArgs,
)

# 載入環境變數
load_dotenv()


def demo_single_condition_order():
    """
    示範單一條件單

    場景：當 2881 股價跌破 80 元時，自動賣出 1000 股（限價 60 元）
    """
    print("\n" + "=" * 60)
    print("示範 1: 單一條件單")
    print("=" * 60)

    # 模擬帳戶號碼（請替換為您的實際帳戶）
    account = os.getenv("FUBON_ACCOUNT", "YOUR_ACCOUNT_NUMBER")

    condition_order_data = {
        "account": account,
        "start_date": "20240427",  # 開始日期
        "end_date": "20240516",  # 結束日期
        "stop_sign": "Full",  # 全部成交為止
        # 觸發條件：當 2881 成交價 < 80
        "condition": {
            "market_type": "Reference",  # 參考價
            "symbol": "2881",
            "trigger": "MatchedPrice",  # 成交價
            "trigger_value": "80",
            "comparison": "LessThan",  # 小於
        },
        # 觸發後賣出
        "order": {
            "buy_sell": "Sell",
            "symbol": "2881",
            "price": "60",  # 限價 60
            "quantity": 1000,  # 1000 股 = 1 張
            "market_type": "Common",
            "price_type": "Limit",
            "time_in_force": "ROD",
            "order_type": "Stock",
        },
    }

    print("\n條件單設定：")
    print(f"  股票代碼：2881")
    print(f"  觸發條件：成交價 < 80")
    print(f"  觸發後動作：賣出 1000 股，限價 60")
    print(f"  有效期間：{condition_order_data['start_date']} ~ {condition_order_data['end_date']}")

    # 執行條件單（示範用，實際執行請取消註解）
    # result = place_condition_order(condition_order_data)
    # print(f"\n結果：{result}")

    print("\n條件單參數驗證：")
    try:
        validated = PlaceConditionOrderArgs(**condition_order_data)
        print("✅ 參數驗證通過")
        print(f"  帳戶：{validated.account}")
        print(f"  條件股票：{validated.condition['symbol']}")
        print(f"  停止條件：{validated.stop_sign}")
    except Exception as e:
        print(f"❌ 參數驗證失敗：{e}")


def demo_multi_condition_order():
    """
    示範多條件單

    場景：當 2881 股價跌破 66 元 AND 成交量小於 8000 時買入
          （所有條件必須同時滿足）
    """
    print("\n" + "=" * 60)
    print("示範 2: 多條件單（價格 AND 成交量）")
    print("=" * 60)

    # 模擬帳戶號碼
    account = os.getenv("FUBON_ACCOUNT", "YOUR_ACCOUNT_NUMBER")

    multi_condition_order_data = {
        "account": account,
        "start_date": "20240426",
        "end_date": "20240430",
        "stop_sign": "Full",
        # 多個觸發條件（全部須滿足）
        "conditions": [
            {
                "market_type": "Reference",
                "symbol": "2881",
                "trigger": "MatchedPrice",  # 成交價
                "trigger_value": "66",
                "comparison": "LessThan",  # < 66
            },
            {
                "market_type": "Reference",
                "symbol": "2881",
                "trigger": "TotalQuantity",  # 總量
                "trigger_value": "8000",
                "comparison": "LessThan",  # < 8000
            },
        ],
        # 觸發後買入
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

    print("\n多條件單設定：")
    print(f"  股票代碼：2881")
    print(f"  條件 1：成交價 < 66")
    print(f"  條件 2：總量 < 8000")
    print(f"  觸發條件：所有條件必須同時滿足")
    print(f"  觸發後動作：買入 1000 股，限價 66")

    # 執行多條件單（示範用，實際執行請取消註解）
    # result = place_multi_condition_order(multi_condition_order_data)
    # print(f"\n結果：{result}")

    print("\n多條件單參數驗證：")
    try:
        validated = PlaceMultiConditionOrderArgs(**multi_condition_order_data)
        print("✅ 參數驗證通過")
        print(f"  帳戶：{validated.account}")
        print(f"  條件數量：{len(validated.conditions)}")
        print(f"  條件股票：{validated.conditions[0]['symbol']}")
        print(f"  委託股票：{validated.order['symbol']}")
    except Exception as e:
        print(f"❌ 參數驗證失敗：{e}")


def demo_tpsl_condition_order():
    """
    示範停損停利條件單

    場景：當 2881 股價跌破 66 元時買入，
          買入後設定停利 85、停損 60（OCO 機制）
    """
    print("\n" + "=" * 60)
    print("示範 3: 停損停利條件單（TPSL with OCO）")
    print("=" * 60)

    # 模擬帳戶號碼
    account = os.getenv("FUBON_ACCOUNT", "YOUR_ACCOUNT_NUMBER")

    tpsl_order_data = {
        "account": account,
        "start_date": "20240426",
        "end_date": "20240430",
        "stop_sign": "Full",
        # 觸發條件：當 2881 成交價 < 66
        "condition": {
            "market_type": "Reference",
            "symbol": "2881",
            "trigger": "MatchedPrice",
            "trigger_value": "66",
            "comparison": "LessThan",
        },
        # 觸發後買入
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
        # 停損停利設定
        "tpsl": {
            "stop_sign": "Full",
            # 停利：價格到達 85 時賣出
            "tp": {
                "time_in_force": "ROD",
                "price_type": "Limit",
                "order_type": "Stock",
                "target_price": "85",  # 停利觸發價
                "price": "85",  # 停利委託價
                "trigger": "MatchedPrice",
            },
            # 停損：價格跌破 60 時賣出
            "sl": {
                "time_in_force": "ROD",
                "price_type": "Limit",
                "order_type": "Stock",
                "target_price": "60",  # 停損觸發價
                "price": "60",  # 停損委託價
                "trigger": "MatchedPrice",
            },
            "end_date": "20240517",  # 停損停利結束日期
            "intraday": False,
        },
    }

    print("\n停損停利條件單設定：")
    print(f"  股票代碼：2881")
    print(f"  觸發條件：成交價 < 66")
    print(f"  觸發後動作：買入 1000 股，限價 66")
    print(f"  停利設定：價格達到 85 時賣出（獲利 19 元/股）")
    print(f"  停損設定：價格跌破 60 時賣出（停損 6 元/股）")
    print(f"  OCO 機制：停利或停損其一觸發後，另一個自動失效")

    # 執行停損停利條件單（示範用，實際執行請取消註解）
    # result = place_tpsl_condition_order(tpsl_order_data)
    # print(f"\n結果：{result}")

    print("\n停損停利參數驗證：")
    try:
        validated = PlaceConditionOrderArgs(**tpsl_order_data)
        print("✅ 參數驗證通過")
        print(f"  帳戶：{validated.account}")
        print(f"  條件股票：{validated.condition['symbol']}")
        print(f"  停利觸發價：{validated.tpsl['tp']['target_price']}")
        print(f"  停損觸發價：{validated.tpsl['sl']['target_price']}")
    except Exception as e:
        print(f"❌ 參數驗證失敗：{e}")


def demo_daytrade_condition_order():
    """
    示範當沖單一條件單（可含停損停利）

    場景：當 2881 成交價 < 66 時買入 1000 股，
          主單成交後於 13:15 前進行回補；同時設定停利/停損。
    """
    print("\n" + "=" * 60)
    print("示範 4: 當沖條件單（single_condition_day_trade）")
    print("=" * 60)

    account = os.getenv("FUBON_ACCOUNT", "YOUR_ACCOUNT_NUMBER")

    daytrade_order_data = {
        "account": account,
        "stop_sign": "Full",
        "end_time": "130000",  # 父單洗價結束時間
        "condition": {
            "market_type": "Reference",
            "symbol": "2881",
            "trigger": "MatchedPrice",
            "trigger_value": "66",
            "comparison": "LessThan",
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
        "daytrade": {
            "day_trade_end_time": "131500",  # 130100 ~ 132000
            "auto_cancel": True,
            "price": "",
            "price_type": "Market",
        },
        "tpsl": {
            "stop_sign": "Full",
            "tp": {"time_in_force": "ROD", "price_type": "Limit", "order_type": "Stock", "target_price": "85", "price": "85"},
            "sl": {"time_in_force": "ROD", "price_type": "Limit", "order_type": "Stock", "target_price": "60", "price": "60"},
            "end_date": "20240517",
            "intraday": True,
        },
        "fix_session": True,
    }

    print("\n當沖條件單設定：")
    print(f"  股票代碼：2881")
    print(f"  觸發條件：成交價 < 66")
    print(f"  主單：買入 1000 股，限價 66")
    print(f"  回補：於 13:15 前（auto_cancel=true）市價回補")
    print(f"  停利：85，停損：60（OCO）")

    # 實際執行請取消註解
    # result = place_daytrade_condition_order(daytrade_order_data)
    # print(f"\n結果：{result}")

    print("\n當沖條件單參數驗證：")
    try:
        validated = PlaceDayTradeConditionOrderArgs(**daytrade_order_data)
        print("✅ 參數驗證通過")
        print(f"  帳戶：{validated.account}")
        print(f"  結束時間：{validated.end_time}")
        print(f"  回補時間：{validated.daytrade['day_trade_end_time']}")
        print(f"  定盤回補：{validated.fix_session}")
    except Exception as e:
        print(f"❌ 參數驗證失敗：{e}")


def demo_condition_order_scenarios():
    """
    示範多種條件單應用場景
    """
    print("\n" + "=" * 60)
    print("示範 3: 條件單應用場景")
    print("=" * 60)

    scenarios = [
        {
            "name": "突破買入",
            "description": "當股價突破 100 元時買入",
            "condition": {"symbol": "2330", "trigger_value": "100", "comparison": "Greater"},
            "order": {"buy_sell": "Buy", "price": "101"},
        },
        {
            "name": "跌破賣出",
            "description": "當股價跌破 90 元時賣出",
            "condition": {"symbol": "2330", "trigger_value": "90", "comparison": "LessThan"},
            "order": {"buy_sell": "Sell", "price": "89"},
        },
        {
            "name": "價格到達",
            "description": "當股價等於 95 元時買入",
            "condition": {"symbol": "2330", "trigger_value": "95", "comparison": "Equal"},
            "order": {"buy_sell": "Buy", "price": "95"},
        },
    ]

    for scenario in scenarios:
        print(f"\n場景：{scenario['name']}")
        print(f"  說明：{scenario['description']}")
        print(f"  股票：{scenario['condition']['symbol']}")
        print(f"  觸發值：{scenario['condition']['trigger_value']}")
        print(f"  比較：{scenario['condition']['comparison']}")
        print(f"  動作：{scenario['order']['buy_sell']} @ {scenario['order']['price']}")


def main():
    """主程式"""
    print("=" * 60)
    print("富邦證券條件單功能示範")
    print("=" * 60)
    print("\n此腳本示範條件單的各種應用場景")
    print("注意：條件單目前不支援期權商品與現貨商品混用")

    # 示範 1: 單一條件單
    demo_single_condition_order()

    # 示範 2: 停損停利條件單
    demo_tpsl_condition_order()

    # 示範 3: 多條件單
    demo_multi_condition_order()

    # 示範 4: 當沖條件單
    demo_daytrade_condition_order()

    # 示範 5: 多種應用場景
    demo_condition_order_scenarios()

    print("\n" + "=" * 60)
    print("示範完成")
    print("=" * 60)
    print("\n提醒：")
    print("  1. 實際執行前請確認環境變數設定正確")
    print("  2. 替換 YOUR_ACCOUNT_NUMBER 為您的實際帳戶")
    print("  3. 取消相關註解以執行實際下單")
    print("  4. 條件單不支援期權與現貨混用")


if __name__ == "__main__":
    main()
