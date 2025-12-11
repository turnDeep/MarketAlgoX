#!/usr/bin/env python
"""
チャート生成モジュール

SQLiteデータベースから株価データを取得し、Plotlyでチャートを生成します。
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
            width: チャート幅（ピクセル）
            height: チャート高さ（ピクセル）

        Returns:
            生成した画像ファイルのパス、生成失敗時はNone
        """
        # 価格データを取得
        df = self.get_price_data(ticker, months)

        if df is None or df.empty:
            return None

        try:
            # サブプロットを作成（価格チャート + 出来高）
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(f'{ticker} - {company_name}' if company_name else ticker, 'Volume'),
                row_width=[0.2, 0.7]
            )

            # ローソク足チャート
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price',
                    increasing_line_color='#26a69a',  # 緑（上昇）
                    decreasing_line_color='#ef5350'   # 赤（下降）
                ),
                row=1, col=1
            )

            # 出来高バーチャート
            colors = ['#26a69a' if row['close'] >= row['open'] else '#ef5350'
                     for _, row in df.iterrows()]

            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )

            # レイアウト設定
            fig.update_layout(
                title=dict(
                    text=f'{ticker} - {months}ヶ月チャート' if not company_name else f'{company_name} ({ticker}) - {months}ヶ月チャート',
                    font=dict(size=20, family='Arial, sans-serif')
                ),
                xaxis_rangeslider_visible=False,
                width=width,
                height=height,
                template='plotly_white',
                hovermode='x unified',
                font=dict(family='Arial, sans-serif', size=12)
            )

            # X軸の設定
            fig.update_xaxes(
                title_text="Date",
                row=2, col=1,
                gridcolor='lightgray'
            )

            # Y軸の設定
            fig.update_yaxes(
                title_text="Price ($)",
                row=1, col=1,
                gridcolor='lightgray'
            )
            fig.update_yaxes(
                title_text="Volume",
                row=2, col=1,
                gridcolor='lightgray'
            )

            # 画像として保存
            output_path = os.path.join(self.output_dir, f'{ticker}_{months}m.png')
            fig.write_image(output_path)

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
            # 終値の変化率を計算
            price_change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            color = '#26a69a' if price_change >= 0 else '#ef5350'

            # 線チャートを作成
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color=color, width=2),
                    fill='tozeroy',
                    fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
                )
            )

            # レイアウト設定
            title_text = f'{ticker}'
            if company_name:
                title_text = f'{company_name} ({ticker})'
            title_text += f' | {months}ヶ月 | {price_change:+.2f}%'

            fig.update_layout(
                title=dict(
                    text=title_text,
                    font=dict(size=18, family='Arial, sans-serif', color='#333')
                ),
                width=width,
                height=height,
                template='plotly_white',
                hovermode='x unified',
                font=dict(family='Arial, sans-serif', size=11),
                margin=dict(l=60, r=30, t=60, b=40),
                xaxis=dict(
                    gridcolor='lightgray',
                    showgrid=True
                ),
                yaxis=dict(
                    title='Price ($)',
                    gridcolor='lightgray',
                    showgrid=True
                ),
                showlegend=False
            )

            # 画像として保存
            output_path = os.path.join(self.output_dir, f'{ticker}_{months}m_simple.png')
            fig.write_image(output_path)

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
