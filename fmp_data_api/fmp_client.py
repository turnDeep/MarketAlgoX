"""
FMP Compatible Client Library
FMP互換のクライアントライブラリ - 既存のFMPコードと同じ使い方が可能
"""

import os
import requests
from typing import List, Dict, Optional, Any


class FMPClient:
    """
    FMP互換クライアント

    使用方法:
    1. 環境変数で制御:
       FMP_USE_LOCAL=true にすると、ローカルAPIサーバーを使用
       FMP_USE_LOCAL=false または未設定の場合は、公式FMP APIを使用

    2. 直接指定:
       client = FMPClient(api_key="your_key", use_local=True, local_url="http://localhost:8000")

    既存のコードを変更せずに使用可能:
       from fmp_client import FMPClient
       client = FMPClient(api_key=os.getenv("FMP_API_KEY"))
       data = client.get_company_profile("AAPL")
    """

    def __init__(
        self,
        api_key: str,
        use_local: Optional[bool] = None,
        local_url: Optional[str] = None,
        official_url: str = "https://financialmodelingprep.com/api/v3"
    ):
        """
        Args:
            api_key: FMP API Key（ローカル・公式の両方で使用）
            use_local: ローカルAPIを使用するか（Noneの場合は環境変数から判断）
            local_url: ローカルAPIのURL（デフォルト: http://localhost:8000/api/v3）
            official_url: 公式FMP APIのURL
        """
        self.api_key = api_key

        # 環境変数からローカル使用の設定を取得
        if use_local is None:
            use_local_env = os.getenv('FMP_USE_LOCAL', 'false').lower()
            use_local = use_local_env in ['true', '1', 'yes']

        self.use_local = use_local

        # ローカルURLの設定
        if local_url is None:
            local_url = os.getenv('FMP_LOCAL_URL', 'http://fmp_api:8000/api/v3')

        # 使用するベースURLを決定
        self.base_url = local_url if self.use_local else official_url

        print(f"FMPClient initialized: {'LOCAL' if self.use_local else 'OFFICIAL'} - {self.base_url}")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        APIリクエストを実行

        Args:
            endpoint: エンドポイントパス（例: "/profile/AAPL"）
            params: クエリパラメータ

        Returns:
            APIレスポンス（JSON）
        """
        if params is None:
            params = {}

        # APIキーをパラメータに追加
        params['apikey'] = self.api_key

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {url} - {str(e)}")
            return None

    # ==================== FMP互換メソッド ====================

    def get_stock_list(self) -> List[Dict]:
        """
        全銘柄リストを取得

        Returns:
            銘柄リスト
        """
        return self._make_request("/stock/list") or []

    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        企業プロファイルを取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）

        Returns:
            企業プロファイル（辞書形式）または None
        """
        data = self._make_request(f"/profile/{symbol}")

        if data and len(data) > 0:
            return data[0]
        return None

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        リアルタイム株価を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）

        Returns:
            株価データ（辞書形式）または None
        """
        data = self._make_request(f"/quote/{symbol}")

        if data and len(data) > 0:
            return data[0]
        return None

    def get_quote_short(self, symbol: str) -> Optional[Dict]:
        """
        リアルタイム株価を取得（簡易版）

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）

        Returns:
            株価データ（簡易版）または None
        """
        data = self._make_request(f"/quote-short/{symbol}")

        if data and len(data) > 0:
            return data[0]
        return None

    def get_historical_prices(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        timeseries: Optional[int] = None
    ) -> Optional[Dict]:
        """
        過去の株価データを取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            from_date: 開始日（YYYY-MM-DD形式）
            to_date: 終了日（YYYY-MM-DD形式）
            timeseries: 取得する日数

        Returns:
            過去株価データ（辞書形式）または None
            形式: {"symbol": "AAPL", "historical": [...]}
        """
        params = {}

        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if timeseries:
            params['timeseries'] = timeseries

        return self._make_request(f"/historical-price-full/{symbol}", params)

    def get_historical_price_full(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        timeseries: Optional[int] = None
    ) -> Optional[Dict]:
        """
        get_historical_prices のエイリアス（FMPとの互換性のため）
        """
        return self.get_historical_prices(symbol, from_date, to_date, timeseries)

    def get_income_statement(
        self,
        symbol: str,
        period: str = 'quarter',
        limit: int = 8
    ) -> List[Dict]:
        """
        損益計算書を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            period: 期間（'annual' または 'quarter'）
            limit: 取得する件数

        Returns:
            損益計算書のリスト
        """
        params = {'period': period, 'limit': limit}
        return self._make_request(f"/income-statement/{symbol}", params) or []

    def get_balance_sheet(
        self,
        symbol: str,
        period: str = 'quarter',
        limit: int = 8
    ) -> List[Dict]:
        """
        貸借対照表を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            period: 期間（'annual' または 'quarter'）
            limit: 取得する件数

        Returns:
            貸借対照表のリスト
        """
        params = {'period': period, 'limit': limit}
        return self._make_request(f"/balance-sheet-statement/{symbol}", params) or []

    def get_cash_flow_statement(
        self,
        symbol: str,
        period: str = 'quarter',
        limit: int = 8
    ) -> List[Dict]:
        """
        キャッシュフロー計算書を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            period: 期間（'annual' または 'quarter'）
            limit: 取得する件数

        Returns:
            キャッシュフロー計算書のリスト
        """
        params = {'period': period, 'limit': limit}
        return self._make_request(f"/cash-flow-statement/{symbol}", params) or []

    def get_financial_ratios(
        self,
        symbol: str,
        period: str = 'quarter',
        limit: int = 8
    ) -> List[Dict]:
        """
        財務比率を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            period: 期間（'annual' または 'quarter'）
            limit: 取得する件数

        Returns:
            財務比率のリスト
        """
        params = {'period': period, 'limit': limit}
        return self._make_request(f"/ratios/{symbol}", params) or []

    def get_key_metrics(
        self,
        symbol: str,
        period: str = 'quarter',
        limit: int = 8
    ) -> List[Dict]:
        """
        主要指標を取得

        Args:
            symbol: 銘柄シンボル（例: "AAPL"）
            period: 期間（'annual' または 'quarter'）
            limit: 取得する件数

        Returns:
            主要指標のリスト
        """
        params = {'period': period, 'limit': limit}
        return self._make_request(f"/key-metrics/{symbol}", params) or []

    # ==================== ヘルパーメソッド ====================

    def is_using_local(self) -> bool:
        """ローカルAPIを使用しているかを返す"""
        return self.use_local

    def get_base_url(self) -> str:
        """現在使用しているベースURLを返す"""
        return self.base_url

    def switch_to_local(self, local_url: Optional[str] = None):
        """ローカルAPIに切り替え"""
        self.use_local = True
        if local_url:
            self.base_url = local_url
        else:
            self.base_url = os.getenv('FMP_LOCAL_URL', 'http://fmp_api:8000/api/v3')
        print(f"Switched to LOCAL API: {self.base_url}")

    def switch_to_official(self):
        """公式FMP APIに切り替え"""
        self.use_local = False
        self.base_url = "https://financialmodelingprep.com/api/v3"
        print(f"Switched to OFFICIAL API: {self.base_url}")


# ==================== 便利な関数 ====================

def create_client(api_key: Optional[str] = None) -> FMPClient:
    """
    環境変数から設定を読み取ってFMPClientを作成

    環境変数:
        FMP_API_KEY: API Key
        FMP_USE_LOCAL: ローカルAPIを使用するか（true/false）
        FMP_LOCAL_URL: ローカルAPIのURL

    Args:
        api_key: API Key（指定しない場合は環境変数から取得）

    Returns:
        FMPClient インスタンス
    """
    if api_key is None:
        api_key = os.getenv('FMP_API_KEY')

    if not api_key:
        raise ValueError("FMP_API_KEY is required (環境変数またはパラメータで指定してください)")

    return FMPClient(api_key=api_key)


# ==================== 使用例 ====================

if __name__ == '__main__':
    """
    使用例
    """
    import os

    # 方法1: 環境変数から自動設定
    # export FMP_API_KEY="your_key"
    # export FMP_USE_LOCAL="true"
    # client = create_client()

    # 方法2: 直接指定
    client = FMPClient(
        api_key=os.getenv('FMP_API_KEY', 'demo'),
        use_local=True,
        local_url='http://localhost:8000/api/v3'
    )

    # テスト
    print("Testing FMP Client...")
    print(f"Using: {'LOCAL' if client.is_using_local() else 'OFFICIAL'}")
    print(f"Base URL: {client.get_base_url()}")

    # 企業プロファイル取得
    profile = client.get_company_profile('AAPL')
    if profile:
        print(f"\nCompany: {profile.get('companyName')}")
        print(f"Sector: {profile.get('sector')}")
        print(f"Industry: {profile.get('industry')}")

    # 株価取得
    quote = client.get_quote('AAPL')
    if quote:
        print(f"\nPrice: ${quote.get('price')}")
        print(f"Change: {quote.get('change')} ({quote.get('changesPercentage')}%)")
