"""
FMP Data API - API Server
FMP互換のAPIサーバー（FastAPIを使用）
"""

from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime

from database import FMPDatabase


# FastAPIアプリの作成
app = FastAPI(
    title="FMP Compatible API Server",
    description="FMP互換のローカルAPIサーバー。データベースから株式データを提供します。",
    version="1.0.0"
)

# データベースインスタンス
db = None

# API認証設定
api_key_query = APIKeyQuery(name="apikey", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_database():
    """データベースインスタンスを取得"""
    global db
    if db is None:
        db = FMPDatabase('./data/fmp_data.db')
    return db


async def verify_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header)
) -> Dict:
    """APIキーを検証"""
    api_key = api_key_query or api_key_header

    if not api_key:
        raise HTTPException(status_code=403, detail="API Key is required")

    database = get_database()
    key_info = database.verify_api_key(api_key)

    if not key_info:
        raise HTTPException(status_code=403, detail="Invalid or expired API Key")

    return key_info


def log_request(key_info: Dict, endpoint: str, params: Dict, response_code: int):
    """リクエストをログに記録"""
    database = get_database()
    database.log_api_request(
        api_key_id=key_info['id'],
        endpoint=endpoint,
        params=params,
        response_code=response_code
    )


# ==================== エンドポイント ====================

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "FMP Compatible API Server",
        "version": "1.0.0",
        "endpoints": {
            "stock_list": "/api/v3/stock/list",
            "company_profile": "/api/v3/profile/{symbol}",
            "quote": "/api/v3/quote/{symbol}",
            "historical_prices": "/api/v3/historical-price-full/{symbol}",
            "income_statement": "/api/v3/income-statement/{symbol}",
            "balance_sheet": "/api/v3/balance-sheet-statement/{symbol}",
            "cash_flow": "/api/v3/cash-flow-statement/{symbol}",
            "ratios": "/api/v3/ratios/{symbol}",
            "key_metrics": "/api/v3/key-metrics/{symbol}"
        }
    }


@app.get("/api/v3/stock/list")
async def get_stock_list(
    key_info: Dict = Depends(verify_api_key)
):
    """
    全銘柄リストを取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/stock/list
    """
    database = get_database()

    try:
        stocks = database.get_stock_list()
        log_request(key_info, "/api/v3/stock/list", {}, 200)
        return stocks
    except Exception as e:
        log_request(key_info, "/api/v3/stock/list", {}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/profile/{symbol}")
async def get_company_profile(
    symbol: str,
    key_info: Dict = Depends(verify_api_key)
):
    """
    企業プロファイルを取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/profile/{symbol}
    """
    database = get_database()

    try:
        profile = database.get_company_profile(symbol.upper())

        if not profile:
            log_request(key_info, f"/api/v3/profile/{symbol}", {}, 404)
            raise HTTPException(status_code=404, detail="Company profile not found")

        log_request(key_info, f"/api/v3/profile/{symbol}", {}, 200)
        return [profile]  # FMPはリストで返す

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/profile/{symbol}", {}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/quote/{symbol}")
async def get_realtime_quote(
    symbol: str,
    key_info: Dict = Depends(verify_api_key)
):
    """
    リアルタイム株価を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/quote/{symbol}
    """
    database = get_database()

    try:
        quote = database.get_realtime_quote(symbol.upper())

        if not quote:
            log_request(key_info, f"/api/v3/quote/{symbol}", {}, 404)
            raise HTTPException(status_code=404, detail="Quote not found")

        log_request(key_info, f"/api/v3/quote/{symbol}", {}, 200)
        return [quote]  # FMPはリストで返す

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/quote/{symbol}", {}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/quote-short/{symbol}")
async def get_realtime_quote_short(
    symbol: str,
    key_info: Dict = Depends(verify_api_key)
):
    """
    リアルタイム株価を取得（簡易版）

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/quote-short/{symbol}
    """
    database = get_database()

    try:
        quote = database.get_realtime_quote(symbol.upper())

        if not quote:
            log_request(key_info, f"/api/v3/quote-short/{symbol}", {}, 404)
            raise HTTPException(status_code=404, detail="Quote not found")

        # 簡易版は価格とボリュームのみ
        short_quote = {
            'symbol': quote.get('symbol'),
            'price': quote.get('price'),
            'volume': quote.get('volume')
        }

        log_request(key_info, f"/api/v3/quote-short/{symbol}", {}, 200)
        return [short_quote]

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/quote-short/{symbol}", {}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/historical-price-full/{symbol}")
async def get_historical_prices(
    symbol: str,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    timeseries: Optional[int] = Query(None, description="Number of days to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    過去の株価データを取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}
    """
    database = get_database()

    try:
        prices = database.get_daily_prices(
            symbol=symbol.upper(),
            from_date=from_date,
            to_date=to_date
        )

        if not prices:
            log_request(key_info, f"/api/v3/historical-price-full/{symbol}",
                       {"from": from_date, "to": to_date, "timeseries": timeseries}, 404)
            raise HTTPException(status_code=404, detail="Historical prices not found")

        # timeseriesパラメータが指定されている場合は制限
        if timeseries:
            prices = prices[:timeseries]

        # FMP形式に変換
        response = {
            "symbol": symbol.upper(),
            "historical": prices
        }

        log_request(key_info, f"/api/v3/historical-price-full/{symbol}",
                   {"from": from_date, "to": to_date, "timeseries": timeseries}, 200)
        return response

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/historical-price-full/{symbol}",
                   {"from": from_date, "to": to_date, "timeseries": timeseries}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/income-statement/{symbol}")
async def get_income_statement(
    symbol: str,
    period: str = Query("quarter", description="annual or quarter"),
    limit: int = Query(8, description="Number of statements to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    損益計算書を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/income-statement/{symbol}
    """
    database = get_database()

    try:
        statements = database.get_income_statements(
            symbol=symbol.upper(),
            period=period,
            limit=limit
        )

        if not statements:
            log_request(key_info, f"/api/v3/income-statement/{symbol}",
                       {"period": period, "limit": limit}, 404)
            raise HTTPException(status_code=404, detail="Income statements not found")

        log_request(key_info, f"/api/v3/income-statement/{symbol}",
                   {"period": period, "limit": limit}, 200)
        return statements

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/income-statement/{symbol}",
                   {"period": period, "limit": limit}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/balance-sheet-statement/{symbol}")
async def get_balance_sheet(
    symbol: str,
    period: str = Query("quarter", description="annual or quarter"),
    limit: int = Query(8, description="Number of statements to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    貸借対照表を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}
    """
    database = get_database()

    try:
        # TODO: データベースにクエリメソッドを追加
        log_request(key_info, f"/api/v3/balance-sheet-statement/{symbol}",
                   {"period": period, "limit": limit}, 501)
        raise HTTPException(status_code=501, detail="Not implemented yet")

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/balance-sheet-statement/{symbol}",
                   {"period": period, "limit": limit}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/cash-flow-statement/{symbol}")
async def get_cash_flow_statement(
    symbol: str,
    period: str = Query("quarter", description="annual or quarter"),
    limit: int = Query(8, description="Number of statements to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    キャッシュフロー計算書を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}
    """
    database = get_database()

    try:
        # TODO: データベースにクエリメソッドを追加
        log_request(key_info, f"/api/v3/cash-flow-statement/{symbol}",
                   {"period": period, "limit": limit}, 501)
        raise HTTPException(status_code=501, detail="Not implemented yet")

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/cash-flow-statement/{symbol}",
                   {"period": period, "limit": limit}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/ratios/{symbol}")
async def get_financial_ratios(
    symbol: str,
    period: str = Query("quarter", description="annual or quarter"),
    limit: int = Query(8, description="Number of ratios to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    財務比率を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/ratios/{symbol}
    """
    database = get_database()

    try:
        # TODO: データベースにクエリメソッドを追加
        log_request(key_info, f"/api/v3/ratios/{symbol}",
                   {"period": period, "limit": limit}, 501)
        raise HTTPException(status_code=501, detail="Not implemented yet")

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/ratios/{symbol}",
                   {"period": period, "limit": limit}, 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/key-metrics/{symbol}")
async def get_key_metrics(
    symbol: str,
    period: str = Query("quarter", description="annual or quarter"),
    limit: int = Query(8, description="Number of metrics to retrieve"),
    key_info: Dict = Depends(verify_api_key)
):
    """
    主要指標を取得

    FMP互換エンドポイント: https://financialmodelingprep.com/api/v3/key-metrics/{symbol}
    """
    database = get_database()

    try:
        # TODO: データベースにクエリメソッドを追加
        log_request(key_info, f"/api/v3/key-metrics/{symbol}",
                   {"period": period, "limit": limit}, 501)
        raise HTTPException(status_code=501, detail="Not implemented yet")

    except HTTPException:
        raise
    except Exception as e:
        log_request(key_info, f"/api/v3/key-metrics/{symbol}",
                   {"period": period, "limit": limit}, 500)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 管理エンドポイント ====================

@app.post("/admin/api-key/create")
async def create_api_key(
    name: str,
    description: Optional[str] = None,
    rate_limit: int = 300,
    admin_key: str = Query(..., description="Admin API Key")
):
    """
    新しいAPIキーを作成（管理者用）
    """
    import secrets

    # 管理者キーの検証（環境変数から取得すべき）
    # TODO: 環境変数からADMIN_KEYを取得
    if admin_key != "ADMIN_SECRET_KEY_CHANGE_ME":
        raise HTTPException(status_code=403, detail="Invalid admin key")

    database = get_database()

    # ランダムなAPIキーを生成
    new_api_key = secrets.token_urlsafe(32)

    try:
        key_id = database.create_api_key(
            api_key=new_api_key,
            name=name,
            description=description,
            rate_limit=rate_limit
        )

        return {
            "success": True,
            "api_key": new_api_key,
            "name": name,
            "rate_limit": rate_limit,
            "message": "API Key created successfully. Please save this key securely."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ==================== アプリケーション起動 ====================

def main():
    """サーバーを起動"""
    import argparse

    parser = argparse.ArgumentParser(description='FMP Compatible API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--db-path', default='./data/fmp_data.db', help='Database file path')

    args = parser.parse_args()

    # データベースを初期化
    global db
    db = FMPDatabase(args.db_path)

    print(f"Starting FMP Compatible API Server on {args.host}:{args.port}")
    print(f"Database: {args.db_path}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")

    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == '__main__':
    main()
