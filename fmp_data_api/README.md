# FMP Data API - ローカルFMP互換APIシステム

FMP（Financial Modeling Prep）APIから米国株の全銘柄データを取得し、ローカルデータベースに保存して、FMP互換のAPIとして提供するシステムです。

## 概要

このシステムは以下の3つのコンポーネントで構成されています：

1. **データ取得スクリプト** (`data_fetcher.py`) - FMP APIから全米国株のデータを取得してデータベースに保存
2. **APIサーバー** (`api_server.py`) - データベースからデータを読み取り、FMP互換のAPIとして提供
3. **クライアントライブラリ** (`fmp_client.py`) - FMP互換のクライアント（環境変数で公式API/ローカルAPIを切り替え可能）

## 主な機能

- 全米国株（NYSE、NASDAQ、AMEX等）のデータを一括取得
- SQLiteデータベースに効率的に保存
- FMP互換のRESTful APIとして提供
- API Key認証システム
- リクエストログ機能
- 既存のFMPコードを変更せずに使用可能（環境変数で切り替え）

## データベーススキーマ

以下のテーブルを含む包括的なスキーマ：

- `stock_list` - 全銘柄リスト
- `company_profile` - 企業プロファイル
- `daily_prices` - 日次株価データ
- `realtime_quotes` - リアルタイム株価
- `income_statements` - 損益計算書
- `balance_sheets` - 貸借対照表
- `cash_flow_statements` - キャッシュフロー計算書
- `financial_ratios` - 財務比率
- `key_metrics` - 主要指標
- `api_keys` - API認証キー
- `api_request_logs` - APIリクエストログ

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd fmp_data_api
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルに以下を設定：

```bash
# FMP API Key（公式API）
FMP_API_KEY=your_fmp_api_key_here

# データ取得設定
FMP_RATE_LIMIT=750
```

### 3. データベースの初期化とデータ取得

```bash
# データベースを初期化して全米国株のデータを取得
python data_fetcher.py --api-key $FMP_API_KEY --db-path ./data/fmp_data.db

# テスト用（最初の100銘柄のみ）
python data_fetcher.py --api-key $FMP_API_KEY --db-path ./data/fmp_data.db --limit 100

# 過去データと財務データをスキップ（銘柄情報とリアルタイム株価のみ）
python data_fetcher.py --api-key $FMP_API_KEY --db-path ./data/fmp_data.db --no-historical --no-financials
```

オプション：
- `--api-key`: FMP API Key
- `--db-path`: データベースファイルのパス（デフォルト: `./data/fmp_data.db`）
- `--rate-limit`: APIレート制限（デフォルト: 750）
- `--max-workers`: 並列処理のワーカー数（デフォルト: 10）
- `--limit`: 取得する銘柄数の制限（テスト用）
- `--no-historical`: 過去の株価データをスキップ
- `--no-financials`: 財務諸表データをスキップ
- `--update-quotes-only`: リアルタイム株価のみを更新

### 4. APIサーバーの起動

```bash
python api_server.py --host 0.0.0.0 --port 8000 --db-path ./data/fmp_data.db
```

オプション：
- `--host`: バインドするホスト（デフォルト: 0.0.0.0）
- `--port`: バインドするポート（デフォルト: 8000）
- `--reload`: 自動リロード（開発用）
- `--db-path`: データベースファイルのパス

### 5. API Keyの生成

```bash
# 管理者エンドポイントで新しいAPI Keyを生成
curl -X POST "http://localhost:8000/admin/api-key/create?name=my-app&rate_limit=300&admin_key=ADMIN_SECRET_KEY_CHANGE_ME"
```

レスポンス例：
```json
{
  "success": true,
  "api_key": "generated_api_key_here",
  "name": "my-app",
  "rate_limit": 300,
  "message": "API Key created successfully. Please save this key securely."
}
```

## Docker使用

### Docker Composeで起動

```bash
# リポジトリルートから
docker-compose up -d fmp_api
```

### データ取得（Dockerコンテナ内）

```bash
docker exec -it fmp_api_server python data_fetcher.py \
  --api-key $FMP_API_KEY \
  --db-path /app/data/fmp_data.db \
  --limit 100
```

## APIエンドポイント

すべてのエンドポイントはFMP APIと互換性があります。

### 認証

すべてのリクエストには`apikey`パラメータが必要です：

```
GET /api/v3/stock/list?apikey=YOUR_API_KEY
```

または、ヘッダーで指定：

```
GET /api/v3/stock/list
X-API-Key: YOUR_API_KEY
```

### 利用可能なエンドポイント

#### 1. 銘柄リスト
```
GET /api/v3/stock/list
```

#### 2. 企業プロファイル
```
GET /api/v3/profile/{symbol}
例: /api/v3/profile/AAPL
```

#### 3. リアルタイム株価
```
GET /api/v3/quote/{symbol}
GET /api/v3/quote-short/{symbol}
例: /api/v3/quote/AAPL
```

#### 4. 過去の株価データ
```
GET /api/v3/historical-price-full/{symbol}?timeseries=100
GET /api/v3/historical-price-full/{symbol}?from=2024-01-01&to=2024-12-31
例: /api/v3/historical-price-full/AAPL?timeseries=100
```

#### 5. 損益計算書
```
GET /api/v3/income-statement/{symbol}?period=quarter&limit=8
例: /api/v3/income-statement/AAPL?period=quarter&limit=8
```

#### 6. 貸借対照表
```
GET /api/v3/balance-sheet-statement/{symbol}?period=quarter&limit=8
```

#### 7. キャッシュフロー計算書
```
GET /api/v3/cash-flow-statement/{symbol}?period=quarter&limit=8
```

#### 8. 財務比率
```
GET /api/v3/ratios/{symbol}?period=quarter&limit=8
```

#### 9. 主要指標
```
GET /api/v3/key-metrics/{symbol}?period=quarter&limit=8
```

### ヘルスチェック
```
GET /health
```

### APIドキュメント

FastAPIの自動生成ドキュメントが利用可能：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## クライアントライブラリの使用

### 方法1: 環境変数で制御（推奨）

```python
from fmp_data_api import create_client

# .envファイルまたは環境変数に設定
# FMP_API_KEY=your_api_key
# FMP_USE_LOCAL=true  # trueでローカルAPI、falseで公式API
# FMP_LOCAL_URL=http://fmp_api:8000/api/v3

client = create_client()

# 使用方法は通常のFMPと同じ
profile = client.get_company_profile('AAPL')
quote = client.get_quote('AAPL')
historical = client.get_historical_prices('AAPL', timeseries=100)
```

### 方法2: 直接指定

```python
from fmp_data_api import FMPClient

# ローカルAPIを使用
client = FMPClient(
    api_key='your_local_api_key',
    use_local=True,
    local_url='http://localhost:8000/api/v3'
)

# 公式FMP APIを使用
client = FMPClient(
    api_key='your_fmp_api_key',
    use_local=False
)
```

### 方法3: 動的切り替え

```python
from fmp_data_api import FMPClient

client = FMPClient(api_key='your_api_key', use_local=False)

# 公式APIを使用
data1 = client.get_quote('AAPL')

# ローカルAPIに切り替え
client.switch_to_local('http://localhost:8000/api/v3')
data2 = client.get_quote('AAPL')

# 公式APIに戻す
client.switch_to_official()
data3 = client.get_quote('AAPL')
```

### 既存コードの移行

既存のFMPコードを変更する必要はありません。環境変数を設定するだけで切り替え可能：

```python
# 既存のコード（変更不要）
import os
import requests

api_key = os.getenv('FMP_API_KEY')
url = f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={api_key}"
response = requests.get(url)
```

↓

```python
# fmp_clientを使用（環境変数で制御）
from fmp_data_api import create_client

client = create_client()  # 環境変数から自動設定
profile = client.get_company_profile('AAPL')
```

## 定期的なデータ更新

### Cronジョブの設定

リアルタイム株価を定期的に更新：

```bash
# 1時間ごとにリアルタイム株価を更新
0 * * * * cd /app/fmp_data_api && python data_fetcher.py --api-key $FMP_API_KEY --update-quotes-only >> /app/logs/fmp_update.log 2>&1

# 毎日深夜に過去データを更新（最新100日分）
0 0 * * * cd /app/fmp_data_api && python data_fetcher.py --api-key $FMP_API_KEY --no-financials >> /app/logs/fmp_daily.log 2>&1
```

## パフォーマンス

### データ取得

- 並列処理により高速化（デフォルト10ワーカー）
- レート制限を自動管理
- 全米国株（約6,000銘柄）の基本データ取得: 約30-60分
- 過去データと財務データを含む完全取得: 約2-4時間

### APIレスポンス

- SQLiteからの高速読み取り
- インデックス最適化済み
- 平均レスポンス時間: < 100ms

## トラブルシューティング

### データベースがロックされる

```bash
# データベースファイルを確認
ls -lah ./data/fmp_data.db

# 権限を確認
chmod 666 ./data/fmp_data.db
```

### APIレート制限エラー

```bash
# レート制限を下げる
python data_fetcher.py --rate-limit 300

# ワーカー数を減らす
python data_fetcher.py --max-workers 3
```

### API認証エラー

```bash
# API Keyが有効か確認
curl "http://localhost:8000/health"

# 新しいAPI Keyを生成
curl -X POST "http://localhost:8000/admin/api-key/create?name=test&admin_key=ADMIN_SECRET_KEY_CHANGE_ME"
```

## セキュリティ

### 本番環境での注意事項

1. **管理者キーの変更**
   - `api_server.py`の`ADMIN_SECRET_KEY_CHANGE_ME`を環境変数に変更

2. **API Keyの管理**
   - 定期的なローテーション
   - レート制限の設定
   - 有効期限の設定

3. **ネットワークセキュリティ**
   - 必要に応じてファイアウォール設定
   - HTTPS/TLSの使用を推奨

## ライセンス

MIT License

## 参考資料

- [Financial Modeling Prep API Documentation](https://site.financialmodelingprep.com/developer/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
