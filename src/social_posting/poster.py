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

    def post_tweet(self, text: str) -> dict:
        """
        ツイートを投稿

        Args:
            text: ツイート本文

        Returns:
            投稿結果
        """
        try:
            response = self.client.create_tweet(text=text)
            return {
                "success": True,
                "tweet_id": response.data['id'] if response.data else None,
                "text": text
            }
        except Exception as e:
            print(f"Error posting tweet: {e}")
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

    MAX_TWEET_LENGTH = 280

    @staticmethod
    def format_analysis_result(analysis_result: dict, date: str) -> List[str]:
        """
        分析結果を投稿用に整形

        Args:
            analysis_result: AI分析結果
            date: 日付 (YYYY-MM-DD形式)

        Returns:
            投稿テキストのリスト（スレッド用）
        """
        tweets = []

        # 1. ヘッダー
        header = f"📊 米国株スクリーニング分析 ({date})\n\n"
        header += "本日の注目銘柄とIndustry Group傾向をAIが分析しました。\n"
        header += "#米国株 #株式投資"
        tweets.append(header)

        # 2. オススメ銘柄
        recommended_stocks = analysis_result.get("recommended_stocks", {})
        if recommended_stocks:
            for screener_name, stock_info in recommended_stocks.items():
                ticker = stock_info.get("ticker", "")
                reason = stock_info.get("reason", "")

                tweet = f"【{screener_name}】\n"
                tweet += f"💡 注目銘柄: ${ticker}\n"
                tweet += f"理由: {reason}"

                # 280字を超える場合は分割
                if len(tweet) > TweetFormatter.MAX_TWEET_LENGTH:
                    # 理由を短縮
                    max_reason_len = TweetFormatter.MAX_TWEET_LENGTH - len(tweet) + len(reason) - 10
                    reason = reason[:max_reason_len] + "..."
                    tweet = f"【{screener_name}】\n"
                    tweet += f"💡 注目銘柄: ${ticker}\n"
                    tweet += f"理由: {reason}"

                tweets.append(tweet)

        # 3. Industry Group傾向
        industry_trends = analysis_result.get("industry_trends", "")
        if industry_trends:
            tweet = f"📈 Industry Group傾向\n\n{industry_trends}"

            # 280字を超える場合は分割
            if len(tweet) > TweetFormatter.MAX_TWEET_LENGTH:
                max_trend_len = TweetFormatter.MAX_TWEET_LENGTH - len("📈 Industry Group傾向\n\n") - 10
                industry_trends_short = industry_trends[:max_trend_len] + "..."
                tweet = f"📈 Industry Group傾向\n\n{industry_trends_short}"

            tweets.append(tweet)

        return tweets

    @staticmethod
    def split_long_text(text: str, max_length: int = MAX_TWEET_LENGTH) -> List[str]:
        """
        長文を指定文字数以内に分割

        Args:
            text: 分割するテキスト
            max_length: 最大文字数

        Returns:
            分割されたテキストのリスト
        """
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
        AI分析結果を投稿

        Args:
            analysis_result: AI分析結果

        Returns:
            投稿結果のリスト
        """
        date = analysis_result.get("date", "")
        tweets = self.formatter.format_analysis_result(analysis_result, date)

        print(f"\n=== X投稿開始 ({len(tweets)}ツイート) ===")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n[{i}/{len(tweets)}]")
            print(tweet)
            print(f"文字数: {len(tweet)}")

        # スレッドとして投稿
        results = self.client.post_thread(tweets)

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
                "reason": "1ヶ月、3ヶ月、6ヶ月すべての期間で上位3%の強力なモメンタムを示しています。"
            },
            "爆発的EPS成長銘柄": {
                "ticker": "NVDA",
                "reason": "直近四半期のEPS成長率が150%を超え、AI需要の恩恵を受けています。"
            }
        },
        "industry_trends": "Technology業界が全体の40%を占め、特にSemiconductorsとSoftware - Infrastructureが目立ちます。AI関連銘柄への注目が集まっています。"
    }

    poster = XPoster(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    results = poster.post_analysis_result(test_analysis)

    # 結果を表示
    import json
    print("\n=== 投稿結果詳細 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
