#!/usr/bin/env python
"""
チャート生成モジュール

SQLiteデータベースから株価データを取得し、mplfinanceでチャートを生成します。
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt


class ChartGenerator:
    """株価チャート生成クラス"""

    def __init__(self, db_path: str = './data/ibd_data.db', output_dir: str = './data/charts'):
        """
        初期化

        Args:
            db_path: データベースパス
            output_dir: チャート画像出力ディレクトリ
        """
        self.db_path = db_path
        self.output_dir = output_dir

        # 出力ディレクトリを作成
        os.makedirs(self.output_dir, exist_ok=True)

    def get_price_data(self, ticker: str, months: int = 3) -> Optional[pd.DataFrame]:
        """
        SQLiteから株価データを取得

        Args:
            ticker: ティッカーシンボル
            months: 取得する月数（デフォルト: 3ヶ月）

        Returns:
            株価データのDataFrame、データがない場合はNone
        """
        try:
            # 3ヶ月前の日付を計算
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            # データベース接続
            conn = sqlite3.connect(self.db_path)

            # SQLクエリ
            query = """
                SELECT date, open, high, low, close, volume
                FROM price_history
                WHERE ticker = ?
                  AND date >= ?
                  AND date <= ?
                ORDER BY date ASC
            """

            # データ取得
            df = pd.read_sql_query(
                query,
                conn,
                params=(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            )

            conn.close()

            if df.empty:
                print(f"Warning: No price data found for {ticker}")
                return None

            # 日付をdatetime型に変換
            df['date'] = pd.to_datetime(df['date'])

            # mplfinanceにはDatetimeIndexが必要
            df.set_index('date', inplace=True)
            df.index.name = 'Date'

            # カラム名をmplfinanceの期待する形式に（Open, High, Low, Close, Volume）
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)

            return df

        except Exception as e:
            print(f"Error getting price data for {ticker}: {e}")
            return None

    def generate_candlestick_chart(
        self,
        ticker: str,
        company_name: str = "",
        months: int = 3,
        width: int = 1200,
        height: int = 600
    ) -> Optional[str]:
        """
        ローソク足チャートを生成

        Args:
            ticker: ティッカーシンボル
            company_name: 会社名（チャートタイトル用）
            months: 表示する月数（デフォルト: 3ヶ月）
            width: チャート幅（ピクセル）- mplfinanceではfigsize (inch) を使用するため概算変換
            height: チャート高さ（ピクセル）

        Returns:
            生成した画像ファイルのパス、生成失敗時はNone
        """
        # 価格データを取得
        df = self.get_price_data(ticker, months)

        if df is None or df.empty:
            return None

        try:
            output_path = os.path.join(self.output_dir, f'{ticker}_{months}m.png')

            # 終値の変化率を計算
            price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100

            # タイトル作成
            title = f'{company_name} ({ticker})' if company_name else ticker
            title += f' | {months} months | {price_change:+.2f}%'

            # スタイル設定
            # IBDスタイルに近いものを作成するか、既存のスタイルを使用
            # 緑色と赤色を使用
            mc = mpf.make_marketcolors(up='#00c853', down='#ff1744', edge='inherit', wick='inherit', volume='in')
            s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=True)

            # ピクセルをインチに変換 (100 dpiと仮定)
            dpi = 100
            figsize = (width / dpi, height / dpi)

            # EMA計算 (High/Lowの21期間)
            ema_high = df['High'].ewm(span=21, adjust=False).mean()
            ema_low = df['Low'].ewm(span=21, adjust=False).mean()

            # チャート生成 (returnfig=TrueでFigureオブジェクトを取得)
            fig, axlist = mpf.plot(
                df,
                type='candle',
                volume=True,
                title=title,
                style=s,
                figsize=figsize,
                returnfig=True
            )

            # メインチャートの軸を取得
            ax = axlist[0]

            # x軸の値を生成 (mplfinanceの内部表現に合わせる)
            x_vals = np.arange(len(df))

            # EMAプロット
            ax.plot(x_vals, ema_high, color='gray', linewidth=1, alpha=0.5)
            ax.plot(x_vals, ema_low, color='gray', linewidth=1, alpha=0.5)

            # クラウドの塗りつぶし条件
            fill_green = (df['Close'] > ema_high).values
            fill_red = (df['Close'] < ema_low).values
            fill_gray = ~(fill_green | fill_red)

            alpha = 0.36 # Pine Scriptのtransparency 64 (alpha ~0.36)

            # 塗りつぶし
            ax.fill_between(x_vals, ema_high, ema_low, where=fill_green, color='#00c853', alpha=alpha) # Green
            ax.fill_between(x_vals, ema_high, ema_low, where=fill_red, color='#ff1744', alpha=alpha)   # Red
            ax.fill_between(x_vals, ema_high, ema_low, where=fill_gray, color='gray', alpha=alpha)

            # 保存
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
            plt.close(fig)

            print(f"Chart generated successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error generating chart for {ticker}: {e}")
            return None

    def generate_simple_line_chart(
        self,
        ticker: str,
        company_name: str = "",
        months: int = 3,
        width: int = 1200,
        height: int = 400
    ) -> Optional[str]:
        """
        シンプルな線チャートを生成（ツイート用の軽量版）

        Args:
            ticker: ティッカーシンボル
            company_name: 会社名
            months: 表示する月数
            width: チャート幅
            height: チャート高さ

        Returns:
            生成した画像ファイルのパス
        """
        # 価格データを取得
        df = self.get_price_data(ticker, months)

        if df is None or df.empty:
            return None

        try:
            output_path = os.path.join(self.output_dir, f'{ticker}_{months}m_simple.png')

            # 終値の変化率を計算
            price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
            color = '#26a69a' if price_change >= 0 else '#ef5350'
            fill_color = color  # alpha is handled by matplotlib

            # プロット設定
            dpi = 100
            figsize = (width / dpi, height / dpi)

            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

            # 線グラフ
            ax.plot(df.index, df['Close'], color=color, linewidth=2)

            # 下部を塗りつぶし
            ax.fill_between(df.index, df['Close'], df['Close'].min() * 0.99, color=fill_color, alpha=0.1)

            # タイトル
            title_text = f'{ticker}'
            if company_name:
                title_text = f'{company_name} ({ticker})'
            title_text += f' | {months} months | {price_change:+.2f}%'

            ax.set_title(title_text, fontsize=18, color='#333333')

            # 軸の設定
            ax.set_ylabel('Price ($)', fontsize=12)
            ax.grid(True, linestyle=':', alpha=0.6)

            # マージン調整
            plt.tight_layout()

            # 保存
            plt.savefig(output_path, dpi=dpi)
            plt.close(fig)

            print(f"Simple chart generated successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error generating simple chart for {ticker}: {e}")
            return None

    def cleanup_old_charts(self, days: int = 7):
        """
        古いチャート画像を削除

        Args:
            days: この日数より古いファイルを削除
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)

            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)

                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))

                    if file_time < cutoff_time:
                        os.remove(filepath)
                        print(f"Deleted old chart: {filename}")

        except Exception as e:
            print(f"Error cleaning up old charts: {e}")


def main():
    """テスト用メイン関数"""
    import sys

    # 引数チェック
    if len(sys.argv) < 2:
        print("Usage: python generator.py <TICKER> [COMPANY_NAME]")
        sys.exit(1)

    ticker = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 else ""

    # チャート生成
    generator = ChartGenerator()

    print(f"Generating charts for {ticker}...")

    # ローソク足チャート
    candlestick_path = generator.generate_candlestick_chart(ticker, company_name)
    if candlestick_path:
        print(f"✓ Candlestick chart: {candlestick_path}")

    # シンプル線チャート
    simple_path = generator.generate_simple_line_chart(ticker, company_name)
    if simple_path:
        print(f"✓ Simple chart: {simple_path}")


if __name__ == "__main__":
    main()
