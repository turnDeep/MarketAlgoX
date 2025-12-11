"""
スクリーナー名称定義

日本語名と英語名のマッピングを提供
"""

# スクリーナー名称マッピング
SCREENER_NAMES = {
    "短期中期長期の最強銘柄": "Momentum 97",
    "爆発的EPS成長銘柄": "Explosive Estimated EPS Growth Stocks",
    "出来高急増上昇銘柄": "Up on Volume List",
    "相対強度トップ2%銘柄": "Top 2% RS Rating List",
    "急騰直後銘柄": "4% Bullish Yesterday",
    "健全チャート銘柄": "Healthy Chart Watch List"
}

# 英語名から日本語名への逆引き
SCREENER_NAMES_EN_TO_JA = {v: k for k, v in SCREENER_NAMES.items()}

# スクリーナー説明
SCREENER_DESCRIPTIONS = {
    "短期中期長期の最強銘柄": "短期・中期・長期すべてでトップパフォーマンスの銘柄を抽出",
    "爆発的EPS成長銘柄": "爆発的なEPS成長を示す強気銘柄を抽出",
    "出来高急増上昇銘柄": "出来高を伴って上昇している銘柄を抽出",
    "相対強度トップ2%銘柄": "相対的強さが極めて高い銘柄を抽出",
    "急騰直後銘柄": "前日に強い上昇を見せた銘柄を抽出",
    "健全チャート銘柄": "健全なチャートパターンを持つ銘柄を抽出"
}

# スクリーナー条件
SCREENER_CRITERIA = {
    "短期中期長期の最強銘柄": {
        "1M Rank (Pct)": "≥ 97%",
        "3M Rank (Pct)": "≥ 97%",
        "6M Rank (Pct)": "≥ 97%"
    },
    "爆発的EPS成長銘柄": {
        "RS Rating": "≥ 80",
        "RS STS%": "≥ 80",
        "EPS Growth Last Qtr": "≥ 100%",
        "50-Day Avg Vol": "≥ 100K",
        "Price vs 50-Day": "≥ 0.0%"
    },
    "出来高急増上昇銘柄": {
        "Price % Chg": "≥ 0.00%",
        "Vol% Chg vs 50-Day": "≥ 20%",
        "Current Price": "≥ $10",
        "50-Day Avg Vol": "≥ 100K",
        "Market Cap": "≥ $250M",
        "RS Rating": "≥ 80",
        "RS STS%": "≥ 80",
        "EPS % Chg Last Qtr": "≥ 20%",
        "A/D Rating": "ABC"
    },
    "相対強度トップ2%銘柄": {
        "RS Rating": "≥ 98",
        "RS STS%": "≥ 80",
        "Moving Averages": "10Day > 21Day > 50Day",
        "50-Day Avg Vol": "≥ 100K",
        "Volume": "≥ 100K",
        "Sector": "NOT medical/healthcare"
    },
    "急騰直後銘柄": {
        "Price": "≥ $1",
        "Change": "> 4%",
        "Market cap": "> $250M",
        "Volume": "> 100K",
        "Rel Volume": "> 1",
        "Change from Open": "> 0%",
        "Avg Volume 90D": "> 100K",
        "RS STS%": "≥ 80"
    },
    "健全チャート銘柄": {
        "Short-term MA": "10Day > 21Day > 50Day",
        "Long-term MA": "50Day > 150Day > 200Day",
        "RS Line": "New High",
        "RS Rating": "≥ 90",
        "A/D Rating": "AB",
        "Comp Rating": "≥ 80",
        "50-Day Avg Vol": "≥ 100K"
    }
}


def get_japanese_name(english_name: str) -> str:
    """英語名から日本語名を取得"""
    return SCREENER_NAMES_EN_TO_JA.get(english_name, english_name)


def get_english_name(japanese_name: str) -> str:
    """日本語名から英語名を取得"""
    return SCREENER_NAMES.get(japanese_name, japanese_name)


def get_screener_info(japanese_name: str) -> dict:
    """スクリーナー情報を取得"""
    return {
        "name": japanese_name,
        "english_name": get_english_name(japanese_name),
        "description": SCREENER_DESCRIPTIONS.get(japanese_name, ""),
        "criteria": SCREENER_CRITERIA.get(japanese_name, {})
    }
