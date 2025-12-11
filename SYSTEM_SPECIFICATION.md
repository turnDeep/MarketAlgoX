# MarketAlgoX システム開発仕様書

## バージョン情報
- **バージョン**: 1.1.0
- **作成日**: 2025-12-11
- **最終更新日**: 2025-12-11

---

## 目次
1. [システム概要](#1-システム概要)
2. [目指すべきゴール](#2-目指すべきゴール)
3. [機能要件](#3-機能要件)
4. [技術スタック](#4-技術スタック)
5. [システムアーキテクチャ](#5-システムアーキテクチャ)
6. [データフロー](#6-データフロー)
7. [各コンポーネントの詳細仕様](#7-各コンポーネントの詳細仕様)
8. [スクリーナー仕様](#8-スクリーナー仕様)
9. [データ構造](#9-データ構造)
10. [API仕様](#10-api仕様)
11. [環境設定](#11-環境設定)
12. [デプロイメント設定](#12-デプロイメント設定)
13. [セキュリティ考慮事項](#13-セキュリティ考慮事項)
14. [エラーハンドリング](#14-エラーハンドリング)
15. [テスト計画](#15-テスト計画)
16. [今後の拡張性](#16-今後の拡張性)

---

## 1. システム概要

MarketAlgoXは、米国株式市場のスクリーニング、AI分析、自動投稿を行う統合システムです。定期的に株価データを収集し、IBD（Investor's Business Daily）スタイルのスクリーニングを実行し、Gemini 3 ProのAI分析を経てX（旧Twitter）に投稿します。

### 1.1 システムの目的
- 米国株式市場の日次分析を自動化
- IBDスクリーニング手法による有望銘柄の抽出
- AIによる客観的な銘柄分析とトレンド把握
- X（Twitter）を通じた情報発信の自動化

### 1.2 対象ユーザー
- 米国株投資家
- テクニカル分析に基づく投資戦略を実践する投資家
- 市場トレンドを把握したい投資家

---

## 2. 目指すべきゴール

### 2.1 主要目標
1. **定期実行**: 毎日決まった時間（日本時間で朝6時、火曜から土曜）に自動実行
2. **データ収集**: FinancialModelingPrepのAPIを使用して米国株の必要なデータを取得
3. **スクリーニング**: 6つのIBDスクリーナーで銘柄をフィルタリング
4. **データ保存**: スクリーニング結果をJSON形式で日次保存（例：20251211.json）
5. **AI分析**: Gemini 3 ProのAPIを使用して分析
   - 各スクリーナーで新規に抽出された銘柄から、各スクリーナーでオススメ銘柄を1つ選定し理由を記述
   - 全スクリーナーの結果から、Industry Groupの傾向を分析
6. **自動投稿**: X（Twitter）APIを使用してBotとして投稿

### 2.2 参考リポジトリ
- **HanaView2**: https://github.com/turnDeep/HanaView2
  - Dockerfileとdocker-compose.ymlのCron設定を参考

---

## 3. 機能要件

### 3.1 データ収集機能
- **FR-DC-01**: FinancialModelingPrep APIから株価データを取得
- **FR-DC-02**: 企業プロファイルデータを取得
- **FR-DC-03**: 財務データ（EPS等）を取得
- **FR-DC-04**: ベンチマークデータ（SPY）を取得
- **FR-DC-05**: データをSQLiteデータベースに保存

### 3.2 スクリーニング機能
- **FR-SC-01**: 短期中期長期の最強銘柄スクリーナーを実行
- **FR-SC-02**: 爆発的EPS成長銘柄スクリーナーを実行
- **FR-SC-03**: 出来高急増上昇銘柄スクリーナーを実行
- **FR-SC-04**: 相対強度トップ2%銘柄スクリーナーを実行
- **FR-SC-05**: 急騰直後銘柄スクリーナーを実行
- **FR-SC-06**: 健全チャート銘柄スクリーナーを実行
- **FR-SC-07**: スクリーニング結果をJSON形式で保存

### 3.3 AI分析機能
- **FR-AI-01**: Gemini 3 Pro APIに接続
- **FR-AI-02**: 各スクリーナーで新規抽出された銘柄を分析
- **FR-AI-03**: 各スクリーナーでオススメ銘柄を1つ選定し、理由を記述
- **FR-AI-04**: Industry Groupの傾向を分析
- **FR-AI-05**: スクリーナーの意味をJSONに含めてGeminiに提供

### 3.4 投稿機能
- **FR-PO-01**: X（Twitter）APIに接続
- **FR-PO-02**: AI分析結果を整形
- **FR-PO-03**: Xに自動投稿
- **FR-PO-04**: 投稿履歴を記録

### 3.5 スケジューリング機能
- **FR-SH-01**: Cronジョブによる定期実行
- **FR-SH-02**: 日本時間で朝6時に実行（火曜から土曜）
- **FR-SH-03**: 実行ログの記録

---

## 4. 技術スタック

### 4.1 プログラミング言語
- **Python 3.12**: メインプログラミング言語

### 4.2 主要ライブラリ
```
# データ処理
pandas>=2.0.0
numpy>=1.24.0

# API クライアント
requests>=2.31.0
curl_cffi>=0.5.0

# Google API
gspread>=6.0.0
google-auth>=2.0.0
google-generativeai>=0.3.0  # Gemini API

# X (Twitter) API
tweepy>=4.14.0

# 環境変数管理
python-dotenv>=1.0.0

# データベース
sqlite3 (標準ライブラリ)
```

### 4.3 外部API
- **FinancialModelingPrep API**: 株価・財務データ取得
- **Gemini 3 Pro API**: AI分析
- **X (Twitter) API v2**: 投稿機能

### 4.4 インフラストラクチャ
- **Docker**: コンテナ化
- **Docker Compose**: オーケストレーション
- **Cron**: スケジューリング
- **SQLite**: データベース

---

## 5. システムアーキテクチャ

### 5.1 システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Container                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Cron Scheduler                           │  │
│  │         (毎日朝6時、火〜土曜実行)                      │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          1. Data Collection Module                    │  │
│  │  ・FMP APIからデータ取得                              │  │
│  │  ・SQLiteに保存                                       │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          2. Rating Calculator Module                  │  │
│  │  ・RS Rating計算                                      │  │
│  │  ・EPS Rating計算                                     │  │
│  │  ・Composite Rating計算                               │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          3. Screener Module                           │  │
│  │  ・6つのIBDスクリーナー実行                           │  │
│  │  ・前日結果との差分計算                               │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          4. JSON Export Module                        │  │
│  │  ・スクリーニング結果をJSON出力                       │  │
│  │  ・スクリーナー説明を含める                           │  │
│  │  ・新規銘柄をマーク                                   │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          5. Gemini Analysis Module                    │  │
│  │  ・各スクリーナーでオススメ銘柄選定                   │  │
│  │  ・Industry Group傾向分析                             │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          6. X Posting Module                          │  │
│  │  ・分析結果を整形                                     │  │
│  │  ・Xに投稿                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SQLite Database                          │  │
│  │  ・価格履歴                                           │  │
│  │  ・企業プロファイル                                   │  │
│  │  ・財務データ                                         │  │
│  │  ・レーティング                                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

External Services:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  FMP API         │  │  Gemini 3 Pro    │  │  X (Twitter)     │
│  (データ取得)     │  │  (AI分析)        │  │  (投稿)          │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### 5.2 ディレクトリ構成

```
MarketAlgoX/
├── Dockerfile                      # Docker設定
├── docker-compose.yml              # Docker Compose設定
├── requirements.txt                # Python依存関係
├── .env                            # 環境変数（非公開）
├── .env.example                    # 環境変数テンプレート
├── README.md                       # プロジェクト概要
├── SYSTEM_SPECIFICATION.md         # 本仕様書
│
├── scripts/                        # スクリプト
│   ├── startup.sh                  # コンテナ起動スクリプト
│   └── daily_workflow.py           # 日次ワークフロー
│
├── src/                            # ソースコード
│   ├── __init__.py
│   ├── data_collector/             # データ収集モジュール
│   │   ├── __init__.py
│   │   ├── fmp_client.py           # FMP APIクライアント
│   │   └── collector.py            # データ収集ロジック
│   │
│   ├── database/                   # データベースモジュール
│   │   ├── __init__.py
│   │   └── db_manager.py           # DB操作
│   │
│   ├── ratings/                    # レーティング計算モジュール
│   │   ├── __init__.py
│   │   └── calculator.py           # レーティング計算
│   │
│   ├── screeners/                  # スクリーナーモジュール
│   │   ├── __init__.py
│   │   ├── base_screener.py        # 基底クラス
│   │   ├── momentum_97.py          # Momentum 97
│   │   ├── explosive_eps.py        # Explosive EPS Growth
│   │   ├── up_on_volume.py         # Up on Volume
│   │   ├── top_2_percent_rs.py     # Top 2% RS Rating
│   │   ├── bullish_yesterday.py    # 4% Bullish Yesterday
│   │   └── healthy_chart.py        # Healthy Chart Watch
│   │
│   ├── json_export/                # JSON出力モジュール
│   │   ├── __init__.py
│   │   └── exporter.py             # JSON出力
│   │
│   ├── ai_analysis/                # AI分析モジュール
│   │   ├── __init__.py
│   │   ├── gemini_client.py        # Gemini APIクライアント
│   │   └── analyzer.py             # 分析ロジック
│   │
│   ├── social_posting/             # 投稿モジュール
│   │   ├── __init__.py
│   │   ├── x_client.py             # X APIクライアント
│   │   └── formatter.py            # 投稿テキスト整形
│   │
│   └── utils/                      # ユーティリティ
│       ├── __init__.py
│       ├── logger.py               # ロギング
│       └── helpers.py              # ヘルパー関数
│
├── data/                           # データディレクトリ
│   ├── ibd_data.db                 # SQLiteデータベース
│   ├── screener_results/           # スクリーニング結果
│   │   ├── 20251211.json
│   │   ├── 20251212.json
│   │   └── ...
│   └── historical/                 # 過去データ
│
├── logs/                           # ログディレクトリ
│   ├── cron.log                    # Cronログ
│   ├── app.log                     # アプリケーションログ
│   └── error.log                   # エラーログ
│
└── tests/                          # テストコード
    ├── __init__.py
    ├── test_data_collector.py
    ├── test_screeners.py
    ├── test_ai_analysis.py
    └── test_social_posting.py
```

---

## 6. データフロー

### 6.1 日次実行フロー

```
[Cron起動] (火〜土曜 6:00 JST)
    ↓
[1] データ収集フェーズ (6:00 - 6:15)
    ・FMP APIから全銘柄の株価データを取得
    ・企業プロファイルデータを取得
    ・財務データ（EPS等）を取得
    ・ベンチマークデータ（SPY）を取得
    ・データをSQLiteに保存
    ↓
[2] レーティング計算フェーズ (6:15 - 6:20)
    ・RS Rating計算
    ・EPS Rating計算
    ・Composite Rating計算
    ・A/D Rating計算
    ↓
[3] スクリーニングフェーズ (6:20 - 6:25)
    ・6つのスクリーナーを順次実行
    ・各スクリーナーの合格銘柄を抽出
    ・前日結果との差分計算（新規銘柄の特定）
    ↓
[4] JSON出力フェーズ (6:25 - 6:26)
    ・スクリーニング結果をJSON形式で保存
    ・ファイル名: YYYYMMDD.json
    ・各銘柄の詳細データと新規フラグを含める
    ↓
[5] AI分析フェーズ (6:26 - 6:30)
    ・JSONデータをGemini 3 Pro APIに送信
    ・各スクリーナーでオススメ銘柄を1つ選定
    ・選定理由を生成
    ・Industry Group傾向を分析
    ↓
[6] 投稿フェーズ (6:30 - 6:32)
    ・AI分析結果を投稿用に整形
    ・X (Twitter) APIで投稿
    ・投稿履歴を記録
    ↓
[完了] (6:32)
    ・実行ログを保存
    ・次回実行まで待機
```

### 6.2 データ更新頻度
- **株価データ**: 毎日
- **企業プロファイル**: 週1回（月曜日）
- **財務データ**: 週1回（月曜日）
- **ベンチマークデータ**: 毎日

---

## 7. 各コンポーネントの詳細仕様

### 7.1 データ収集モジュール (Data Collection Module)

#### 7.1.1 概要
FinancialModelingPrep APIから株価データを取得し、SQLiteデータベースに保存します。

#### 7.1.2 主要クラス: `FMPClient`

```python
class FMPClient:
    """FinancialModelingPrep APIクライアント"""

    def __init__(self, api_key: str, rate_limit: int = 750):
        """
        Args:
            api_key: FMP API キー
            rate_limit: 分あたりのリクエスト制限
        """
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def get_price_history(self, ticker: str, days: int = 180) -> pd.DataFrame:
        """株価履歴を取得"""
        pass

    def get_company_profile(self, ticker: str) -> dict:
        """企業プロファイルを取得"""
        pass

    def get_income_statement(self, ticker: str) -> dict:
        """損益計算書を取得"""
        pass

    def get_eps_data(self, ticker: str) -> dict:
        """EPS データを取得"""
        pass
```

#### 7.1.3 主要クラス: `DataCollector`

```python
class DataCollector:
    """データ収集オーケストレーター"""

    def __init__(self, fmp_client: FMPClient, db_manager: DBManager):
        self.fmp_client = fmp_client
        self.db_manager = db_manager

    def collect_all_data(self, tickers: List[str], max_workers: int = 6):
        """全データを並列収集"""
        pass

    def collect_price_data(self, ticker: str):
        """株価データを収集"""
        pass

    def collect_fundamental_data(self, ticker: str):
        """ファンダメンタルデータを収集"""
        pass
```

### 7.2 レーティング計算モジュール (Rating Calculator Module)

#### 7.2.1 概要
IBDスタイルのレーティング（RS Rating、EPS Rating、Composite Rating等）を計算します。

#### 7.2.2 主要クラス: `RatingsCalculator`

```python
class RatingsCalculator:
    """IBDレーティング計算"""

    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    def calculate_rs_rating(self, ticker: str) -> float:
        """Relative Strength Ratingを計算 (0-99)"""
        pass

    def calculate_eps_rating(self, ticker: str) -> float:
        """EPS Ratingを計算 (0-99)"""
        pass

    def calculate_composite_rating(self, ticker: str) -> float:
        """Composite Ratingを計算 (0-99)"""
        pass

    def calculate_ad_rating(self, ticker: str) -> str:
        """Accumulation/Distribution Ratingを計算 (A-E)"""
        pass

    def calculate_all_ratings(self):
        """全銘柄のレーティングを計算"""
        pass
```

### 7.3 スクリーナーモジュール (Screener Module)

#### 7.3.1 概要
6つのIBDスクリーナーを実行し、条件に合致する銘柄を抽出します。

#### 7.3.2 基底クラス: `BaseScreener`

```python
class BaseScreener(ABC):
    """スクリーナー基底クラス"""

    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.name = ""
        self.description = ""
        self.criteria = {}

    @abstractmethod
    def screen(self) -> List[str]:
        """スクリーニングを実行"""
        pass

    def get_screener_info(self) -> dict:
        """スクリーナー情報を取得"""
        return {
            "name": self.name,
            "description": self.description,
            "criteria": self.criteria
        }
```

### 7.4 JSON出力モジュール (JSON Export Module)

#### 7.4.1 概要
スクリーニング結果をJSON形式で出力します。前日結果との差分を計算し、新規銘柄をマークします。

#### 7.4.2 主要クラス: `JSONExporter`

```python
class JSONExporter:
    """JSON出力管理"""

    def __init__(self, db_manager: DBManager, output_dir: str = "./data/screener_results"):
        self.db_manager = db_manager
        self.output_dir = output_dir

    def export_screening_results(
        self,
        date: str,
        screener_results: Dict[str, List[str]],
        screener_info: Dict[str, dict]
    ) -> str:
        """
        スクリーニング結果をJSON出力

        Args:
            date: 日付 (YYYYMMDD形式)
            screener_results: {スクリーナー名: [銘柄リスト]}
            screener_info: {スクリーナー名: {説明、条件}}

        Returns:
            JSONファイルパス
        """
        pass

    def identify_new_tickers(
        self,
        today_results: Dict[str, List[str]],
        yesterday_results: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """新規銘柄を特定"""
        pass

    def get_ticker_details(self, ticker: str) -> dict:
        """銘柄の詳細データを取得"""
        pass
```

### 7.5 AI分析モジュール (AI Analysis Module)

#### 7.5.1 概要
Gemini 3 Pro APIを使用してスクリーニング結果を分析します。

#### 7.5.2 主要クラス: `GeminiClient`

```python
class GeminiClient:
    """Gemini 3 Pro APIクライアント"""

    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-pro')

    def generate_content(self, prompt: str) -> str:
        """コンテンツ生成"""
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_with_json(self, json_data: dict) -> str:
        """JSONデータを使って分析"""
        pass
```

#### 7.5.3 主要クラス: `ScreenerAnalyzer`

```python
class ScreenerAnalyzer:
    """スクリーニング結果分析"""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def analyze_screening_results(self, json_file_path: str) -> dict:
        """
        スクリーニング結果を分析

        Returns:
            {
                "recommended_stocks": {
                    "screener_name": {
                        "ticker": "AAPL",
                        "reason": "理由..."
                    }
                },
                "industry_trends": "分析結果..."
            }
        """
        pass

    def select_top_stock_per_screener(
        self,
        screener_name: str,
        new_tickers: List[str],
        ticker_data: Dict[str, dict],
        screener_info: dict
    ) -> dict:
        """各スクリーナーでトップ銘柄を選定"""
        pass

    def analyze_industry_trends(
        self,
        all_tickers: List[str],
        ticker_data: Dict[str, dict]
    ) -> str:
        """Industry Group傾向を分析"""
        pass
```

### 7.6 投稿モジュール (Social Posting Module)

#### 7.6.1 概要
X (Twitter) APIを使用してAI分析結果を投稿します。

#### 7.6.2 主要クラス: `XClient`

```python
class XClient:
    """X (Twitter) APIクライアント"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        import tweepy
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

    def post_tweet(self, text: str) -> dict:
        """ツイートを投稿"""
        response = self.client.create_tweet(text=text)
        return response.data

    def post_thread(self, texts: List[str]) -> List[dict]:
        """スレッドを投稿"""
        pass
```

#### 7.6.3 主要クラス: `TweetFormatter`

```python
class TweetFormatter:
    """投稿テキスト整形"""

    MAX_TWEET_LENGTH = 280

    def format_analysis_result(self, analysis_result: dict, date: str) -> List[str]:
        """
        分析結果を投稿用に整形

        Args:
            analysis_result: AI分析結果
            date: 日付 (YYYY-MM-DD形式)

        Returns:
            投稿テキストのリスト（スレッド用）
        """
        pass

    def format_recommended_stocks(self, recommended_stocks: dict) -> str:
        """オススメ銘柄を整形"""
        pass

    def format_industry_trends(self, industry_trends: str) -> str:
        """Industry Group傾向を整形"""
        pass

    def split_long_text(self, text: str) -> List[str]:
        """長文を280字以内に分割"""
        pass
```

### 7.7 スケジューラーモジュール (Scheduler Module)

#### 7.7.1 Cronジョブ設定

**crontab設定** (`/etc/cron.d/marketalgox`):
```cron
# MarketAlgoX Daily Workflow
# 毎日朝6時（JST）、火曜から土曜に実行
# 米国市場の営業日（月〜金）の翌日（火〜土）にデータ取得

TZ=Asia/Tokyo
0 6 * * 2-6 root cd /app && /usr/local/bin/python scripts/daily_workflow.py >> /app/logs/cron.log 2>> /app/logs/error.log
```

#### 7.7.2 日次ワークフロースクリプト

**scripts/daily_workflow.py**:
```python
#!/usr/bin/env python
"""
MarketAlgoX 日次ワークフロー

このスクリプトは以下の処理を順次実行します:
1. データ収集
2. レーティング計算
3. スクリーニング
4. JSON出力
5. AI分析
6. X投稿
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def main():
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("MarketAlgoX Daily Workflow 開始")
    logger.info(f"実行時刻: {datetime.now()}")
    logger.info("=" * 80)

    try:
        # 1. データ収集
        logger.info("\n[1/6] データ収集フェーズ開始")
        from src.data_collector import DataCollector
        collector = DataCollector()
        collector.run()
        logger.info("データ収集完了")

        # 2. レーティング計算
        logger.info("\n[2/6] レーティング計算フェーズ開始")
        from src.ratings import RatingsCalculator
        calculator = RatingsCalculator()
        calculator.calculate_all_ratings()
        logger.info("レーティング計算完了")

        # 3. スクリーニング
        logger.info("\n[3/6] スクリーニングフェーズ開始")
        from src.screeners import ScreenerRunner
        screener = ScreenerRunner()
        results = screener.run_all_screeners()
        logger.info(f"スクリーニング完了: {len(results)} スクリーナー実行")

        # 4. JSON出力
        logger.info("\n[4/6] JSON出力フェーズ開始")
        from src.json_export import JSONExporter
        exporter = JSONExporter()
        json_file = exporter.export_screening_results(
            date=datetime.now().strftime("%Y%m%d"),
            screener_results=results
        )
        logger.info(f"JSON出力完了: {json_file}")

        # 5. AI分析
        logger.info("\n[5/6] AI分析フェーズ開始")
        from src.ai_analysis import ScreenerAnalyzer
        analyzer = ScreenerAnalyzer()
        analysis = analyzer.analyze_screening_results(json_file)
        logger.info("AI分析完了")

        # 6. X投稿
        logger.info("\n[6/6] X投稿フェーズ開始")
        from src.social_posting import XPoster
        poster = XPoster()
        poster.post_analysis_result(analysis)
        logger.info("X投稿完了")

        logger.info("\n" + "=" * 80)
        logger.info("MarketAlgoX Daily Workflow 正常終了")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 8. スクリーナー仕様

### 8.1 短期中期長期の最強銘柄 (Momentum 97)

**目的**: 短期・中期・長期すべてでトップパフォーマンスの銘柄を抽出

**条件**:
- 1M Rank (Pct) ≥ 97%
- 3M Rank (Pct) ≥ 97%
- 6M Rank (Pct) ≥ 97%

**説明**:
過去1ヶ月、3ヶ月、6ヶ月のすべての期間でパフォーマンスが上位3%に入る強力なモメンタムを持つ銘柄を抽出します。

**英語名**: Momentum 97

### 8.2 爆発的EPS成長銘柄 (Explosive Estimated EPS Growth Stocks)

**目的**: 爆発的なEPS成長を示す強気銘柄を抽出

**条件**:
- RS Rating ≥ 80
- RS STS% ≥ 80
- EPS Growth Last Qtr ≥ 100%
- 50-Day Avg Vol ≥ 100K
- Price vs 50-Day ≥ 0.0%

**説明**:
直近四半期のEPS成長率が100%以上で、相対的強さも高い銘柄を抽出します。

**英語名**: Explosive Estimated EPS Growth Stocks

### 8.3 出来高急増上昇銘柄 (Up on Volume List)

**目的**: 出来高を伴って上昇している銘柄を抽出

**条件**:
- Price % Chg ≥ 0.00%
- Vol% Chg vs 50-Day ≥ 20%
- Current Price ≥ $10
- 50-Day Avg Vol ≥ 100K
- Market Cap ≥ $250M
- RS Rating ≥ 80
- RS STS% ≥ 80
- EPS % Chg Last Qtr ≥ 20%
- A/D Rating ABC

**説明**:
出来高が平常時より20%以上増加しながら価格が上昇している銘柄を抽出します。

**英語名**: Up on Volume List

### 8.4 相対強度トップ2%銘柄 (Top 2% RS Rating List)

**目的**: 相対的強さが極めて高い銘柄を抽出

**条件**:
- RS Rating ≥ 98
- RS STS% ≥ 80
- 10Day > 21Day > 50Day
- 50-Day Avg Vol ≥ 100K
- Volume ≥ 100K
- Sector NOT: medical/healthcare

**説明**:
RS Ratingが98以上（上位2%）で、移動平均が理想的な上昇トレンドを形成している銘柄を抽出します。

**英語名**: Top 2% RS Rating List

### 8.5 急騰直後銘柄 (4% Bullish Yesterday)

**目的**: 前日に強い上昇を見せた銘柄を抽出

**条件**:
- Price ≥ $1
- Change > 4%
- Market cap > $250M
- Volume > 100K
- Rel Volume > 1
- Change from Open > 0%
- Avg Volume 90D > 100K
- RS STS% ≥ 80

**説明**:
前日に4%以上上昇し、出来高も平常時以上の銘柄を抽出します。

**英語名**: 4% Bullish Yesterday

### 8.6 健全チャート銘柄 (Healthy Chart Watch List)

**目的**: 健全なチャートパターンを持つ銘柄を抽出

**条件**:
- 10Day > 21Day > 50Day
- 50Day > 150Day > 200Day
- RS Line New High
- RS Rating ≥ 90
- A/D Rating AB
- Comp Rating ≥ 80
- 50-Day Avg Vol ≥ 100K

**説明**:
短期・中期・長期の移動平均がすべて理想的な上昇トレンドを形成し、RS Lineが新高値の銘柄を抽出します。

**英語名**: Healthy Chart Watch List

### 8.7 スクリーナー名称対応表

| 日本語名 | 英語名 |
|---------|--------|
| 短期中期長期の最強銘柄 | Momentum 97 |
| 爆発的EPS成長銘柄 | Explosive Estimated EPS Growth Stocks |
| 出来高急増上昇銘柄 | Up on Volume List |
| 相対強度トップ2%銘柄 | Top 2% RS Rating List |
| 急騰直後銘柄 | 4% Bullish Yesterday |
| 健全チャート銘柄 | Healthy Chart Watch List |

**注意**: JSONデータやプログラム内では日本語名を使用し、参照用に英語名も併記します。

---

## 9. データ構造

### 9.1 JSON出力フォーマット

**ファイル名**: `YYYYMMDD.json` (例: `20251211.json`)

**構造**:
```json
{
  "date": "2025-12-11",
  "market_date": "2025-12-10",
  "screeners": [
    {
      "name": "短期中期長期の最強銘柄",
      "english_name": "Momentum 97",
      "description": "短期・中期・長期すべてでトップパフォーマンスの銘柄を抽出",
      "criteria": {
        "1M Rank (Pct)": "≥ 97%",
        "3M Rank (Pct)": "≥ 97%",
        "6M Rank (Pct)": "≥ 97%"
      },
      "total_count": 15,
      "new_count": 3,
      "tickers": [
        {
          "ticker": "AAPL",
          "company_name": "Apple Inc.",
          "is_new": true,
          "price": 195.50,
          "change_1d_pct": 2.5,
          "volume": 52000000,
          "market_cap": 3000000000000,
          "sector": "Technology",
          "industry_group": "Consumer Electronics",
          "ratings": {
            "rs_rating": 95,
            "eps_rating": 88,
            "comp_rating": 92,
            "ad_rating": "A"
          },
          "screener_values": {
            "1m_rank_pct": 98.5,
            "3m_rank_pct": 97.8,
            "6m_rank_pct": 99.2
          }
        }
      ]
    },
    {
      "name": "爆発的EPS成長銘柄",
      "english_name": "Explosive Estimated EPS Growth Stocks",
      "description": "爆発的なEPS成長を示す強気銘柄を抽出",
      "criteria": {
        "RS Rating": "≥ 80",
        "RS STS%": "≥ 80",
        "EPS Growth Last Qtr": "≥ 100%",
        "50-Day Avg Vol": "≥ 100K",
        "Price vs 50-Day": "≥ 0.0%"
      },
      "total_count": 8,
      "new_count": 2,
      "tickers": [
        // ...
      ]
    }
    // ... 他のスクリーナー
  ],
  "summary": {
    "total_screeners": 6,
    "total_unique_tickers": 45,
    "total_new_tickers": 12,
    "industry_distribution": {
      "Technology": 15,
      "Healthcare": 8,
      "Consumer Cyclical": 7,
      "Industrials": 5,
      "Other": 10
    }
  }
}
```

### 9.2 データベーススキーマ (SQLite)

#### 9.2.1 price_history テーブル
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

CREATE INDEX idx_price_ticker_date ON price_history(ticker, date);
```

#### 9.2.2 company_profiles テーブル
```sql
CREATE TABLE company_profiles (
    ticker TEXT PRIMARY KEY,
    company_name TEXT,
    sector TEXT,
    industry TEXT,
    industry_group TEXT,
    market_cap REAL,
    country TEXT,
    exchange TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 9.2.3 ratings テーブル
```sql
CREATE TABLE ratings (
    ticker TEXT PRIMARY KEY,
    rs_rating REAL,
    eps_rating REAL,
    comp_rating REAL,
    ad_rating TEXT,
    price_vs_52w_high REAL,
    calculated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 9.2.4 eps_data テーブル
```sql
CREATE TABLE eps_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    fiscal_date TEXT,
    reported_eps REAL,
    estimated_eps REAL,
    surprise_pct REAL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, fiscal_date)
);
```

#### 9.2.5 screener_history テーブル
```sql
CREATE TABLE screener_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    screener_name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    is_new BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, screener_name, ticker)
);

CREATE INDEX idx_screener_date ON screener_history(date, screener_name);
```

#### 9.2.6 post_history テーブル
```sql
CREATE TABLE post_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    platform TEXT NOT NULL,  -- 'X' or 'Twitter'
    post_id TEXT,
    content TEXT,
    status TEXT,  -- 'success', 'failed'
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 10. API仕様

### 10.1 FinancialModelingPrep API

**ベースURL**: `https://financialmodelingprep.com/api/v3`

**主要エンドポイント**:

1. **株価履歴**
   - エンドポイント: `/historical-price-full/{ticker}`
   - パラメータ: `?from=YYYY-MM-DD&to=YYYY-MM-DD&apikey={API_KEY}`
   - レート制限: Premium Plan 750 req/min

2. **企業プロファイル**
   - エンドポイント: `/profile/{ticker}`
   - パラメータ: `?apikey={API_KEY}`

3. **損益計算書**
   - エンドポイント: `/income-statement/{ticker}`
   - パラメータ: `?period=quarter&limit=4&apikey={API_KEY}`

4. **EPS**
   - エンドポイント: `/earnings-surprises/{ticker}`
   - パラメータ: `?apikey={API_KEY}`

### 10.2 Gemini 3 Pro API

**SDKライブラリ**: `google-generativeai`

**主要メソッド**:

```python
import google.generativeai as genai

# 設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-pro')

# コンテンツ生成
response = model.generate_content(prompt)
text = response.text
```

**プロンプト設計**:

```
あなたは米国株式市場の専門アナリストです。以下のスクリーニング結果を分析してください。

【タスク1】各スクリーナーでオススメ銘柄を1つ選定
各スクリーナーで新規に抽出された銘柄の中から、各スクリーナーの基準値を参考に最も有望な銘柄を1つ選び、理由を簡潔に述べてください。

スクリーナー情報:
{screener_info}

新規銘柄データ:
{new_tickers_data}

【タスク2】Industry Group傾向分析
すべてのスクリーナーで抽出された銘柄を見て、どのIndustry Groupの銘柄が多いか傾向を述べてください。

全銘柄データ:
{all_tickers_data}

出力形式:
{
  "recommended_stocks": {
    "短期中期長期の最強銘柄": {
      "ticker": "AAPL",
      "reason": "..."
    },
    "爆発的EPS成長銘柄": {
      "ticker": "NVDA",
      "reason": "..."
    },
    ...
  },
  "industry_trends": "..."
}
```

### 10.3 X (Twitter) API v2

**SDKライブラリ**: `tweepy`

**認証方式**: OAuth 1.0a

**主要メソッド**:

```python
import tweepy

# 認証
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# ツイート投稿
response = client.create_tweet(text="...")

# スレッド投稿
tweets = []
for text in thread_texts:
    response = client.create_tweet(
        text=text,
        in_reply_to_tweet_id=tweets[-1].data['id'] if tweets else None
    )
    tweets.append(response)
```

**レート制限**:
- ツイート投稿: 300ツイート/3時間（ユーザーコンテキスト）

---

## 11. 環境設定

### 11.1 環境変数 (.env)

```bash
# FinancialModelingPrep API
FMP_API_KEY=your_fmp_api_key_here
FMP_RATE_LIMIT=750

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# X (Twitter) API
X_API_KEY=your_x_api_key_here
X_API_SECRET=your_x_api_secret_here
X_ACCESS_TOKEN=your_x_access_token_here
X_ACCESS_TOKEN_SECRET=your_x_access_token_secret_here

# Google Sheets (既存機能用)
CREDENTIALS_FILE=credentials.json
SPREADSHEET_NAME=Market Dashboard

# データベース
IBD_DB_PATH=./data/ibd_data.db

# 並列処理
ORATNEK_MAX_WORKERS=6

# ログレベル
LOG_LEVEL=INFO

# タイムゾーン
TZ=Asia/Tokyo
```

### 11.2 API キー取得方法

#### 11.2.1 FinancialModelingPrep API
1. https://financialmodelingprep.com/ にアクセス
2. アカウント作成
3. Premium Plan ($29/月) 以上を契約（推奨: 750 req/min）
4. ダッシュボードからAPI Keyを取得

#### 11.2.2 Gemini API
1. https://ai.google.dev/ にアクセス
2. Googleアカウントでログイン
3. "Get API Key" をクリック
4. API Keyを生成

#### 11.2.3 X (Twitter) API
1. https://developer.twitter.com/ にアクセス
2. Developer Portalでアプリを作成
3. OAuth 1.0a の認証情報を取得:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
4. App permissionsを "Read and Write" に設定

---

## 12. デプロイメント設定

### 12.1 Dockerfile

```dockerfile
# Use Python 3.12 slim
FROM python:3.12-slim

# Set timezone to Asia/Tokyo
ENV TZ=Asia/Tokyo
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/data/screener_results

# Setup cron job
COPY cron/marketalgox /etc/cron.d/marketalgox
RUN chmod 0644 /etc/cron.d/marketalgox && \
    crontab /etc/cron.d/marketalgox

# Make startup script executable
COPY scripts/startup.sh /app/scripts/startup.sh
RUN chmod +x /app/scripts/startup.sh

# Start cron and keep container running
CMD ["/app/scripts/startup.sh"]
```

### 12.2 docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: marketalgox
    env_file:
      - .env
    environment:
      - TZ=Asia/Tokyo
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    restart: unless-stopped
    # No port mapping needed (cron only)
```

### 12.3 Cronジョブ設定

**cron/marketalgox**:
```cron
# MarketAlgoX Daily Workflow
# 火曜から土曜の朝6時（JST）に実行

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
TZ=Asia/Tokyo

# 毎日朝6時、火曜から土曜
0 6 * * 2-6 root cd /app && /usr/local/bin/python scripts/daily_workflow.py >> /app/logs/cron.log 2>> /app/logs/error.log
```

### 12.4 起動スクリプト

**scripts/startup.sh**:
```bash
#!/bin/bash

# MarketAlgoX Startup Script

echo "Starting MarketAlgoX..."
echo "Timezone: $TZ"
echo "Current time: $(date)"

# Create log files if they don't exist
touch /app/logs/cron.log
touch /app/logs/error.log
touch /app/logs/app.log

# Start cron service
echo "Starting cron service..."
service cron start

# Verify cron is running
if pgrep cron > /dev/null; then
    echo "Cron service started successfully"
else
    echo "ERROR: Cron service failed to start"
    exit 1
fi

# Display cron jobs
echo "Active cron jobs:"
crontab -l

# Tail logs to keep container running
echo "Tailing logs..."
tail -f /app/logs/cron.log /app/logs/error.log
```

### 12.5 デプロイ手順

```bash
# 1. リポジトリクローン
git clone https://github.com/turnDeep/MarketAlgoX.git
cd MarketAlgoX

# 2. 環境変数設定
cp .env.example .env
# .envファイルを編集してAPI Keyを設定

# 3. Dockerイメージビルド
docker-compose build

# 4. コンテナ起動
docker-compose up -d

# 5. ログ確認
docker-compose logs -f

# 6. 手動実行テスト（オプション）
docker-compose exec app python scripts/daily_workflow.py

# 7. Cronジョブ確認
docker-compose exec app crontab -l
```

---

## 13. セキュリティ考慮事項

### 13.1 APIキー管理
- **環境変数**: すべてのAPIキーは`.env`ファイルで管理
- **Git除外**: `.gitignore`で`.env`ファイルを除外
- **権限管理**: `.env`ファイルのパーミッションを`600`に設定

### 13.2 データ保護
- **データベース暗号化**: SQLiteデータベースファイルのバックアップ時は暗号化
- **ログ管理**: エラーログにAPIキーや機密情報を含めない
- **ボリュームマウント**: Dockerボリュームで機密データを保護

### 13.3 API レート制限対策
- **リクエスト制御**: FMP APIのレート制限を遵守（750 req/min）
- **リトライロジック**: API失敗時の指数バックオフ実装
- **並列処理制限**: `max_workers`パラメータで並列数を制御

### 13.4 エラーハンドリング
- **例外処理**: すべてのAPIコールに`try-except`ブロック
- **ログ記録**: すべてのエラーを詳細にログに記録
- **リトライ機構**: 一時的なエラーには自動リトライ

---

## 14. エラーハンドリング

### 14.1 データ収集エラー
- **FMP API エラー**:
  - レート制限超過: 待機後リトライ
  - 無効なティッカー: スキップしてログ記録
  - ネットワークエラー: 3回までリトライ

### 14.2 スクリーニングエラー
- **データ不足**:
  - 最小データ要件を満たさない銘柄はスキップ
  - ログに警告を記録

### 14.3 AI分析エラー
- **Gemini API エラー**:
  - レート制限: 待機後リトライ
  - 無効なレスポンス: デフォルト分析結果を使用
  - ネットワークエラー: 3回までリトライ

### 14.4 投稿エラー
- **X API エラー**:
  - 重複投稿: ログに記録してスキップ
  - レート制限: 次回実行時に投稿
  - 認証エラー: アラート通知

---

## 15. テスト計画

### 15.1 ユニットテスト
- **データ収集モジュール**: `tests/test_data_collector.py`
- **レーティング計算**: `tests/test_ratings.py`
- **スクリーナー**: `tests/test_screeners.py`
- **JSON出力**: `tests/test_json_export.py`
- **AI分析**: `tests/test_ai_analysis.py`
- **投稿機能**: `tests/test_social_posting.py`

### 15.2 統合テスト
- **エンドツーエンドテスト**: 全ワークフローを通したテスト
- **APIモック**: 外部API呼び出しをモック化

### 15.3 テスト実行
```bash
# 全テスト実行
pytest tests/

# カバレッジレポート
pytest --cov=src tests/
```

---

## 16. 今後の拡張性

### 16.1 機能拡張
- **複数マーケット対応**: NASDAQ、NYSEに加えて他の市場にも対応
- **アラート機能**: 特定条件を満たした銘柄のアラート通知
- **バックテスト**: 過去データを使用した戦略のバックテスト
- **ポートフォリオ管理**: 選定銘柄のポートフォリオ追跡

### 16.2 AI機能強化
- **マルチモデル対応**: GPT-4、Claude等の複数AIモデルを統合
- **チャート分析**: 画像認識によるチャートパターン分析
- **センチメント分析**: ニュース・SNSのセンチメント分析

### 16.3 投稿プラットフォーム拡張
- **Bluesky対応**: X以外のプラットフォームへの投稿
- **Discord/Slack通知**: チーム向け通知機能
- **ウェブダッシュボード**: リアルタイムダッシュボードの構築

---

## 付録A: 用語集

| 用語 | 説明 |
|------|------|
| **IBD** | Investor's Business Daily - 投資情報誌 |
| **RS Rating** | Relative Strength Rating - 相対的強さレーティング（0-99） |
| **EPS Rating** | Earnings Per Share Rating - 1株当たり利益レーティング（0-99） |
| **Composite Rating** | 総合レーティング - RS RatingとEPS Ratingを組み合わせたもの |
| **A/D Rating** | Accumulation/Distribution Rating - 蓄積/分配レーティング（A-E） |
| **FMP** | FinancialModelingPrep - 金融データプロバイダー |
| **Cron** | Unixベースのジョブスケジューラー |
| **Industry Group** | 産業グループ - 同じ産業に属する企業のグループ |

---

## 付録B: 参考資料

- **IBD Methodology**: https://www.investors.com/ibd-university/
- **FinancialModelingPrep API Docs**: https://site.financialmodelingprep.com/developer/docs
- **Gemini API Docs**: https://ai.google.dev/docs
- **Twitter API v2 Docs**: https://developer.twitter.com/en/docs/twitter-api
- **Docker Documentation**: https://docs.docker.com/
- **Python Best Practices**: https://docs.python-guide.org/

---

## 変更履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|------------|------|----------|--------|
| 1.1.0 | 2025-12-11 | スクリーナー名を分かりやすい日本語名に変更 | Claude |
| 1.0.0 | 2025-12-11 | 初版作成 | Claude |

---

**文書終わり**
