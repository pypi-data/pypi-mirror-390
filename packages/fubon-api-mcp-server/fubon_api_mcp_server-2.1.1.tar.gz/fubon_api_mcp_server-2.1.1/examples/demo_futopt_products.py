#!/usr/bin/env python3
"""
Demo: 呼叫富邦期貨/選擇權 intraday/products 取得契約清單

環境變數（推薦使用 .env 設定）：
- FUBON_USERNAME
- FUBON_PASSWORD
- FUBON_PFX_PATH
- FUBON_PFX_PASSWORD (可選)

執行範例：
  python examples/demo_futopt_products.py --type FUTURE --exchange TAIFEX --session REGULAR --contractType E

參數說明：
- type: FUTURE | OPTION
- exchange: TAIFEX
- session: REGULAR | AFTERHOURS
- contractType: I|R|B|C|S|E（指數/利率/債券/商品/股票/匯率）
- status: N|P|U（正常/暫停交易/即將上市）
"""

import os
import sys
import argparse
from typing import Any, Dict

from dotenv import load_dotenv


def get_env(name: str, required: bool = True) -> str:
    val = os.getenv(name)
    if required and not val:
        print(f"缺少必要環境變數: {name}", file=sys.stderr)
        sys.exit(1)
    return val or ""


def print_summary(resp: Dict[str, Any]) -> None:
    if not isinstance(resp, dict):
        print(resp)
        return

    t = resp.get("type")
    ex = resp.get("exchange")
    sess = resp.get("session")
    ctype = resp.get("contractType")
    status = resp.get("status")
    data = resp.get("data", [])

    print(f"查詢條件: type={t}, exchange={ex}, session={sess}, contractType={ctype}, status={status}")
    print(f"取得 {len(data)} 筆資料")
    for i, item in enumerate(data[:10], start=1):
        # 常見欄位示例
        print(
            f"{i:>2}. symbol={item.get('symbol')} name={item.get('name')} type={item.get('type')} "
            f"contractType={item.get('contractType')} statusCode={item.get('statusCode')} "
            f"contractSize={item.get('contractSize')} tradingCurrency={item.get('tradingCurrency')}"
        )


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Fubon intraday/products demo")
    parser.add_argument("--type", default="FUTURE", choices=["FUTURE", "OPTION"], help="商品類型")
    parser.add_argument("--exchange", default="TAIFEX", help="交易所，預設 TAIFEX")
    parser.add_argument("--session", default="REGULAR", choices=["REGULAR", "AFTERHOURS"], help="交易時段")
    parser.add_argument("--contractType", default=None, help="契約類別 I/R/B/C/S/E")
    parser.add_argument("--status", default="N", help="契約狀態 N/P/U")
    args = parser.parse_args()

    username = get_env("FUBON_USERNAME")
    password = get_env("FUBON_PASSWORD")
    pfx_path = get_env("FUBON_PFX_PATH")
    pfx_password = get_env("FUBON_PFX_PASSWORD", required=False)

    # 延遲載入，避免未安裝套件時阻擋說明輸出
    from fubon_neo.sdk import FubonSDK  # type: ignore
    from fubon_neo.fugle_marketdata.rest.base_rest import FugleAPIError  # type: ignore

    sdk = FubonSDK()

    print("登入中...")
    accounts = sdk.login(username, password, pfx_path, pfx_password)
    if not getattr(accounts, "is_success", False):
        print("登入失敗，請確認帳密與憑證設定", file=sys.stderr)
        sys.exit(1)

    print("初始化行情連線...")
    sdk.init_realtime()

    restfutopt = sdk.marketdata.rest_client.futopt

    try:
        print("呼叫 intraday/products 中...")
        resp = restfutopt.intraday.products(
            type=args.type,
            exchange=args.exchange,
            session=args.session,
            contractType=args.contractType,
            status=args.status,
        )
        # SDK 該端點回傳 dict（包含 data），直接印出摘要
        print_summary(resp)
    except FugleAPIError as e:
        print(f"Error: {e}")
        print("------------")
        print(f"Status Code: {getattr(e, 'status_code', None)}")
        print(f"Response Text: {getattr(e, 'response_text', None)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
