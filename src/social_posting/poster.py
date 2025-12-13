"""
X (Twitter) 投稿モジュール

AI分析結果をX (Twitter)に投稿
"""

import os
from typing import Dict, List

try:
    import tweepy
except ImportError:
    print("Warning: tweepy not installed. Run: pip install tweepy")
    tweepy = None


class XClient:
    """X (Twitter) APIクライアント"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """
        Args:
            api_key: X API Key (Consumer Key)
            api_secret: X API Secret (Consumer Secret)
            access_token: X Access Token
            access_token_secret: X Access Token Secret
        """
        if not tweepy:
            raise ImportError("tweepy is not installed")

        # OAuth 1.0a認証
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

        # Client for v2 API
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

    def upload_media(self, media_path: str) -> str:
        """
        メディアファイルをアップロード

        Args:
            media_path: メディアファイルのパス

        Returns:
            media_id（アップロード失敗時はNone）
        """
        try:
            if not os.path.exists(media_path):
                print(f"Media file not found: {media_path}")
                return None

            # API v1.1を使用してメディアをアップロード
            media = self.api.media_upload(media_path)
            print(f"Media uploaded successfully: {media.media_id}")
            return str(media.media_id)

        except Exception as e:
            print(f"Error uploading media: {e}")
            if "403 Forbidden" in str(e):
                print("ヒント: X Developer PortalでAppの権限が'Read and Write'になっているか確認してください。")
            return None

    def post_tweet(self, text: str, media_ids: List[str] = None) -> dict:
        """
        ツイートを投稿

        Args:
            text: ツイート本文
            media_ids: 添付するメディアIDのリスト（最大4つ）

        Returns:
            投稿結果
        """
        try:
            # メディアIDがある場合は添付
            kwargs = {"text": text}
            if media_ids:
                kwargs["media_ids"] = media_ids[:4]  # 最大4つまで

            response = self.client.create_tweet(**kwargs)
            return {
                "success": True,
                "tweet_id": response.data['id'] if response.data else None,
                "text": text,
                "media_count": len(media_ids) if media_ids else 0
            }
        except Exception as e:
            print(f"Error posting tweet: {e}")
            if "403 Forbidden" in str(e):
                print("ヒント: X Developer PortalでAppの権限が'Read and Write'になっているか確認してください。")
                print("また、Access Tokenを再生成する必要があるかもしれません。")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }

    def post_thread(self, texts: List[str]) -> List[dict]:
        """
        スレッドを投稿

        Args:
            texts: ツイート本文のリスト

        Returns:
            投稿結果のリスト
        """
        results = []
        previous_tweet_id = None

        for text in texts:
            try:
                response = self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=previous_tweet_id
                )
                result = {
                    "success": True,
                    "tweet_id": response.data['id'] if response.data else None,
                    "text": text
                }
                results.append(result)

                if response.data:
                    previous_tweet_id = response.data['id']

            except Exception as e:
                print(f"Error posting tweet in thread: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "text": text
                })
                break  # エラーが発生したらスレッド投稿を中止

        return results


class TweetFormatter:
    """投稿テキスト整形"""

    # 日本語は140文字、英語は280文字
    MAX_TWEET_LENGTH_JP = 140
    MAX_TWEET_LENGTH_EN = 280

    @staticmethod
    def format_analysis_result(analysis_result: dict, date: str) -> List[str]:
        """
        分析結果を投稿用に整形（各スクリーナーごとに独立したツイート）

        フォーマット:
        【スクリーナー名】
        💡 $TICKER
        理由

        その他
        $NVDA $AVGO $META

        傾向
        AI需要によるIndustry Groupが強い

        Args:
            analysis_result: AI分析結果
            date: 日付 (YYYY-MM-DD形式)

        Returns:
            投稿テキストのリスト（各スクリーナーごとに1ツイート）
        """
        tweets = []

        # 各スクリーナーごとに独立したツイートを作成
        recommended_stocks = analysis_result.get("recommended_stocks", {})
        if recommended_stocks:
            for screener_name, stock_info in recommended_stocks.items():
                ticker = stock_info.get("ticker", "")
                reason = stock_info.get("reason", "")
                other_tickers = stock_info.get("other_tickers", [])
                trend = stock_info.get("trend", "")

                # 基本フォーマット
                tweet = f"【{screener_name}】\n"
                tweet += f"💡 ${ticker}\n"
                tweet += f"{reason}\n"
                tweet += f"\n"

                # その他の銘柄（最大10個）
                if other_tickers:
                    tweet += f"その他\n"
                    other_str = " ".join([f"${t}" for t in other_tickers[:10]])
                    tweet += f"{other_str}\n"
                    tweet += f"\n"

                # 傾向
                if trend:
                    tweet += f"傾向\n"
                    tweet += f"{trend}"

                # 140字を超える場合は調整
                if len(tweet) > TweetFormatter.MAX_TWEET_LENGTH_JP:
                    # 優先度: スクリーナー名 > 銘柄 > 理由 > その他 > 傾向
                    # その他の銘柄数を減らす
                    for max_other in [7, 5, 3, 1, 0]:
                        tweet = f"【{screener_name}】\n"
                        tweet += f"💡 ${ticker}\n"
                        tweet += f"{reason}\n"
                        tweet += f"\n"

                        if max_other > 0 and other_tickers:
                            tweet += f"その他\n"
                            other_str = " ".join([f"${t}" for t in other_tickers[:max_other]])
                            tweet += f"{other_str}\n"
                            tweet += f"\n"

                        if trend:
                            tweet += f"傾向\n"
                            tweet += f"{trend}"

                        if len(tweet) <= TweetFormatter.MAX_TWEET_LENGTH_JP:
                            break

                    # まだ超える場合は理由を短縮
                    if len(tweet) > TweetFormatter.MAX_TWEET_LENGTH_JP:
                        base_len = len(f"【{screener_name}】\n💡 ${ticker}\n\n\n傾向\n{trend}")
                        max_reason_len = TweetFormatter.MAX_TWEET_LENGTH_JP - base_len - 5

                        if max_reason_len > 0:
                            reason_short = reason[:max_reason_len] + "..."
                            tweet = f"【{screener_name}】\n"
                            tweet += f"💡 ${ticker}\n"
                            tweet += f"{reason_short}\n"
                            tweet += f"\n"
                            tweet += f"傾向\n"
                            tweet += f"{trend}"

                tweets.append(tweet)

        return tweets

    @staticmethod
    def split_long_text(text: str, max_length: int = None) -> List[str]:
        """
        長文を指定文字数以内に分割

        Args:
            text: 分割するテキスト
            max_length: 最大文字数（デフォルト: 140）

        Returns:
            分割されたテキストのリスト
        """
        if max_length is None:
            max_length = TweetFormatter.MAX_TWEET_LENGTH_JP

        if len(text) <= max_length:
            return [text]

        parts = []
        current_part = ""

        sentences = text.split("\n")
        for sentence in sentences:
            if len(current_part) + len(sentence) + 1 <= max_length:
                current_part += sentence + "\n"
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = sentence + "\n"

        if current_part:
            parts.append(current_part.strip())

        return parts


class XPoster:
    """X投稿管理"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """
        Args:
            api_key: X API Key
            api_secret: X API Secret
            access_token: X Access Token
            access_token_secret: X Access Token Secret
        """
        self.client = XClient(api_key, api_secret, access_token, access_token_secret)
        self.formatter = TweetFormatter()

    def post_analysis_result(self, analysis_result: dict) -> List[dict]:
        """
        AI分析結果を投稿（各スクリーナーごとに独立したツイート）

        Args:
            analysis_result: AI分析結果（チャートパスを含む）

        Returns:
            投稿結果のリスト
        """
        date = analysis_result.get("date", "")
        tweets = self.formatter.format_analysis_result(analysis_result, date)
        recommended_stocks = analysis_result.get("recommended_stocks", {})

        print(f"\n=== X投稿開始 ({len(tweets)}ツイート - 各スクリーナーごとに独立投稿) ===")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n[{i}/{len(tweets)}]")
            print(tweet)
            print(f"文字数: {len(tweet)}")

        # 各ツイートを独立して投稿（スレッドではない）
        results = []
        import time

        screener_names = list(recommended_stocks.keys())

        for i, tweet in enumerate(tweets, 1):
            print(f"\n投稿中 [{i}/{len(tweets)}]...")

            # チャート画像を添付（ある場合）
            media_ids = []
            if i <= len(screener_names):
                screener_name = screener_names[i - 1]
                chart_path = recommended_stocks[screener_name].get("chart_path")

                if chart_path and os.path.exists(chart_path):
                    print(f"Uploading chart: {chart_path}")
                    media_id = self.client.upload_media(chart_path)
                    if media_id:
                        media_ids.append(media_id)
                        print(f"✓ Chart uploaded: media_id={media_id}")
                    else:
                        print(f"✗ Chart upload failed")

            # ツイート投稿
            result = self.client.post_tweet(tweet, media_ids=media_ids if media_ids else None)
            results.append(result)

            if result.get("success"):
                print(f"✓ 投稿成功")
                if media_ids:
                    print(f"  画像添付: {len(media_ids)}枚")
            else:
                print(f"✗ 投稿失敗: {result.get('error', 'Unknown error')}")

            # レート制限対策: 各投稿の間に2秒待機
            if i < len(tweets):
                time.sleep(2)

        print("\n=== X投稿完了 ===")
        success_count = sum(1 for r in results if r.get("success"))
        print(f"成功: {success_count}/{len(results)}")

        return results


def main():
    """テスト実行"""
    from dotenv import load_dotenv

    load_dotenv()

    X_API_KEY = os.getenv('X_API_KEY')
    X_API_SECRET = os.getenv('X_API_SECRET')
    X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("エラー: X API認証情報が設定されていません")
        return

    # テスト用の分析結果
    test_analysis = {
        "date": "2025-12-11",
        "recommended_stocks": {
            "短期中期長期の最強銘柄": {
                "ticker": "AAPL",
                "reason": "直近の決算で黒字化したことで上昇",
                "other_tickers": ["NVDA", "AVGO", "META", "GOOGL", "MSFT"],
                "trend": "AI需要によるTechnology業界が強い"
            },
            "爆発的EPS成長銘柄": {
                "ticker": "NVDA",
                "reason": "AI事業の好調な業績で期待上昇",
                "other_tickers": ["AMD", "AVGO", "TSM"],
                "trend": "Semiconductors業界が好調"
            },
            "出来高急増上昇銘柄": {
                "ticker": "TSLA",
                "reason": "新製品発表で期待が高まる",
                "other_tickers": ["RIVN", "LCID", "NIO"],
                "trend": "Electric Vehicles業界に注目"
            },
            "相対強度トップ2%銘柄": {
                "ticker": "MSFT",
                "reason": "クラウド事業の売上が予想超え",
                "other_tickers": ["GOOGL", "AMZN", "CRM"],
                "trend": "Software業界が堅調"
            },
            "急騰直後銘柄": {
                "ticker": "META",
                "reason": "広告収入の回復で株価急騰",
                "other_tickers": ["SNAP", "PINS", "SPOT"],
                "trend": "Social Media業界が回復"
            },
            "健全チャート銘柄": {
                "ticker": "GOOGL",
                "reason": "AI統合で検索事業が強化",
                "other_tickers": ["MSFT", "META", "AMZN"],
                "trend": "Internet Services業界が好調"
            }
        }
    }

    poster = XPoster(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    results = poster.post_analysis_result(test_analysis)

    # 結果を表示
    import json
    print("\n=== 投稿結果詳細 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
