"""
FMP Data API - Data Fetcher Module
FMP APIから全米国株のデータを取得してデータベースに保存
"""

import os
import time
import requests
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from database import FMPDatabase


class RateLimiter:
    """APIレート制限を管理するクラス"""

    def __init__(self, max_calls_per_minute: int = 750):
        self.max_calls_per_minute = max_calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        """必要に応じて待機"""
        now = time.time()
        # 1分以内のコールをフィルタ
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]

        if len(self.calls) >= self.max_calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.calls = []

        self.calls.append(now)


class FMPDataFetcher:
    """FMP APIからデータを取得してデータベースに保存するクラス"""

    def __init__(self, api_key: str, db_path: str = './data/fmp_data.db',
                 rate_limit: int = 750, max_workers: int = 10):
        """
        Args:
            api_key: FMP API Key
            db_path: データベースファイルのパス
            rate_limit: 1分あたりの最大リクエスト数
            max_workers: 並列処理のワーカー数
        """
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.db = FMPDatabase(db_path)
        self.rate_limiter = RateLimiter(max_calls_per_minute=rate_limit)
        self.max_workers = max_workers

    def _fetch_with_rate_limit(self, url: str, params: dict = None) -> Optional[dict]:
        """レート制限を考慮したAPIリクエスト"""
        self.rate_limiter.wait_if_needed()

        if params is None:
            params = {}
        params['apikey'] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {url} - {str(e)}")
            return None

    # ==================== データ取得メソッド ====================

    def fetch_stock_list(self) -> List[Dict]:
        """全銘柄リストを取得"""
        print("Fetching stock list...")
        url = f"{self.base_url}/stock/list"
        data = self._fetch_with_rate_limit(url)

        if data:
            print(f"Found {len(data)} stocks")
            return data
        return []

    def fetch_us_stocks_only(self) -> List[Dict]:
        """米国株のみをフィルタリング"""
        all_stocks = self.fetch_stock_list()

        us_exchanges = ['NYSE', 'NASDAQ', 'AMEX', 'NYSE ARCA', 'BATS']
        us_stocks = [
            stock for stock in all_stocks
            if stock.get('exchangeShortName') in us_exchanges
            and stock.get('type') == 'stock'
        ]

        print(f"Filtered to {len(us_stocks)} US stocks")
        return us_stocks

    def fetch_company_profile(self, symbol: str) -> Optional[Dict]:
        """企業プロファイルを取得"""
        url = f"{self.base_url}/profile/{symbol}"
        data = self._fetch_with_rate_limit(url)

        if data and len(data) > 0:
            return data[0]
        return None

    def fetch_historical_prices(self, symbol: str, days: int = 1000) -> List[Dict]:
        """過去の株価データを取得"""
        url = f"{self.base_url}/historical-price-full/{symbol}"
        params = {'timeseries': days}

        data = self._fetch_with_rate_limit(url, params)

        if data and 'historical' in data:
            # シンボルを各データに追加
            for item in data['historical']:
                item['symbol'] = symbol
            return data['historical']
        return []

    def fetch_realtime_quote(self, symbol: str) -> Optional[Dict]:
        """リアルタイム株価を取得"""
        url = f"{self.base_url}/quote/{symbol}"
        data = self._fetch_with_rate_limit(url)

        if data and len(data) > 0:
            return data[0]
        return None

    def fetch_income_statement(self, symbol: str, period: str = 'quarter', limit: int = 40) -> List[Dict]:
        """損益計算書を取得"""
        url = f"{self.base_url}/income-statement/{symbol}"
        params = {'period': period, 'limit': limit}
        data = self._fetch_with_rate_limit(url, params)

        if data:
            # シンボルを各データに追加
            for item in data:
                item['symbol'] = symbol
            return data
        return []

    def fetch_balance_sheet(self, symbol: str, period: str = 'quarter', limit: int = 40) -> List[Dict]:
        """貸借対照表を取得"""
        url = f"{self.base_url}/balance-sheet-statement/{symbol}"
        params = {'period': period, 'limit': limit}
        data = self._fetch_with_rate_limit(url, params)

        if data:
            for item in data:
                item['symbol'] = symbol
            return data
        return []

    def fetch_cash_flow_statement(self, symbol: str, period: str = 'quarter', limit: int = 40) -> List[Dict]:
        """キャッシュフロー計算書を取得"""
        url = f"{self.base_url}/cash-flow-statement/{symbol}"
        params = {'period': period, 'limit': limit}
        data = self._fetch_with_rate_limit(url, params)

        if data:
            for item in data:
                item['symbol'] = symbol
            return data
        return []

    def fetch_financial_ratios(self, symbol: str, period: str = 'quarter', limit: int = 40) -> List[Dict]:
        """財務比率を取得"""
        url = f"{self.base_url}/ratios/{symbol}"
        params = {'period': period, 'limit': limit}
        data = self._fetch_with_rate_limit(url, params)

        if data:
            for item in data:
                item['symbol'] = symbol
            return data
        return []

    def fetch_key_metrics(self, symbol: str, period: str = 'quarter', limit: int = 40) -> List[Dict]:
        """主要指標を取得"""
        url = f"{self.base_url}/key-metrics/{symbol}"
        params = {'period': period, 'limit': limit}
        data = self._fetch_with_rate_limit(url, params)

        if data:
            for item in data:
                item['symbol'] = symbol
            return data
        return []

    # ==================== データベース保存メソッド ====================

    def save_stock_list(self, stocks: List[Dict]):
        """銘柄リストをデータベースに保存"""
        print(f"Saving {len(stocks)} stocks to database...")

        for stock in stocks:
            self.db.upsert_stock(stock)

        print("Stock list saved successfully")

    def save_company_profile(self, symbol: str, profile_data: Dict):
        """企業プロファイルをデータベースに保存"""
        if profile_data:
            self.db.upsert_company_profile(profile_data)

    def save_historical_prices(self, prices: List[Dict]):
        """株価データをデータベースに保存"""
        for price in prices:
            self.db.insert_daily_price(price)

    def save_income_statements(self, statements: List[Dict]):
        """損益計算書をデータベースに保存"""
        for statement in statements:
            self.db.insert_income_statement(statement)

    # ==================== 一括処理メソッド ====================

    def process_single_stock(self, symbol: str, fetch_historical: bool = True,
                           fetch_financials: bool = True):
        """単一銘柄のデータを全て取得して保存"""
        print(f"Processing {symbol}...")

        try:
            # 1. 企業プロファイル
            profile = self.fetch_company_profile(symbol)
            if profile:
                self.save_company_profile(symbol, profile)

            # 2. リアルタイム株価
            quote = self.fetch_realtime_quote(symbol)
            if quote:
                self.db.upsert_realtime_quote(quote)

            # 3. 過去の株価データ（オプション）
            if fetch_historical:
                prices = self.fetch_historical_prices(symbol, days=1000)
                if prices:
                    self.save_historical_prices(prices)

            # 4. 財務データ（オプション）
            if fetch_financials:
                # 損益計算書
                income_statements = self.fetch_income_statement(symbol, period='quarter', limit=40)
                if income_statements:
                    self.save_income_statements(income_statements)

                # 貸借対照表
                balance_sheets = self.fetch_balance_sheet(symbol, period='quarter', limit=40)
                # TODO: データベース保存メソッドを実装

                # キャッシュフロー
                cash_flows = self.fetch_cash_flow_statement(symbol, period='quarter', limit=40)
                # TODO: データベース保存メソッドを実装

            print(f"✓ {symbol} completed")
            return True

        except Exception as e:
            print(f"✗ {symbol} failed: {str(e)}")
            return False

    def fetch_all_us_stocks(self, fetch_historical: bool = True,
                          fetch_financials: bool = True,
                          limit: Optional[int] = None):
        """全米国株のデータを取得"""
        print("=" * 80)
        print("FMP Data Fetcher - Fetching All US Stocks Data")
        print("=" * 80)

        # 1. 銘柄リストを取得して保存
        us_stocks = self.fetch_us_stocks_only()

        if limit:
            us_stocks = us_stocks[:limit]
            print(f"Limited to {limit} stocks for testing")

        self.save_stock_list(us_stocks)

        # 2. 各銘柄のデータを並列取得
        symbols = [stock['symbol'] for stock in us_stocks]
        total = len(symbols)
        completed = 0
        failed = 0

        print(f"\nProcessing {total} stocks with {self.max_workers} workers...")
        print(f"Fetch historical: {fetch_historical}, Fetch financials: {fetch_financials}")
        print("-" * 80)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.process_single_stock,
                    symbol,
                    fetch_historical,
                    fetch_financials
                ): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    success = future.result()
                    if success:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"Exception for {symbol}: {str(e)}")
                    failed += 1

                # 進捗表示
                progress = ((completed + failed) / total) * 100
                print(f"Progress: {completed + failed}/{total} ({progress:.1f}%) - "
                      f"Success: {completed}, Failed: {failed}")

        print("=" * 80)
        print(f"Completed! Total: {total}, Success: {completed}, Failed: {failed}")
        print("=" * 80)

    def update_realtime_quotes(self, symbols: Optional[List[str]] = None):
        """リアルタイム株価を更新"""
        if symbols is None:
            symbols = self.db.get_all_symbols()

        print(f"Updating realtime quotes for {len(symbols)} symbols...")

        completed = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.fetch_realtime_quote, symbol): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    quote = future.result()
                    if quote:
                        self.db.upsert_realtime_quote(quote)
                        completed += 1

                    if completed % 100 == 0:
                        print(f"Updated {completed}/{len(symbols)} quotes...")

                except Exception as e:
                    print(f"Failed to update {symbol}: {str(e)}")

        print(f"Completed! Updated {completed} quotes")

    def close(self):
        """リソースのクリーンアップ"""
        self.db.close()


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description='FMP Data Fetcher')
    parser.add_argument('--api-key', required=True, help='FMP API Key')
    parser.add_argument('--db-path', default='./data/fmp_data.db', help='Database file path')
    parser.add_argument('--rate-limit', type=int, default=750, help='API rate limit per minute')
    parser.add_argument('--max-workers', type=int, default=10, help='Max parallel workers')
    parser.add_argument('--limit', type=int, help='Limit number of stocks (for testing)')
    parser.add_argument('--no-historical', action='store_true', help='Skip historical prices')
    parser.add_argument('--no-financials', action='store_true', help='Skip financial statements')
    parser.add_argument('--update-quotes-only', action='store_true',
                       help='Only update realtime quotes')

    args = parser.parse_args()

    fetcher = FMPDataFetcher(
        api_key=args.api_key,
        db_path=args.db_path,
        rate_limit=args.rate_limit,
        max_workers=args.max_workers
    )

    try:
        if args.update_quotes_only:
            fetcher.update_realtime_quotes()
        else:
            fetcher.fetch_all_us_stocks(
                fetch_historical=not args.no_historical,
                fetch_financials=not args.no_financials,
                limit=args.limit
            )
    finally:
        fetcher.close()


if __name__ == '__main__':
    main()
