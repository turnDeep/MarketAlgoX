# FMP Data API 導入ガイド

## 概要

このシステムは、FMP（Financial Modeling Prep）APIから全米国株のデータを取得し、ローカルデータベースに保存して、FMP互換のAPIサーバーとして提供します。

### なぜこのシステムが必要か？

1. **コスト削減**: FMP APIの呼び出し回数を削減し、API利用料金を節約
2. **高速化**: ローカルデータベースからの読み取りで、APIレスポンスが高速化
3. **可用性**: ネットワーク障害時でもデータにアクセス可能
4. **カスタマイズ**: 独自の分析やデータ加工が容易
5. **互換性**: 既存のFMPコードを変更せずに使用可能

## システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                         MarketAlgoX System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │  App         │         │  FMP API     │                     │
│  │  Container   │◄────────┤  Server      │                     │
│  │              │         │  Container   │                     │
│  └──────────────┘         └──────────────┘                     │
│         │                        │                              │
│         │                        │                              │
│         ▼                        ▼                              │
│  ┌─────────────────────────────────────┐                       │
│  │       Shared Data Volume            │                       │
│  │  ┌──────────────────────────────┐   │                       │
│  │  │   fmp_data.db (SQLite)       │   │                       │
│  │  │  - stock_list                │   │                       │
│  │  │  - company_profile           │   │                       │
│  │  │  - daily_prices              │   │                       │
│  │  │  - realtime_quotes           │   │                       │
│  │  │  - income_statements         │   │                       │
│  │  │  - balance_sheets            │   │                       │
│  │  │  - cash_flow_statements      │   │                       │
│  │  │  - financial_ratios          │   │                       │
│  │  │  - key_metrics               │   │                       │
│  │  └──────────────────────────────┘   │                       │
│  └─────────────────────────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │ 初回データ取得
                          ▼
                 ┌─────────────────┐
                 │   FMP Official  │
                 │   API           │
                 │  (financialmo-  │
                 │   delingprep)   │
                 └─────────────────┘
```

## セットアップ手順

### ステップ1: データベースの初期化とデータ取得

まず、FMP公式APIから全米国株のデータを取得してデータベースを構築します。

```bash
# Docker環境で実行
docker-compose up -d fmp_api

# データ取得スクリプトを実行（テスト: 100銘柄のみ）
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key YOUR_FMP_API_KEY \
  --db-path /app/data/fmp_data.db \
  --limit 100

# 本番: 全米国株を取得（数時間かかります）
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key YOUR_FMP_API_KEY \
  --db-path /app/data/fmp_data.db \
  --rate-limit 750 \
  --max-workers 10
```

#### データ取得のオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--api-key` | FMP API Key | 必須 |
| `--db-path` | データベースファイルパス | `./data/fmp_data.db` |
| `--rate-limit` | APIレート制限（回/分） | 750 |
| `--max-workers` | 並列ワーカー数 | 10 |
| `--limit` | 取得銘柄数の制限（テスト用） | なし |
| `--no-historical` | 過去株価データをスキップ | false |
| `--no-financials` | 財務諸表データをスキップ | false |
| `--update-quotes-only` | リアルタイム株価のみ更新 | false |

### ステップ2: API Keyの生成

ローカルAPIサーバーにアクセスするためのAPI Keyを生成します。

```bash
# API Keyを生成
curl -X POST "http://localhost:8000/admin/api-key/create?name=marketalgox-app&rate_limit=300&admin_key=ADMIN_SECRET_KEY_CHANGE_ME"
```

レスポンス:
```json
{
  "success": true,
  "api_key": "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890",
  "name": "marketalgox-app",
  "rate_limit": 300,
  "message": "API Key created successfully. Please save this key securely."
}
```

**重要**: 生成されたAPI Keyを`.env`ファイルに保存してください。

### ステップ3: 環境変数の設定

`.env`ファイルを編集:

```bash
# FMP API設定
FMP_API_KEY=your_fmp_official_api_key_here

# ローカルAPIを使用する設定
FMP_USE_LOCAL=true
FMP_LOCAL_URL=http://fmp_api:8000/api/v3
FMP_LOCAL_API_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

### ステップ4: アプリケーションの再起動

```bash
# すべてのコンテナを再起動
docker-compose down
docker-compose up -d
```

## 使用方法

### 既存コードの移行

既存のFMP APIを使用しているコードを、ローカルAPIに移行するのは簡単です。

#### Before（公式FMP API）

```python
import os
import requests

api_key = os.getenv('FMP_API_KEY')
url = f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={api_key}"
response = requests.get(url)
profile = response.json()[0]
```

#### After（FMP互換クライアント）

```python
from fmp_data_api import create_client

# 環境変数から自動設定（FMP_USE_LOCALで切り替え）
client = create_client()
profile = client.get_company_profile('AAPL')
```

### 使用例

#### 1. 基本的な使用

```python
from fmp_data_api import create_client

client = create_client()

# 企業プロファイル
profile = client.get_company_profile('AAPL')
print(f"Company: {profile['companyName']}")

# リアルタイム株価
quote = client.get_quote('AAPL')
print(f"Price: ${quote['price']}")

# 過去の株価データ
historical = client.get_historical_prices('AAPL', timeseries=100)
for price in historical['historical'][:5]:
    print(f"{price['date']}: ${price['close']}")
```

#### 2. 財務諸表の取得

```python
# 損益計算書（四半期）
income = client.get_income_statement('AAPL', period='quarter', limit=8)

# 貸借対照表（年次）
balance = client.get_balance_sheet('AAPL', period='annual', limit=5)

# キャッシュフロー計算書
cashflow = client.get_cash_flow_statement('AAPL', period='quarter', limit=8)
```

#### 3. APIの切り替え

```python
from fmp_data_api import FMPClient

client = FMPClient(api_key='your_key', use_local=False)

# 公式APIを使用
quote1 = client.get_quote('AAPL')

# ローカルAPIに切り替え
client.switch_to_local()
quote2 = client.get_quote('AAPL')

# 公式APIに戻す
client.switch_to_official()
quote3 = client.get_quote('AAPL')
```

## データの更新

### 定期的な更新スケジュール

#### 1. リアルタイム株価の更新（1時間ごと）

```bash
# Cronジョブに追加
0 * * * * docker exec fmp_api_server python data_fetcher.py --api-key $FMP_API_KEY --update-quotes-only >> /app/logs/fmp_update.log 2>&1
```

#### 2. 過去データの更新（毎日深夜）

```bash
# Cronジョブに追加
0 0 * * * docker exec fmp_api_server python data_fetcher.py --api-key $FMP_API_KEY --no-financials >> /app/logs/fmp_daily.log 2>&1
```

#### 3. 財務諸表の更新（週1回）

```bash
# Cronジョブに追加（毎週日曜深夜）
0 0 * * 0 docker exec fmp_api_server python data_fetcher.py --api-key $FMP_API_KEY >> /app/logs/fmp_weekly.log 2>&1
```

### 手動更新

```bash
# リアルタイム株価のみ更新
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key $FMP_API_KEY \
  --update-quotes-only

# 全データを更新
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key $FMP_API_KEY
```

## APIエンドポイント一覧

すべてのエンドポイントは`http://fmp_api:8000`でアクセス可能です。

| エンドポイント | 説明 | パラメータ |
|---------------|------|-----------|
| `/api/v3/stock/list` | 全銘柄リスト | - |
| `/api/v3/profile/{symbol}` | 企業プロファイル | symbol |
| `/api/v3/quote/{symbol}` | リアルタイム株価 | symbol |
| `/api/v3/quote-short/{symbol}` | 簡易株価 | symbol |
| `/api/v3/historical-price-full/{symbol}` | 過去株価データ | symbol, timeseries, from, to |
| `/api/v3/income-statement/{symbol}` | 損益計算書 | symbol, period, limit |
| `/api/v3/balance-sheet-statement/{symbol}` | 貸借対照表 | symbol, period, limit |
| `/api/v3/cash-flow-statement/{symbol}` | キャッシュフロー | symbol, period, limit |
| `/api/v3/ratios/{symbol}` | 財務比率 | symbol, period, limit |
| `/api/v3/key-metrics/{symbol}` | 主要指標 | symbol, period, limit |

### ドキュメント

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## パフォーマンス

### データ取得時間

| タスク | 銘柄数 | 推定時間 |
|-------|-------|---------|
| 基本情報のみ | 6,000 | 30-60分 |
| 基本情報 + 株価 | 6,000 | 1-2時間 |
| 全データ | 6,000 | 2-4時間 |

### APIレスポンス時間

| エンドポイント | 公式FMP | ローカルAPI |
|---------------|---------|-----------|
| Company Profile | 200-500ms | < 50ms |
| Quote | 200-500ms | < 50ms |
| Historical Prices | 500-1000ms | < 100ms |
| Income Statement | 500-1000ms | < 100ms |

## トラブルシューティング

### 1. データベースがロックされる

```bash
# データベースファイルの確認
docker exec -it fmp_api_server ls -lah /app/data/fmp_data.db

# 権限の修正
docker exec -it fmp_api_server chmod 666 /app/data/fmp_data.db
```

### 2. APIレート制限エラー

```bash
# レート制限を下げる
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key $FMP_API_KEY \
  --rate-limit 300 \
  --max-workers 3
```

### 3. API認証エラー

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 新しいAPI Keyを生成
curl -X POST "http://localhost:8000/admin/api-key/create?name=test&admin_key=ADMIN_SECRET_KEY_CHANGE_ME"
```

### 4. コンテナが起動しない

```bash
# ログを確認
docker-compose logs fmp_api

# コンテナを再ビルド
docker-compose build fmp_api
docker-compose up -d fmp_api
```

## よくある質問（FAQ）

### Q1: 公式FMP APIとローカルAPIを切り替えるには？

A: 環境変数`FMP_USE_LOCAL`を変更するだけです：

```bash
# ローカルAPIを使用
FMP_USE_LOCAL=true

# 公式FMP APIを使用
FMP_USE_LOCAL=false
```

### Q2: データはいつ更新すべきですか？

A: 以下を推奨します：
- リアルタイム株価: 1時間ごと
- 過去株価データ: 毎日1回
- 財務諸表: 週1回または四半期ごと

### Q3: データベースのサイズはどのくらいですか？

A: 約6,000銘柄の全データで：
- 基本情報のみ: 約50MB
- 株価データ含む: 約500MB-1GB
- 全データ: 約2-3GB

### Q4: 既存のコードを変更する必要はありますか？

A: 基本的に変更不要です。`fmp_client.py`の`create_client()`を使用すれば、環境変数で自動的に切り替わります。

### Q5: セキュリティは大丈夫ですか？

A: 以下の対策を推奨します：
1. 管理者キーを環境変数に変更
2. API Keyの定期的なローテーション
3. ファイアウォールでポート8000へのアクセス制限
4. 本番環境ではHTTPS/TLSを使用

## 次のステップ

1. ✅ データベースの初期化完了
2. ✅ API Keyの生成完了
3. ✅ 環境変数の設定完了
4. ⬜ 既存コードの移行
5. ⬜ 定期更新の設定
6. ⬜ 監視とログの設定

## サポート

詳細なドキュメント:
- [fmp_data_api/README.md](fmp_data_api/README.md) - 技術的な詳細
- [FMP Official Docs](https://site.financialmodelingprep.com/developer/docs) - 公式APIドキュメント

---

**更新日**: 2025-12-28
