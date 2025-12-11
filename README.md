# MarketAlgoX

米国株式市場の自動スクリーニング・AI分析・X投稿システム

## 概要

MarketAlgoXは、FinancialModelingPrep APIからデータを取得し、IBDスタイルのスクリーニングを実行し、OpenAI GPT-4oのAI分析を経てX (Twitter)に自動投稿するシステムです。

### 主な機能

- **データ収集**: FinancialModelingPrep APIから株価・財務データを取得
- **レーティング計算**: RS Rating、EPS Rating、Composite Rating等のIBDレーティングを計算
- **スクリーニング**: 6つのIBDスクリーナーで有望銘柄を抽出
- **JSON出力**: 日次スクリーニング結果をJSON形式で保存
- **AI分析**: OpenAI GPT-4oが各スクリーナーでオススメ銘柄を選定し、Industry Group傾向を分析
- **X投稿**: 分析結果を自動的にX (Twitter)に投稿
- **自動実行**: Cronで毎日朝6時（日本時間、火〜土曜）に自動実行

## スクリーナー一覧

| 日本語名 | 英語名 | 説明 |
|---------|--------|------|
| 短期中期長期の最強銘柄 | Momentum 97 | 短期・中期・長期すべてでトップパフォーマンスの銘柄 |
| 爆発的EPS成長銘柄 | Explosive Estimated EPS Growth Stocks | 爆発的なEPS成長を示す強気銘柄 |
| 出来高急増上昇銘柄 | Up on Volume List | 出来高を伴って上昇している銘柄 |
| 相対強度トップ2%銘柄 | Top 2% RS Rating List | 相対的強さが極めて高い銘柄 |
| 急騰直後銘柄 | 4% Bullish Yesterday | 前日に強い上昇を見せた銘柄 |
| 健全チャート銘柄 | Healthy Chart Watch List | 健全なチャートパターンを持つ銘柄 |

## セットアップ

### 1. 必要なAPI Keyを取得

#### FinancialModelingPrep API
1. https://financialmodelingprep.com/ にアクセス
2. アカウント作成
3. Premium Plan ($29/月) 以上を契約（推奨: 750 req/min）
4. API Keyを取得

#### OpenAI API
1. https://platform.openai.com/ にアクセス
2. アカウントでログイン
3. "API Keys" に移動
4. "Create new secret key" をクリック
5. API Keyをコピーして保存

#### X (Twitter) API
1. https://developer.twitter.com/ にアクセス
2. Developer Portalでアプリを作成
3. OAuth 1.0a の認証情報を取得:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
4. App permissionsを "Read and Write" に設定

### 2. 環境変数を設定

```bash
# .env.exampleを.envにコピー
cp .env.example .env

# .envファイルを編集してAPI Keyを設定
nano .env
```

`.env`ファイルの例:
```bash
FMP_API_KEY=your_actual_fmp_api_key
OPENAI_API_KEY=your_actual_openai_api_key
OPENAI_MODEL=gpt-4o
X_API_KEY=your_actual_x_api_key
X_API_SECRET=your_actual_x_api_secret
X_ACCESS_TOKEN=your_actual_x_access_token
X_ACCESS_TOKEN_SECRET=your_actual_x_access_token_secret
```

### 3. Dockerでデプロイ

```bash
# Dockerイメージをビルド
docker-compose build

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 4. 手動実行（テスト用）

```bash
# コンテナ内に入る
docker-compose exec app bash

# 日次ワークフローを手動実行
python scripts/daily_workflow.py
```

## ディレクトリ構成

```
MarketAlgoX/
├── SYSTEM_SPECIFICATION.md    # システム開発仕様書
├── README.md                   # このファイル
├── Dockerfile                  # Docker設定
├── docker-compose.yml          # Docker Compose設定
├── requirements.txt            # Python依存関係
├── .env.example                # 環境変数テンプレート
│
├── scripts/                    # スクリプト
│   ├── startup.sh              # コンテナ起動スクリプト
│   └── daily_workflow.py       # 日次ワークフロー
│
├── src/                        # ソースコード
│   ├── screeners/              # スクリーナーモジュール
│   │   └── screener_names.py   # スクリーナー名称定義
│   ├── json_export/            # JSON出力モジュール
│   │   └── exporter.py
│   ├── ai_analysis/            # AI分析モジュール
│   │   └── analyzer.py
│   └── social_posting/         # 投稿モジュール
│       └── poster.py
│
├── data/                       # データディレクトリ
│   ├── ibd_data.db             # SQLiteデータベース
│   └── screener_results/       # スクリーニング結果JSON
│
├── logs/                       # ログディレクトリ
│   ├── cron.log                # Cronログ
│   ├── app.log                 # アプリケーションログ
│   └── error.log               # エラーログ
│
├── cron/                       # Cron設定
│   └── marketalgox             # Cron定義ファイル
│
├── ibd_screeners.py            # IBDスクリーナー実装
├── ibd_data_collector.py       # データ収集
├── ibd_ratings_calculator.py   # レーティング計算
├── ibd_database.py             # データベース管理
└── run_ibd_screeners.py        # スクリーナー実行スクリプト
```

## 使い方

### 自動実行

デフォルトでは、毎日朝6時（日本時間、火〜土曜）に自動実行されます。

Cron設定:
```cron
0 6 * * 2-6 root cd /app && python scripts/daily_workflow.py
```

### 手動実行

```bash
# 日次ワークフロー全体を実行
python scripts/daily_workflow.py

# 個別にスクリーナーのみ実行
python run_ibd_screeners.py --run-screeners

# データ収集のみ実行
python run_ibd_screeners.py --collect-data

# レーティング計算のみ実行
python run_ibd_screeners.py --calculate-ratings
```

## JSON出力フォーマット

スクリーニング結果は `data/screener_results/YYYYMMDD.json` に保存されます。

```json
{
  "date": "2025-12-11",
  "market_date": "2025-12-10",
  "screeners": [
    {
      "name": "短期中期長期の最強銘柄",
      "english_name": "Momentum 97",
      "description": "短期・中期・長期すべてでトップパフォーマンスの銘柄を抽出",
      "total_count": 15,
      "new_count": 3,
      "tickers": [...]
    }
  ],
  "summary": {
    "total_screeners": 6,
    "total_unique_tickers": 45,
    "industry_distribution": {...}
  }
}
```

## トラブルシューティング

### Cronが実行されない

```bash
# Cronサービスの状態を確認
docker-compose exec app service cron status

# Cronログを確認
docker-compose exec app tail -f /app/logs/cron.log
```

### API制限エラー

FMP APIのレート制限を超えた場合、`ORATNEK_MAX_WORKERS`を減らしてください。

```bash
# .envファイルで調整
ORATNEK_MAX_WORKERS=3  # Starter Planの場合
```

### データベースエラー

```bash
# データベースを削除して再作成
docker-compose exec app rm /app/data/ibd_data.db
docker-compose exec app python run_ibd_screeners.py --collect-data
```

## ライセンス

MIT License

## 関連ドキュメント

- [システム開発仕様書](SYSTEM_SPECIFICATION.md)
- [FinancialModelingPrep API Docs](https://site.financialmodelingprep.com/developer/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
