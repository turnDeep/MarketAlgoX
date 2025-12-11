"""
AI分析モジュール

OpenAI APIを使用してスクリーニング結果を分析
"""

import json
import os
from typing import Dict, List

try:
    from openai import OpenAI
except ImportError:
    print("Warning: openai not installed. Run: pip install openai")
    OpenAI = None


class OpenAIClient:
    """OpenAI APIクライアント"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Args:
            api_key: OpenAI API Key
            model: 使用するモデル (例: gpt-4o, gpt-4-turbo)
        """
        if not OpenAI:
            raise ImportError("openai is not installed")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_content(self, prompt: str, use_search: bool = False) -> str:
        """
        コンテンツ生成

        Args:
            prompt: プロンプト
            use_search: Web検索を使用するか（OpenAIではサポートされていないため無視）

        Returns:
            生成されたテキスト
        """
        try:
            # Web検索はOpenAIのネイティブ機能ではないため、
            # プロンプトで最新情報を求めるよう指示
            if use_search:
                prompt = f"{prompt}\n\n※最新の市場動向や決算情報を考慮して回答してください。"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは米国株式市場の専門アナリストです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""


class ScreenerAnalyzer:
    """スクリーニング結果分析"""

    def __init__(self, openai_api_key: str, model: str = "gpt-4o"):
        """
        Args:
            openai_api_key: OpenAI API Key
            model: 使用するモデル
        """
        self.openai_client = OpenAIClient(openai_api_key, model)

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
            all_tickers_in_screener = screener.get("tickers", [])
            new_tickers = [t for t in all_tickers_in_screener if t.get("is_new", False)]

            if new_tickers:
                top_stock = self.select_top_stock_per_screener(
                    screener_name=screener_name,
                    new_tickers=new_tickers,
                    all_tickers=all_tickers_in_screener,
                    screener_info=screener
                )
                recommended_stocks[screener_name] = top_stock

        return {
            "date": json_data.get("date", ""),
            "recommended_stocks": recommended_stocks
        }

    def select_top_stock_per_screener(
        self,
        screener_name: str,
        new_tickers: List[dict],
        all_tickers: List[dict],
        screener_info: dict
    ) -> dict:
        """
        各スクリーナーでトップ銘柄を選定し、その他の銘柄とトレンドも取得

        Args:
            screener_name: スクリーナー名
            new_tickers: 新規銘柄リスト
            all_tickers: スクリーナーの全銘柄リスト
            screener_info: スクリーナー情報

        Returns:
            {
                "ticker": "AAPL",
                "reason": "Web検索で調査した上昇理由",
                "other_tickers": ["NVDA", "AVGO", "META", ...],
                "trend": "トレンド説明"
            }
        """
        if not new_tickers:
            return {
                "ticker": "",
                "reason": "新規銘柄がありません",
                "other_tickers": [],
                "trend": ""
            }

        # ステップ1: トップ銘柄を選定
        selection_prompt = f"""あなたは米国株式市場の専門アナリストです。

以下のスクリーナーで新規に抽出された銘柄の中から、最も有望な銘柄を1つ選んでください。

【スクリーナー情報】
名称: {screener_name}
条件: {json.dumps(screener_info.get('criteria', {}), ensure_ascii=False)}

【新規抽出銘柄】
{json.dumps([{"ticker": t["ticker"], "price": t.get("price"), "sector": t.get("sector")} for t in new_tickers[:20]], ensure_ascii=False)}

出力形式（JSON）:
{{
  "ticker": "銘柄コード"
}}
"""

        try:
            response_text = self.openai_client.generate_content(selection_prompt)
            json_text = self._extract_json(response_text)
            selected = json.loads(json_text.strip())
            top_ticker = selected.get("ticker", new_tickers[0]["ticker"] if new_tickers else "")
        except Exception as e:
            print(f"Error selecting ticker: {e}")
            top_ticker = new_tickers[0]["ticker"] if new_tickers else ""

        # ステップ2: 銘柄の上昇理由を調査
        reason_prompt = f"""${top_ticker}の株価が最近上昇している理由を、最新のニュースや決算情報から30文字以内で簡潔に説明してください。

例: 「直近の決算で黒字化」「AI事業の好調な業績」「新製品発表で期待」
"""

        try:
            reason = self.openai_client.generate_content(reason_prompt, use_search=True)
            reason = reason.strip().replace('\n', '')[:30]
        except Exception as e:
            print(f"Error getting reason: {e}")
            reason = "市場で注目されている銘柄"

        # ステップ3: その他の銘柄リストを作成（最大10銘柄）
        other_tickers_list = [t["ticker"] for t in all_tickers if t["ticker"] != top_ticker]

        if len(other_tickers_list) > 10:
            # AIに10個選定してもらう
            other_selection_prompt = f"""以下の銘柄リストから、最も有望な10銘柄を選んでください。

銘柄リスト:
{json.dumps(other_tickers_list[:30], ensure_ascii=False)}

出力形式（JSON）:
{{
  "tickers": ["NVDA", "AVGO", "META", ...]
}}
"""
            try:
                response_text = self.openai_client.generate_content(other_selection_prompt)
                json_text = self._extract_json(response_text)
                selected_others = json.loads(json_text.strip())
                other_tickers_list = selected_others.get("tickers", other_tickers_list[:10])
            except Exception as e:
                print(f"Error selecting other tickers: {e}")
                other_tickers_list = other_tickers_list[:10]
        else:
            other_tickers_list = other_tickers_list[:10]

        # ステップ4: トレンド分析（Industry Group）
        industry_dist = {}
        for ticker in all_tickers:
            industry = ticker.get("industry_group", "Unknown")
            industry_dist[industry] = industry_dist.get(industry, 0) + 1

        top_industry = max(industry_dist.items(), key=lambda x: x[1])[0] if industry_dist else "不明"
        trend = f"{top_industry}が強い"[:30]

        return {
            "ticker": top_ticker,
            "reason": reason,
            "other_tickers": other_tickers_list,
            "trend": trend
        }

    def _extract_json(self, text: str) -> str:
        """レスポンステキストからJSONを抽出"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        elif "```" in text:
            return text.split("```")[1].split("```")[0]
        return text

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
            response_text = self.openai_client.generate_content(prompt)
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

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
        print("エラー: OPENAI_API_KEYが設定されていません")
        return

    analyzer = ScreenerAnalyzer(OPENAI_API_KEY, OPENAI_MODEL)

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
