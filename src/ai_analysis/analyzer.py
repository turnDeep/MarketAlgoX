"""
AI分析モジュール

Gemini 3 ProのAPIを使用してスクリーニング結果を分析
"""

import json
import os
from typing import Dict, List

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")
    genai = None


class GeminiClient:
    """Gemini 3 Pro APIクライアント"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Gemini API Key
        """
        if not genai:
            raise ImportError("google-generativeai is not installed")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt: str) -> str:
        """
        コンテンツ生成

        Args:
            prompt: プロンプト

        Returns:
            生成されたテキスト
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return ""


class ScreenerAnalyzer:
    """スクリーニング結果分析"""

    def __init__(self, gemini_api_key: str):
        """
        Args:
            gemini_api_key: Gemini API Key
        """
        self.gemini_client = GeminiClient(gemini_api_key)

    def analyze_screening_results(self, json_file_path: str) -> dict:
        """
        スクリーニング結果を分析

        Args:
            json_file_path: スクリーニング結果JSONファイルパス

        Returns:
            {
                "recommended_stocks": {
                    "スクリーナー名": {
                        "ticker": "AAPL",
                        "reason": "理由..."
                    }
                },
                "industry_trends": "分析結果..."
            }
        """
        # JSONファイルを読み込み
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 各スクリーナーでトップ銘柄を選定
        recommended_stocks = {}
        for screener in json_data.get("screeners", []):
            screener_name = screener["name"]
            new_tickers = [t for t in screener.get("tickers", []) if t.get("is_new", False)]

            if new_tickers:
                top_stock = self.select_top_stock_per_screener(
                    screener_name=screener_name,
                    new_tickers=new_tickers,
                    screener_info=screener
                )
                recommended_stocks[screener_name] = top_stock

        # Industry Group傾向を分析
        all_tickers = []
        for screener in json_data.get("screeners", []):
            all_tickers.extend(screener.get("tickers", []))

        industry_trends = self.analyze_industry_trends(all_tickers)

        return {
            "date": json_data.get("date", ""),
            "recommended_stocks": recommended_stocks,
            "industry_trends": industry_trends
        }

    def select_top_stock_per_screener(
        self,
        screener_name: str,
        new_tickers: List[dict],
        screener_info: dict
    ) -> dict:
        """
        各スクリーナーでトップ銘柄を選定

        Args:
            screener_name: スクリーナー名
            new_tickers: 新規銘柄リスト
            screener_info: スクリーナー情報

        Returns:
            {"ticker": "AAPL", "reason": "理由..."}
        """
        # プロンプトを構築
        prompt = f"""あなたは米国株式市場の専門アナリストです。

以下のスクリーナーで新規に抽出された銘柄の中から、最も有望な銘柄を1つ選び、理由を簡潔に述べてください。

【スクリーナー情報】
名称: {screener_name}
説明: {screener_info.get('description', '')}
条件: {json.dumps(screener_info.get('criteria', {}), ensure_ascii=False, indent=2)}

【新規抽出銘柄】
{json.dumps(new_tickers, ensure_ascii=False, indent=2)}

出力形式（JSON）:
{{
  "ticker": "銘柄コード",
  "reason": "選定理由（100文字以内）"
}}
"""

        try:
            response_text = self.gemini_client.generate_content(prompt)

            # JSONを抽出
            # レスポンステキストから```json と ``` を除去
            json_text = response_text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]

            result = json.loads(json_text.strip())
            return result

        except Exception as e:
            print(f"Error selecting top stock for {screener_name}: {e}")
            # デフォルト: 最初の銘柄を選択
            if new_tickers:
                return {
                    "ticker": new_tickers[0]["ticker"],
                    "reason": "AI分析エラーのため、リストの最初の銘柄を選択しました。"
                }
            return {"ticker": "", "reason": "新規銘柄がありません"}

    def analyze_industry_trends(self, all_tickers: List[dict]) -> str:
        """
        Industry Group傾向を分析

        Args:
            all_tickers: 全銘柄データ

        Returns:
            傾向分析テキスト
        """
        # Industry Groupの分布を集計
        industry_distribution = {}
        for ticker in all_tickers:
            industry = ticker.get("industry_group", "Unknown")
            industry_distribution[industry] = industry_distribution.get(industry, 0) + 1

        # ソート
        sorted_industries = sorted(industry_distribution.items(), key=lambda x: x[1], reverse=True)

        # プロンプトを構築
        prompt = f"""あなたは米国株式市場の専門アナリストです。

以下のIndustry Group分布データを分析し、どのIndustry Groupの銘柄が多いか傾向を述べてください。

【Industry Group分布】
{json.dumps(dict(sorted_industries[:10]), ensure_ascii=False, indent=2)}

【全銘柄データ】
{json.dumps(all_tickers[:50], ensure_ascii=False, indent=2)}

200文字以内で傾向を分析してください。
"""

        try:
            response_text = self.gemini_client.generate_content(prompt)
            return response_text.strip()

        except Exception as e:
            print(f"Error analyzing industry trends: {e}")
            # デフォルトの分析
            if sorted_industries:
                top_3 = sorted_industries[:3]
                return f"上位3つのIndustry Groupは{', '.join([f'{k} ({v}銘柄)' for k, v in top_3])}です。"
            return "Industry Group傾向の分析データが不足しています。"


def main():
    """テスト実行"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("エラー: GEMINI_API_KEYが設定されていません")
        return

    analyzer = ScreenerAnalyzer(GEMINI_API_KEY)

    # テスト用のJSONファイルパス
    json_file = "./data/screener_results/20251211.json"
    if not os.path.exists(json_file):
        print(f"テスト用JSONファイルが見つかりません: {json_file}")
        return

    result = analyzer.analyze_screening_results(json_file)
    print("\n=== AI分析結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
