"""
FMP Data API - 使用例
"""

import os
from fmp_client import FMPClient, create_client


def example_1_basic_usage():
    """基本的な使用例"""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)

    # 環境変数から自動設定
    client = create_client()

    # 企業プロファイル取得
    print("\n1. Company Profile for AAPL:")
    profile = client.get_company_profile('AAPL')
    if profile:
        print(f"  Company: {profile.get('companyName')}")
        print(f"  Sector: {profile.get('sector')}")
        print(f"  Industry: {profile.get('industry')}")
        print(f"  Description: {profile.get('description')[:100]}...")

    # リアルタイム株価取得
    print("\n2. Real-time Quote for AAPL:")
    quote = client.get_quote('AAPL')
    if quote:
        print(f"  Price: ${quote.get('price')}")
        print(f"  Change: {quote.get('change')} ({quote.get('changesPercentage')}%)")
        print(f"  Volume: {quote.get('volume'):,}")

    # 過去の株価データ取得
    print("\n3. Historical Prices for AAPL (last 5 days):")
    historical = client.get_historical_prices('AAPL', timeseries=5)
    if historical and 'historical' in historical:
        for price in historical['historical'][:5]:
            print(f"  {price.get('date')}: ${price.get('close')} (Vol: {price.get('volume'):,})")


def example_2_switch_api():
    """APIの切り替え例"""
    print("\n" + "=" * 80)
    print("Example 2: Switching Between Official and Local API")
    print("=" * 80)

    client = FMPClient(
        api_key=os.getenv('FMP_API_KEY', 'demo'),
        use_local=False  # 最初は公式APIを使用
    )

    print(f"\n1. Using: {'LOCAL' if client.is_using_local() else 'OFFICIAL'} API")
    print(f"   Base URL: {client.get_base_url()}")

    # 公式APIでデータ取得
    quote1 = client.get_quote('MSFT')
    if quote1:
        print(f"   MSFT Price (Official): ${quote1.get('price')}")

    # ローカルAPIに切り替え
    client.switch_to_local('http://localhost:8000/api/v3')
    print(f"\n2. Using: {'LOCAL' if client.is_using_local() else 'OFFICIAL'} API")
    print(f"   Base URL: {client.get_base_url()}")

    # ローカルAPIでデータ取得
    quote2 = client.get_quote('MSFT')
    if quote2:
        print(f"   MSFT Price (Local): ${quote2.get('price')}")

    # 公式APIに戻す
    client.switch_to_official()
    print(f"\n3. Using: {'LOCAL' if client.is_using_local() else 'OFFICIAL'} API")
    print(f"   Base URL: {client.get_base_url()}")


def example_3_financial_statements():
    """財務諸表の取得例"""
    print("\n" + "=" * 80)
    print("Example 3: Financial Statements")
    print("=" * 80)

    client = create_client()

    # 損益計算書
    print("\n1. Income Statement for AAPL (last 4 quarters):")
    income_statements = client.get_income_statement('AAPL', period='quarter', limit=4)
    if income_statements:
        for statement in income_statements[:4]:
            date = statement.get('date')
            revenue = statement.get('revenue', 0)
            net_income = statement.get('netIncome', 0)
            eps = statement.get('eps', 0)
            print(f"  {date}: Revenue=${revenue/1e9:.2f}B, Net Income=${net_income/1e9:.2f}B, EPS=${eps:.2f}")

    # 貸借対照表
    print("\n2. Balance Sheet for AAPL (last 2 years):")
    balance_sheets = client.get_balance_sheet('AAPL', period='annual', limit=2)
    if balance_sheets:
        for sheet in balance_sheets[:2]:
            date = sheet.get('date')
            total_assets = sheet.get('totalAssets', 0)
            total_liabilities = sheet.get('totalLiabilities', 0)
            total_equity = sheet.get('totalStockholdersEquity', 0)
            print(f"  {date}:")
            print(f"    Total Assets: ${total_assets/1e9:.2f}B")
            print(f"    Total Liabilities: ${total_liabilities/1e9:.2f}B")
            print(f"    Total Equity: ${total_equity/1e9:.2f}B")


def example_4_batch_processing():
    """複数銘柄の一括処理例"""
    print("\n" + "=" * 80)
    print("Example 4: Batch Processing Multiple Symbols")
    print("=" * 80)

    client = create_client()

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

    print(f"\nFetching quotes for {len(symbols)} symbols:")
    for symbol in symbols:
        quote = client.get_quote(symbol)
        if quote:
            price = quote.get('price', 0)
            change_pct = quote.get('changesPercentage', 0)
            print(f"  {symbol:6s}: ${price:8.2f} ({change_pct:+6.2f}%)")


def example_5_env_controlled():
    """環境変数で完全制御する例"""
    print("\n" + "=" * 80)
    print("Example 5: Environment Variable Controlled")
    print("=" * 80)

    # .envファイルまたは環境変数に以下を設定：
    # FMP_API_KEY=your_api_key
    # FMP_USE_LOCAL=true
    # FMP_LOCAL_URL=http://fmp_api:8000/api/v3

    print("\nEnvironment Variables:")
    print(f"  FMP_API_KEY: {os.getenv('FMP_API_KEY', 'NOT SET')[:20]}...")
    print(f"  FMP_USE_LOCAL: {os.getenv('FMP_USE_LOCAL', 'NOT SET')}")
    print(f"  FMP_LOCAL_URL: {os.getenv('FMP_LOCAL_URL', 'NOT SET')}")

    # 環境変数から自動設定
    client = create_client()

    print(f"\nClient Configuration:")
    print(f"  Using: {'LOCAL' if client.is_using_local() else 'OFFICIAL'} API")
    print(f"  Base URL: {client.get_base_url()}")

    # データ取得（どちらのAPIを使用しているか気にせず使える）
    quote = client.get_quote('AAPL')
    if quote:
        print(f"\nAAPL Quote:")
        print(f"  Price: ${quote.get('price')}")
        print(f"  Source: {'Local Database' if client.is_using_local() else 'FMP Official API'}")


def main():
    """すべての例を実行"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "FMP Data API - Usage Examples" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Example 1: Basic Usage
        example_1_basic_usage()

        # Example 2: Switching APIs
        example_2_switch_api()

        # Example 3: Financial Statements
        example_3_financial_statements()

        # Example 4: Batch Processing
        example_4_batch_processing()

        # Example 5: Environment Controlled
        example_5_env_controlled()

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
