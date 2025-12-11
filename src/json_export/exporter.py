"""
JSON出力モジュール

スクリーニング結果をJSON形式で出力
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from ibd_database import IBDDatabase
from src.screeners.screener_names import get_screener_info


class JSONExporter:
    """JSON出力管理"""

    def __init__(self, db_path: str = './data/ibd_data.db', output_dir: str = "./data/screener_results"):
        """
        Args:
            db_path: データベースファイルパス
            output_dir: JSON出力ディレクトリ
        """
        self.db = IBDDatabase(db_path)
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def export_screening_results(
        self,
        date: str,
        screener_results: Dict[str, List[str]],
        previous_results: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        スクリーニング結果をJSON出力

        Args:
            date: 日付 (YYYYMMDD形式)
            screener_results: {スクリーナー名: [銘柄リスト]}
            previous_results: 前日の結果 (新規銘柄特定用)

        Returns:
            JSONファイルパス
        """
        # 前日結果との差分を計算
        new_tickers_per_screener = {}
        if previous_results:
            new_tickers_per_screener = self.identify_new_tickers(screener_results, previous_results)
        else:
            # 前日結果がない場合、すべて新規として扱う
            new_tickers_per_screener = {name: tickers for name, tickers in screener_results.items()}

        # JSON構造を構築
        json_data = {
            "date": datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d"),
            "market_date": self.db.get_latest_price_date() or datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d"),
            "screeners": []
        }

        all_tickers = set()
        industry_distribution = {}

        # 各スクリーナーの結果を処理
        for screener_name, tickers in screener_results.items():
            screener_info = get_screener_info(screener_name)
            new_tickers = new_tickers_per_screener.get(screener_name, [])

            screener_data = {
                "name": screener_name,
                "english_name": screener_info["english_name"],
                "description": screener_info["description"],
                "criteria": screener_info["criteria"],
                "total_count": len(tickers),
                "new_count": len(new_tickers),
                "tickers": []
            }

            # 各銘柄の詳細データを取得
            for ticker in tickers:
                ticker_data = self.get_ticker_details(ticker)
                if ticker_data:
                    ticker_data["is_new"] = ticker in new_tickers
                    screener_data["tickers"].append(ticker_data)

                    # 集計用
                    all_tickers.add(ticker)
                    industry = ticker_data.get("industry_group", "Unknown")
                    industry_distribution[industry] = industry_distribution.get(industry, 0) + 1

            json_data["screeners"].append(screener_data)

        # サマリー追加
        json_data["summary"] = {
            "total_screeners": len(screener_results),
            "total_unique_tickers": len(all_tickers),
            "total_new_tickers": sum(len(v) for v in new_tickers_per_screener.values()),
            "industry_distribution": dict(sorted(industry_distribution.items(), key=lambda x: x[1], reverse=True))
        }

        # JSONファイルに書き出し
        json_file_path = os.path.join(self.output_dir, f"{date}.json")
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"JSON出力完了: {json_file_path}")
        return json_file_path

    def identify_new_tickers(
        self,
        today_results: Dict[str, List[str]],
        yesterday_results: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """新規銘柄を特定"""
        new_tickers = {}

        for screener_name, today_tickers in today_results.items():
            yesterday_tickers = set(yesterday_results.get(screener_name, []))
            new = [t for t in today_tickers if t not in yesterday_tickers]
            new_tickers[screener_name] = new

        return new_tickers

    def get_ticker_details(self, ticker: str) -> Optional[dict]:
        """銘柄の詳細データを取得"""
        try:
            # 企業プロファイルを取得
            profile = self.db.get_company_profile(ticker)
            if not profile:
                return None

            # レーティングを取得
            rating = self.db.get_rating(ticker)

            # 価格データを取得
            prices_df = self.db.get_price_history(ticker, days=2)
            if prices_df is None or len(prices_df) < 1:
                return None

            latest_price = prices_df.iloc[-1]
            change_1d_pct = 0
            if len(prices_df) >= 2:
                prev_close = prices_df.iloc[-2]['close']
                if prev_close != 0:
                    change_1d_pct = ((latest_price['close'] - prev_close) / prev_close * 100)

            ticker_data = {
                "ticker": ticker,
                "company_name": profile.get('company_name', ''),
                "price": round(latest_price['close'], 2),
                "change_1d_pct": round(change_1d_pct, 2),
                "volume": int(latest_price['volume']),
                "market_cap": profile.get('market_cap'),
                "sector": profile.get('sector', ''),
                "industry_group": profile.get('industry', ''),
                "ratings": {}
            }

            # レーティング追加
            if rating:
                ticker_data["ratings"] = {
                    "rs_rating": rating.get('rs_rating'),
                    "eps_rating": rating.get('eps_rating'),
                    "comp_rating": rating.get('comp_rating'),
                    "ad_rating": rating.get('ad_rating')
                }

            return ticker_data

        except Exception as e:
            print(f"Error getting details for {ticker}: {e}")
            return None

    def load_previous_results(self, date: str) -> Optional[Dict[str, List[str]]]:
        """前日のJSON結果を読み込み"""
        try:
            # 前日の日付を計算 (簡易版: 1日前)
            from datetime import datetime, timedelta
            dt = datetime.strptime(date, "%Y%m%d")
            prev_dt = dt - timedelta(days=1)
            prev_date = prev_dt.strftime("%Y%m%d")

            prev_json_path = os.path.join(self.output_dir, f"{prev_date}.json")
            if not os.path.exists(prev_json_path):
                return None

            with open(prev_json_path, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)

            # スクリーナー名: [銘柄リスト] の形式に変換
            prev_results = {}
            for screener in prev_data.get("screeners", []):
                screener_name = screener["name"]
                tickers = [t["ticker"] for t in screener.get("tickers", [])]
                prev_results[screener_name] = tickers

            return prev_results

        except Exception as e:
            print(f"Error loading previous results: {e}")
            return None

    def close(self):
        """リソースをクリーンアップ"""
        self.db.close()
