# MarketAlgoX

米国株式市場の自動スクリーニング・AI分析・X投稿システム

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://platform.openai.com/)

## 📋 目次

- [概要](#概要)
- [主な機能](#主な機能)
- [スクリーナー一覧](#スクリーナー一覧)
- [技術スタック](#技術スタック)
- [必要なAPI Key](#必要なapi-key)
- [セットアップ](#セットアップ)
  - [XserverVPSでのセットアップ](#xservervpsでのセットアップ)
  - [ローカル環境でのセットアップ](#ローカル環境でのセットアップ)
- [使い方](#使い方)
- [ディレクトリ構成](#ディレクトリ構成)
- [トラブルシューティング](#トラブルシューティング)
- [関連ドキュメント](#関連ドキュメント)

## 概要

MarketAlgoXは、FinancialModelingPrep APIから米国株式データを取得し、IBD（Investor's Business Daily）スタイルのスクリーニングを実行し、OpenAI GPT-4.1のAI分析を経てX (Twitter)に自動投稿するシステムです。

**動作スケジュール**: 毎日朝6時（日本時間、火〜土曜）に自動実行

## 主な機能

- 🗂️ **データ収集**: FinancialModelingPrep APIから株価・財務データを取得
- 📊 **レーティング計算**: RS Rating、EPS Rating、Composite Rating等のIBDレーティングを計算
- 🔍 **スクリーニング**: 6つのIBDスクリーナーで有望銘柄を抽出
- 💾 **JSON出力**: 日次スクリーニング結果をJSON形式で保存（`YYYYMMDD.json`）
- 🤖 **AI分析**: OpenAI GPT-4.1が各スクリーナーでオススメ銘柄を選定し、Industry Group傾向を分析
- 🐦 **X投稿**: 分析結果を自動的にX (Twitter)に投稿（個別ツイート×6、日本語140文字対応）
- ⏰ **自動実行**: Cronで毎日朝6時（日本時間、火〜土曜）に自動実行

## スクリーナー一覧

| 日本語名 | 英語名 | 説明 |
|---------|--------|------|
| 短期中期長期の最強銘柄 | Momentum 97 | 短期・中期・長期すべてでトップパフォーマンスの銘柄 |
| 爆発的EPS成長銘柄 | Explosive Estimated EPS Growth Stocks | 爆発的なEPS成長を示す強気銘柄 |
| 出来高急増上昇銘柄 | Up on Volume List | 出来高を伴って上昇している銘柄 |
| 相対強度トップ2%銘柄 | Top 2% RS Rating List | 相対的強さが極めて高い銘柄 |
| 急騰直後銘柄 | 4% Bullish Yesterday | 前日に強い上昇を見せた銘柄 |
| 健全チャート銘柄 | Healthy Chart Watch List | 健全なチャートパターンを持つ銘柄 |

## 技術スタック

- **言語**: Python 3.12
- **AI**: OpenAI GPT-4o API (openai==1.107.1)
- **データソース**: FinancialModelingPrep API
- **SNS**: X (Twitter) API v2
- **インフラ**: Docker + Docker Compose + Cron
- **データベース**: SQLite
- **主要ライブラリ**: pandas==2.1.4, requests, tweepy, python-dotenv==0.21.0

## 必要なAPI Key

### 1. FinancialModelingPrep API

1. https://financialmodelingprep.com/ にアクセス
2. アカウント作成
3. **Premium Plan ($29/月) 以上を契約**（推奨: 750 req/min）
4. ダッシュボードからAPI Keyを取得

### 2. OpenAI API

1. https://platform.openai.com/ にアクセス
2. アカウントでログイン
3. "API Keys" セクションに移動
4. "Create new secret key" をクリック
5. API Keyをコピーして安全に保存

**注意**: GPT-4oの使用には課金が必要です。

### 3. X (Twitter) API

1. https://developer.twitter.com/ にアクセス
2. Developer Portalでアプリを作成
3. **OAuth 1.0a** の認証情報を取得:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
4. App permissionsを **"Read and Write"** に設定

## セットアップ

### XserverVPSでのセットアップ

XserverVPS（またはConoHa VPS、さくらのVPS等のLinux VPS）で運用する手順です。

#### 1. VPSにSSH接続

```bash
# XserverVPSのコンソールまたはローカルターミナルから接続
ssh root@your-server-ip

# または
ssh username@your-server-ip
```

#### 2. システムのアップデート

```bash
# パッケージリストを更新
sudo apt update && sudo apt upgrade -y
```

#### 3. Dockerのインストール（未インストールの場合）

```bash
# Dockerの公式インストールスクリプトを実行
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Composeのインストール
sudo apt install docker-compose -y

# Dockerサービスの起動と自動起動設定
sudo systemctl start docker
sudo systemctl enable docker

# 動作確認
docker --version
docker-compose --version
```

#### 4. Gitのインストール（未インストールの場合）

```bash
sudo apt install git -y
```

#### 5. リポジトリのクローン

```bash
# ホームディレクトリに移動
cd ~

# リポジトリをクローン
git clone https://github.com/turnDeep/MarketAlgoX.git
cd MarketAlgoX
```

#### 6. 環境変数の設定

```bash
# .env.exampleを.envにコピー
cp .env.example .env

# .envファイルを編集
nano .env
# または
vi .env
```

`.env`ファイルの設定例:
```bash
# FMP API Key
FMP_API_KEY=your_actual_fmp_api_key_here
FMP_RATE_LIMIT=750

# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o

# X (Twitter) API Keys
X_API_KEY=your_actual_x_api_key_here
X_API_SECRET=your_actual_x_api_secret_here
X_ACCESS_TOKEN=your_actual_x_access_token_here
X_ACCESS_TOKEN_SECRET=your_actual_x_access_token_secret_here

# Oratnek Screener Settings
ORATNEK_MAX_WORKERS=6

# Database
IBD_DB_PATH=./data/ibd_data.db
```

**保存方法**:
- `nano`の場合: `Ctrl + O` → Enter → `Ctrl + X`
- `vi`の場合: `Esc` → `:wq` → Enter

#### 7. データディレクトリの作成

```bash
# データとログディレクトリを作成
mkdir -p data/screener_results
mkdir -p logs
```

#### 8. Dockerコンテナの起動

```bash
# Dockerイメージをビルド
docker-compose build

# コンテナをバックグラウンドで起動
docker-compose up -d

# 起動確認
docker-compose ps
```

#### 9. ログの確認

```bash
# コンテナのログをリアルタイムで表示
docker-compose logs -f

# Cronログを確認
docker-compose exec app tail -f /app/logs/cron.log

# アプリケーションログを確認
docker-compose exec app tail -f /app/logs/app.log
```

#### 10. 手動テスト実行（オプション）

```bash
# コンテナ内に入る
docker-compose exec app bash

# 日次ワークフローを手動実行
python scripts/daily_workflow.py

# コンテナから退出
exit
```

#### 11. 自動実行の確認

```bash
# Cronジョブが登録されているか確認
docker-compose exec app crontab -l

# 出力例:
# TZ=Asia/Tokyo
# 0 6 * * 2-6 root cd /app && python /app/scripts/daily_workflow.py >> /app/logs/cron.log 2>> /app/logs/error.log
```

#### 12. ファイアウォール設定（必要に応じて）

XserverVPSではファイアウォールの設定が必要な場合があります。

```bash
# UFWの場合（ポート開放は不要ですが、SSH用に22番を許可）
sudo ufw allow 22/tcp
sudo ufw enable
sudo ufw status
```

**注意**: MarketAlgoXは外部からのアクセスを受け付けないため、特別なポート開放は不要です。

#### XserverVPS固有の注意点

- **メモリ**: 最低2GB以上のプランを推奨（4GB以上が理想）
- **ストレージ**: 50GB以上推奨（データとログの蓄積のため）
- **タイムゾーン**: Dockerコンテナ内で自動的にAsia/Tokyoに設定されます
- **再起動**: サーバー再起動時にDockerコンテナも自動起動する設定:

```bash
# docker-compose.ymlに以下が含まれていることを確認
# restart: unless-stopped
```

- **バックアップ**: 定期的に`data/`ディレクトリをバックアップしてください

```bash
# バックアップコマンド例
tar -czf marketalgox_backup_$(date +%Y%m%d).tar.gz data/ .env
```

### ローカル環境でのセットアップ

ローカルPC（Mac/Linux/Windows）でDockerを使用して実行する手順です。

#### 1. 前提条件

- Docker Desktop がインストールされていること
- Git がインストールされていること

#### 2. リポジトリのクローン

```bash
git clone https://github.com/turnDeep/MarketAlgoX.git
cd MarketAlgoX
```

#### 3. 環境変数の設定

```bash
# .env.exampleを.envにコピー
cp .env.example .env

# .envファイルを編集してAPI Keyを設定
# macOS/Linux
nano .env

# Windows
notepad .env
```

#### 4. Dockerコンテナの起動

```bash
# Dockerイメージをビルド
docker-compose build

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

#### 5. 手動テスト実行

```bash
# コンテナ内に入る
docker-compose exec app bash

# 日次ワークフローを手動実行
python scripts/daily_workflow.py

# 退出
exit
```

## 使い方

### 自動実行

デフォルトでは、毎日朝6時（日本時間、火〜土曜）に自動実行されます。

**Cron設定**:
```cron
TZ=Asia/Tokyo
0 6 * * 2-6 root cd /app && python /app/scripts/daily_workflow.py >> /app/logs/cron.log 2>> /app/logs/error.log
```

**実行曜日の理由**:
- 火曜〜土曜: 米国市場の営業日（月〜金）の翌日にデータを取得

### 手動実行

```bash
# 日次ワークフロー全体を実行
docker-compose exec app python scripts/daily_workflow.py

# または、コンテナ内で実行
docker-compose exec app bash
python scripts/daily_workflow.py
```

### 個別コンポーネントの実行

```bash
# データ収集のみ実行
docker-compose exec app python run_ibd_screeners.py --collect-data

# レーティング計算のみ実行
docker-compose exec app python run_ibd_screeners.py --calculate-ratings

# スクリーナーのみ実行
docker-compose exec app python run_ibd_screeners.py --run-screeners
```

### コンテナの管理

```bash
# コンテナの状態確認
docker-compose ps

# コンテナの停止
docker-compose stop

# コンテナの起動
docker-compose start

# コンテナの再起動
docker-compose restart

# コンテナの削除（データは残る）
docker-compose down

# コンテナとイメージの完全削除
docker-compose down --rmi all

# ログの確認
docker-compose logs -f

# 特定のサービスのログのみ表示
docker-compose logs -f app
```

## ディレクトリ構成

```
MarketAlgoX/
├── SYSTEM_SPECIFICATION.md    # システム開発仕様書 v1.2.0
├── README.md                   # このファイル
├── Dockerfile                  # Docker設定
├── docker-compose.yml          # Docker Compose設定
├── requirements.txt            # Python依存関係
├── .env.example                # 環境変数テンプレート
├── .env                        # 環境変数（要作成、gitignore対象）
│
├── scripts/                    # スクリプト
│   ├── startup.sh              # コンテナ起動スクリプト
│   └── daily_workflow.py       # 日次ワークフロー
│
├── src/                        # ソースコード
│   ├── screeners/              # スクリーナーモジュール
│   │   └── screener_names.py   # スクリーナー名称定義
│   ├── json_export/            # JSON出力モジュール
│   │   └── exporter.py         # JSON出力ロジック
│   ├── ai_analysis/            # AI分析モジュール
│   │   └── analyzer.py         # OpenAI GPT-4o分析
│   └── social_posting/         # 投稿モジュール
│       └── poster.py           # X投稿ロジック
│
├── data/                       # データディレクトリ
│   ├── ibd_data.db             # SQLiteデータベース
│   └── screener_results/       # スクリーニング結果JSON
│       ├── 20251211.json
│       ├── 20251212.json
│       └── ...
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

## JSON出力フォーマット

スクリーニング結果は `data/screener_results/YYYYMMDD.json` に保存されます。

**ファイル名例**: `20251211.json`

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
          }
        }
      ]
    }
  ],
  "summary": {
    "total_screeners": 6,
    "total_unique_tickers": 45,
    "total_new_tickers": 12,
    "industry_distribution": {
      "Technology": 15,
      "Healthcare": 8
    }
  }
}
```

## X投稿フォーマット

各スクリーナーごとに個別のツイートが投稿されます（合計6ツイート）。

**ツイート形式**:
```
【短期中期長期の最強銘柄】
💡 $AAPL
AI分析による上昇理由（30文字以内）

その他
$NVDA $MSFT $GOOGL ...

傾向
Technology業界が優勢
```

**仕様**:
- 日本語140文字制限に自動対応
- トップ推奨銘柄: AIが選定した1銘柄
- その他: 最大10銘柄（多い場合はAIが選定）
- 傾向: Industry Groupの分析結果

## トラブルシューティング

### 1. Cronが実行されない

**原因**: Cronサービスが起動していない

**解決方法**:
```bash
# Cronサービスの状態を確認
docker-compose exec app service cron status

# Cronサービスを再起動
docker-compose exec app service cron restart

# Cronログを確認
docker-compose exec app tail -f /app/logs/cron.log
```

### 2. API制限エラー

**原因**: FMP APIのレート制限を超えた

**解決方法**:
```bash
# .envファイルでMAX_WORKERSを調整
nano .env

# Starter Plan (300 req/min): ORATNEK_MAX_WORKERS=3
# Premium Plan (750 req/min): ORATNEK_MAX_WORKERS=6
# Professional Plan (1500 req/min): ORATNEK_MAX_WORKERS=10

# コンテナを再起動
docker-compose restart
```

### 3. OpenAI API エラー

**原因**: APIキーが無効、または残高不足

**解決方法**:
```bash
# APIキーを確認
cat .env | grep OPENAI_API_KEY

# OpenAIのダッシュボードで残高とAPIキーを確認
# https://platform.openai.com/account/usage
```

### 4. X投稿エラー

**原因**: Twitter APIの認証情報が間違っている

**解決方法**:
```bash
# 認証情報を確認
cat .env | grep X_

# Twitter Developer Portalで認証情報を再確認
# https://developer.twitter.com/en/portal/dashboard

# App permissionsが "Read and Write" になっているか確認
```

### 5. データベースエラー

**原因**: データベースファイルが破損している

**解決方法**:
```bash
# データベースを削除して再作成
docker-compose exec app rm /app/data/ibd_data.db

# データ収集を再実行
docker-compose exec app python run_ibd_screeners.py --collect-data
```

### 6. メモリ不足エラー

**原因**: VPSのメモリが不足している

**解決方法**:
- より大きなメモリプランにアップグレード（推奨: 4GB以上）
- `ORATNEK_MAX_WORKERS` を減らす
- 不要なプロセスを停止

### 7. タイムゾーンがずれている

**原因**: コンテナのタイムゾーン設定が正しくない

**確認方法**:
```bash
# コンテナ内の時刻を確認
docker-compose exec app date

# 日本時間（JST）になっているか確認
```

**解決方法**:
- `Dockerfile`に`ENV TZ=Asia/Tokyo`が設定されていることを確認
- コンテナを再ビルド: `docker-compose up -d --build`

## システム要件

### VPSサーバー（推奨）

- **CPU**: 2コア以上
- **メモリ**: 4GB以上推奨（最低2GB）
- **ストレージ**: 50GB以上
- **OS**: Ubuntu 20.04 LTS / 22.04 LTS / Debian 11+
- **ネットワーク**: 常時接続

### ローカル環境

- **Docker Desktop**: 最新版
- **メモリ**: 8GB以上推奨
- **ストレージ**: 10GB以上の空き容量

## セキュリティ

### API Keyの管理

- `.env`ファイルは**絶対にGitにコミットしない**（`.gitignore`に含まれています）
- API Keyは定期的にローテーション
- サーバーへのSSH接続は公開鍵認証を推奨

### ファイアウォール

- 不要なポートは閉じる
- SSH（22番）のみ許可で十分

### バックアップ

```bash
# 定期的にデータをバックアップ
cd ~/MarketAlgoX
tar -czf backup_$(date +%Y%m%d).tar.gz data/ .env

# バックアップをローカルにダウンロード
scp username@your-server-ip:~/MarketAlgoX/backup_*.tar.gz ./
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

質問や問題がある場合:
1. [Issues](https://github.com/turnDeep/MarketAlgoX/issues) で既存の問題を検索
2. 新しいissueを作成
3. [システム開発仕様書](SYSTEM_SPECIFICATION.md) を参照

## 関連ドキュメント

- [システム開発仕様書](SYSTEM_SPECIFICATION.md) - v1.2.0
- [FinancialModelingPrep API Docs](https://site.financialmodelingprep.com/developer/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Docker Documentation](https://docs.docker.com/)

---

**作成者**: Claude
**バージョン**: 1.2.0
**最終更新**: 2025-12-11
