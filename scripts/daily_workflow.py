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
import logging
from datetime import datetime
from dotenv import load_dotenv

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ibd_data_collector import IBDDataCollector
from ibd_ratings_calculator import IBDRatingsCalculator
from ibd_database import IBDDatabase
from src.json_export.exporter import JSONExporter
from src.ai_analysis.analyzer import ScreenerAnalyzer
from src.social_posting.poster import XPoster
from src.screeners.screener_names import get_screener_info


def setup_logger():
    """ロガーをセットアップ"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('./logs/app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def run_screeners(db_path: str) -> dict:
    """
    スクリーナーを実行

    Args:
        db_path: データベースパス

    Returns:
        {スクリーナー名: [銘柄リスト]}
    """
    from ibd_screeners import IBDScreeners

    # 既存のIBDScreenersを使用してスクリーナーを実行
    # Note: Googleスプレッドシート出力は省略し、結果だけを返す
    screeners_obj = IBDScreeners(
        credentials_file=os.getenv('CREDENTIALS_FILE', 'credentials.json'),
        spreadsheet_name=os.getenv('SPREADSHEET_NAME', 'Market Dashboard'),
        db_path=db_path
    )

    # ベンチマークデータの確認
    if not screeners_obj.ensure_benchmark_data('SPY'):
        logger.warning("SPYデータが取得できませんでした")

    # 各スクリーナーを実行
    results = {
        "短期中期長期の最強銘柄": screeners_obj.screener_momentum_97(),
        "爆発的EPS成長銘柄": screeners_obj.screener_explosive_eps_growth(),
        "出来高急増上昇銘柄": screeners_obj.screener_up_on_volume(),
        "相対強度トップ2%銘柄": screeners_obj.screener_top_2_percent_rs(),
        "急騰直後銘柄": screeners_obj.screener_4_percent_bullish_yesterday(),
        "健全チャート銘柄": screeners_obj.screener_healthy_chart_watchlist()
    }

    screeners_obj.close()
    return results


def main():
    """メイン処理"""
    global logger
    logger = setup_logger()

    logger.info("=" * 80)
    logger.info("MarketAlgoX Daily Workflow 開始")
    logger.info(f"実行時刻: {datetime.now()}")
    logger.info("=" * 80)

    # 環境変数読み込み
    load_dotenv()

    FMP_API_KEY = os.getenv('FMP_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    X_API_KEY = os.getenv('X_API_KEY')
    X_API_SECRET = os.getenv('X_API_SECRET')
    X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
    DB_PATH = os.getenv('IBD_DB_PATH', './data/ibd_data.db')
    MAX_WORKERS = int(os.getenv('ORATNEK_MAX_WORKERS', '6'))

    # API KEYのチェック
    if not FMP_API_KEY or FMP_API_KEY == 'your_fmp_api_key_here':
        logger.error("FMP_API_KEYが設定されていません")
        sys.exit(1)

    try:
        # ステップ1: データ収集
        logger.info("\n[1/6] データ収集フェーズ開始")
        collector = IBDDataCollector(FMP_API_KEY, db_path=DB_PATH)
        collector.run_full_collection(
            use_full_dataset=True,
            max_workers=MAX_WORKERS
        )
        collector.close()
        logger.info("データ収集完了")

        # ステップ2: レーティング計算
        logger.info("\n[2/6] レーティング計算フェーズ開始")
        calculator = IBDRatingsCalculator(db_path=DB_PATH)
        calculator.calculate_all_ratings()
        calculator.close()
        logger.info("レーティング計算完了")

        # ステップ3: スクリーニング
        logger.info("\n[3/6] スクリーニングフェーズ開始")
        results = run_screeners(DB_PATH)
        logger.info(f"スクリーニング完了: {len(results)} スクリーナー実行")

        # ステップ4: JSON出力
        logger.info("\n[4/6] JSON出力フェーズ開始")
        exporter = JSONExporter(db_path=DB_PATH)
        today_date = datetime.now().strftime("%Y%m%d")

        # 前日結果を読み込み
        previous_results = exporter.load_previous_results(today_date)

        json_file = exporter.export_screening_results(
            date=today_date,
            screener_results=results,
            previous_results=previous_results
        )
        exporter.close()
        logger.info(f"JSON出力完了: {json_file}")

        # ステップ5: AI分析
        if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here':
            logger.info("\n[5/6] AI分析フェーズ開始")
            analyzer = ScreenerAnalyzer(OPENAI_API_KEY, OPENAI_MODEL)
            analysis = analyzer.analyze_screening_results(json_file)
            logger.info("AI分析完了")

            # ステップ6: X投稿
            if all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]) and \
               X_API_KEY != 'your_x_api_key_here':
                logger.info("\n[6/6] X投稿フェーズ開始")
                poster = XPoster(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
                post_results = poster.post_analysis_result(analysis)
                success_count = sum(1 for r in post_results if r.get("success"))
                logger.info(f"X投稿完了: {success_count}/{len(post_results)} 成功")
            else:
                logger.warning("X API認証情報が設定されていないため、投稿をスキップします")
        else:
            logger.warning("OPENAI_API_KEYが設定されていないため、AI分析と投稿をスキップします")

        logger.info("\n" + "=" * 80)
        logger.info("MarketAlgoX Daily Workflow 正常終了")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
