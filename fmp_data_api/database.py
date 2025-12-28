"""
FMP Data API - Database Module
全米国株のデータを保存するデータベースモジュール
"""

import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


class FMPDatabase:
    """FMPデータを保存するデータベースクラス"""

    def __init__(self, db_path: str = './data/fmp_data.db'):
        """
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """データベース接続を取得"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_database(self):
        """データベースの初期化"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. 銘柄リストテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_list (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                exchange TEXT,
                exchangeShortName TEXT,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 企業プロファイルテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_profile (
                symbol TEXT PRIMARY KEY,
                companyName TEXT,
                currency TEXT,
                cik TEXT,
                isin TEXT,
                cusip TEXT,
                exchange TEXT,
                exchangeShortName TEXT,
                industry TEXT,
                sector TEXT,
                country TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip TEXT,
                website TEXT,
                phone TEXT,
                description TEXT,
                ceo TEXT,
                fullTimeEmployees INTEGER,
                image TEXT,
                ipoDate TEXT,
                defaultImage INTEGER,
                isEtf INTEGER,
                isActivelyTrading INTEGER,
                isFund INTEGER,
                isAdr INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 3. 株価データテーブル（日次）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adjClose REAL,
                volume INTEGER,
                unadjustedVolume INTEGER,
                change REAL,
                changePercent REAL,
                vwap REAL,
                label TEXT,
                changeOverTime REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 4. リアルタイム株価テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_quotes (
                symbol TEXT PRIMARY KEY,
                price REAL,
                changesPercentage REAL,
                change REAL,
                dayLow REAL,
                dayHigh REAL,
                yearHigh REAL,
                yearLow REAL,
                marketCap INTEGER,
                priceAvg50 REAL,
                priceAvg200 REAL,
                volume INTEGER,
                avgVolume INTEGER,
                exchange TEXT,
                open REAL,
                previousClose REAL,
                eps REAL,
                pe REAL,
                earningsAnnouncement TEXT,
                sharesOutstanding INTEGER,
                timestamp INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 5. 損益計算書テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                period TEXT,
                reportedCurrency TEXT,
                cik TEXT,
                fillingDate TEXT,
                acceptedDate TEXT,
                calendarYear TEXT,
                revenue REAL,
                costOfRevenue REAL,
                grossProfit REAL,
                grossProfitRatio REAL,
                researchAndDevelopmentExpenses REAL,
                generalAndAdministrativeExpenses REAL,
                sellingAndMarketingExpenses REAL,
                sellingGeneralAndAdministrativeExpenses REAL,
                otherExpenses REAL,
                operatingExpenses REAL,
                costAndExpenses REAL,
                interestIncome REAL,
                interestExpense REAL,
                depreciationAndAmortization REAL,
                ebitda REAL,
                ebitdaratio REAL,
                operatingIncome REAL,
                operatingIncomeRatio REAL,
                totalOtherIncomeExpensesNet REAL,
                incomeBeforeTax REAL,
                incomeBeforeTaxRatio REAL,
                incomeTaxExpense REAL,
                netIncome REAL,
                netIncomeRatio REAL,
                eps REAL,
                epsdiluted REAL,
                weightedAverageShsOut REAL,
                weightedAverageShsOutDil REAL,
                link TEXT,
                finalLink TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, period),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 6. 貸借対照表テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                period TEXT,
                reportedCurrency TEXT,
                cik TEXT,
                fillingDate TEXT,
                acceptedDate TEXT,
                calendarYear TEXT,
                cashAndCashEquivalents REAL,
                shortTermInvestments REAL,
                cashAndShortTermInvestments REAL,
                netReceivables REAL,
                inventory REAL,
                otherCurrentAssets REAL,
                totalCurrentAssets REAL,
                propertyPlantEquipmentNet REAL,
                goodwill REAL,
                intangibleAssets REAL,
                goodwillAndIntangibleAssets REAL,
                longTermInvestments REAL,
                taxAssets REAL,
                otherNonCurrentAssets REAL,
                totalNonCurrentAssets REAL,
                otherAssets REAL,
                totalAssets REAL,
                accountPayables REAL,
                shortTermDebt REAL,
                taxPayables REAL,
                deferredRevenue REAL,
                otherCurrentLiabilities REAL,
                totalCurrentLiabilities REAL,
                longTermDebt REAL,
                deferredRevenueNonCurrent REAL,
                deferredTaxLiabilitiesNonCurrent REAL,
                otherNonCurrentLiabilities REAL,
                totalNonCurrentLiabilities REAL,
                otherLiabilities REAL,
                capitalLeaseObligations REAL,
                totalLiabilities REAL,
                preferredStock REAL,
                commonStock REAL,
                retainedEarnings REAL,
                accumulatedOtherComprehensiveIncomeLoss REAL,
                othertotalStockholdersEquity REAL,
                totalStockholdersEquity REAL,
                totalEquity REAL,
                totalLiabilitiesAndStockholdersEquity REAL,
                minorityInterest REAL,
                totalLiabilitiesAndTotalEquity REAL,
                totalInvestments REAL,
                totalDebt REAL,
                netDebt REAL,
                link TEXT,
                finalLink TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, period),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 7. キャッシュフロー計算書テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_flow_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                period TEXT,
                reportedCurrency TEXT,
                cik TEXT,
                fillingDate TEXT,
                acceptedDate TEXT,
                calendarYear TEXT,
                netIncome REAL,
                depreciationAndAmortization REAL,
                deferredIncomeTax REAL,
                stockBasedCompensation REAL,
                changeInWorkingCapital REAL,
                accountsReceivables REAL,
                inventory REAL,
                accountsPayables REAL,
                otherWorkingCapital REAL,
                otherNonCashItems REAL,
                netCashProvidedByOperatingActivities REAL,
                investmentsInPropertyPlantAndEquipment REAL,
                acquisitionsNet REAL,
                purchasesOfInvestments REAL,
                salesMaturitiesOfInvestments REAL,
                otherInvestingActivites REAL,
                netCashUsedForInvestingActivites REAL,
                debtRepayment REAL,
                commonStockIssued REAL,
                commonStockRepurchased REAL,
                dividendsPaid REAL,
                otherFinancingActivites REAL,
                netCashUsedProvidedByFinancingActivities REAL,
                effectOfForexChangesOnCash REAL,
                netChangeInCash REAL,
                cashAtEndOfPeriod REAL,
                cashAtBeginningOfPeriod REAL,
                operatingCashFlow REAL,
                capitalExpenditure REAL,
                freeCashFlow REAL,
                link TEXT,
                finalLink TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, period),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 8. 財務比率テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_ratios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                period TEXT,
                currentRatio REAL,
                quickRatio REAL,
                cashRatio REAL,
                daysOfSalesOutstanding REAL,
                daysOfInventoryOutstanding REAL,
                operatingCycle REAL,
                daysOfPayablesOutstanding REAL,
                cashConversionCycle REAL,
                grossProfitMargin REAL,
                operatingProfitMargin REAL,
                pretaxProfitMargin REAL,
                netProfitMargin REAL,
                effectiveTaxRate REAL,
                returnOnAssets REAL,
                returnOnEquity REAL,
                returnOnCapitalEmployed REAL,
                netIncomePerEBT REAL,
                ebtPerEbit REAL,
                ebitPerRevenue REAL,
                debtRatio REAL,
                debtEquityRatio REAL,
                longTermDebtToCapitalization REAL,
                totalDebtToCapitalization REAL,
                interestCoverage REAL,
                cashFlowToDebtRatio REAL,
                companyEquityMultiplier REAL,
                receivablesTurnover REAL,
                payablesTurnover REAL,
                inventoryTurnover REAL,
                fixedAssetTurnover REAL,
                assetTurnover REAL,
                operatingCashFlowPerShare REAL,
                freeCashFlowPerShare REAL,
                cashPerShare REAL,
                payoutRatio REAL,
                operatingCashFlowSalesRatio REAL,
                freeCashFlowOperatingCashFlowRatio REAL,
                cashFlowCoverageRatios REAL,
                shortTermCoverageRatios REAL,
                capitalExpenditureCoverageRatio REAL,
                dividendPaidAndCapexCoverageRatio REAL,
                dividendPayoutRatio REAL,
                priceBookValueRatio REAL,
                priceToBookRatio REAL,
                priceToSalesRatio REAL,
                priceEarningsRatio REAL,
                priceToFreeCashFlowsRatio REAL,
                priceToOperatingCashFlowsRatio REAL,
                priceCashFlowRatio REAL,
                priceEarningsToGrowthRatio REAL,
                priceSalesRatio REAL,
                dividendYield REAL,
                enterpriseValueMultiple REAL,
                priceFairValue REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, period),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 9. 主要指標テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                period TEXT,
                revenuePerShare REAL,
                netIncomePerShare REAL,
                operatingCashFlowPerShare REAL,
                freeCashFlowPerShare REAL,
                cashPerShare REAL,
                bookValuePerShare REAL,
                tangibleBookValuePerShare REAL,
                shareholdersEquityPerShare REAL,
                interestDebtPerShare REAL,
                marketCap REAL,
                enterpriseValue REAL,
                peRatio REAL,
                priceToSalesRatio REAL,
                pocfratio REAL,
                pfcfRatio REAL,
                pbRatio REAL,
                ptbRatio REAL,
                evToSales REAL,
                enterpriseValueOverEBITDA REAL,
                evToOperatingCashFlow REAL,
                evToFreeCashFlow REAL,
                earningsYield REAL,
                freeCashFlowYield REAL,
                debtToEquity REAL,
                debtToAssets REAL,
                netDebtToEBITDA REAL,
                currentRatio REAL,
                interestCoverage REAL,
                incomeQuality REAL,
                dividendYield REAL,
                payoutRatio REAL,
                salesGeneralAndAdministrativeToRevenue REAL,
                researchAndDdevelopementToRevenue REAL,
                intangiblesToTotalAssets REAL,
                capexToOperatingCashFlow REAL,
                capexToRevenue REAL,
                capexToDepreciation REAL,
                stockBasedCompensationToRevenue REAL,
                grahamNumber REAL,
                roic REAL,
                returnOnTangibleAssets REAL,
                grahamNetNet REAL,
                workingCapital REAL,
                tangibleAssetValue REAL,
                netCurrentAssetValue REAL,
                investedCapital REAL,
                averageReceivables REAL,
                averagePayables REAL,
                averageInventory REAL,
                daysSalesOutstanding REAL,
                daysPayablesOutstanding REAL,
                daysOfInventoryOnHand REAL,
                receivablesTurnover REAL,
                payablesTurnover REAL,
                inventoryTurnover REAL,
                roe REAL,
                capexPerShare REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, period),
                FOREIGN KEY (symbol) REFERENCES stock_list(symbol)
            )
        ''')

        # 10. API認証テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                rate_limit INTEGER DEFAULT 300,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')

        # 11. APIリクエストログテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id INTEGER,
                endpoint TEXT,
                params TEXT,
                response_code INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
            )
        ''')

        # インデックスの作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol_date ON daily_prices(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_income_statements_symbol_date ON income_statements(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_balance_sheets_symbol_date ON balance_sheets(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cash_flow_statements_symbol_date ON cash_flow_statements(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_financial_ratios_symbol_date ON financial_ratios(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key_metrics_symbol_date ON key_metrics(symbol, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_request_logs_api_key_id ON api_request_logs(api_key_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_request_logs_timestamp ON api_request_logs(timestamp)')

        conn.commit()
        print("Database initialized successfully")

    # ==================== INSERT/UPDATE メソッド ====================

    def upsert_stock(self, stock_data: Dict[str, Any]):
        """銘柄情報を挿入または更新"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO stock_list
            (symbol, name, exchange, exchangeShortName, type, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            stock_data.get('symbol'),
            stock_data.get('name'),
            stock_data.get('exchange'),
            stock_data.get('exchangeShortName'),
            stock_data.get('type')
        ))
        conn.commit()

    def upsert_company_profile(self, profile_data: Dict[str, Any]):
        """企業プロファイルを挿入または更新"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO company_profile
            (symbol, companyName, currency, cik, isin, cusip, exchange, exchangeShortName,
             industry, sector, country, address, city, state, zip, website, phone,
             description, ceo, fullTimeEmployees, image, ipoDate, defaultImage,
             isEtf, isActivelyTrading, isFund, isAdr, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            profile_data.get('symbol'),
            profile_data.get('companyName'),
            profile_data.get('currency'),
            profile_data.get('cik'),
            profile_data.get('isin'),
            profile_data.get('cusip'),
            profile_data.get('exchange'),
            profile_data.get('exchangeShortName'),
            profile_data.get('industry'),
            profile_data.get('sector'),
            profile_data.get('country'),
            profile_data.get('address'),
            profile_data.get('city'),
            profile_data.get('state'),
            profile_data.get('zip'),
            profile_data.get('website'),
            profile_data.get('phone'),
            profile_data.get('description'),
            profile_data.get('ceo'),
            profile_data.get('fullTimeEmployees'),
            profile_data.get('image'),
            profile_data.get('ipoDate'),
            profile_data.get('defaultImage'),
            profile_data.get('isEtf'),
            profile_data.get('isActivelyTrading'),
            profile_data.get('isFund'),
            profile_data.get('isAdr')
        ))
        conn.commit()

    def insert_daily_price(self, price_data: Dict[str, Any]):
        """日次株価データを挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_prices
                (symbol, date, open, high, low, close, adjClose, volume, unadjustedVolume,
                 change, changePercent, vwap, label, changeOverTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                price_data.get('symbol'),
                price_data.get('date'),
                price_data.get('open'),
                price_data.get('high'),
                price_data.get('low'),
                price_data.get('close'),
                price_data.get('adjClose'),
                price_data.get('volume'),
                price_data.get('unadjustedVolume'),
                price_data.get('change'),
                price_data.get('changePercent'),
                price_data.get('vwap'),
                price_data.get('label'),
                price_data.get('changeOverTime')
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already exists

    def upsert_realtime_quote(self, quote_data: Dict[str, Any]):
        """リアルタイム株価を挿入または更新"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO realtime_quotes
            (symbol, price, changesPercentage, change, dayLow, dayHigh, yearHigh, yearLow,
             marketCap, priceAvg50, priceAvg200, volume, avgVolume, exchange, open,
             previousClose, eps, pe, earningsAnnouncement, sharesOutstanding, timestamp, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            quote_data.get('symbol'),
            quote_data.get('price'),
            quote_data.get('changesPercentage'),
            quote_data.get('change'),
            quote_data.get('dayLow'),
            quote_data.get('dayHigh'),
            quote_data.get('yearHigh'),
            quote_data.get('yearLow'),
            quote_data.get('marketCap'),
            quote_data.get('priceAvg50'),
            quote_data.get('priceAvg200'),
            quote_data.get('volume'),
            quote_data.get('avgVolume'),
            quote_data.get('exchange'),
            quote_data.get('open'),
            quote_data.get('previousClose'),
            quote_data.get('eps'),
            quote_data.get('pe'),
            quote_data.get('earningsAnnouncement'),
            quote_data.get('sharesOutstanding'),
            quote_data.get('timestamp')
        ))
        conn.commit()

    def insert_income_statement(self, income_data: Dict[str, Any]):
        """損益計算書データを挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO income_statements
                (symbol, date, period, reportedCurrency, cik, fillingDate, acceptedDate, calendarYear,
                 revenue, costOfRevenue, grossProfit, grossProfitRatio, researchAndDevelopmentExpenses,
                 generalAndAdministrativeExpenses, sellingAndMarketingExpenses, sellingGeneralAndAdministrativeExpenses,
                 otherExpenses, operatingExpenses, costAndExpenses, interestIncome, interestExpense,
                 depreciationAndAmortization, ebitda, ebitdaratio, operatingIncome, operatingIncomeRatio,
                 totalOtherIncomeExpensesNet, incomeBeforeTax, incomeBeforeTaxRatio, incomeTaxExpense,
                 netIncome, netIncomeRatio, eps, epsdiluted, weightedAverageShsOut, weightedAverageShsOutDil,
                 link, finalLink)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                income_data.get('symbol'),
                income_data.get('date'),
                income_data.get('period'),
                income_data.get('reportedCurrency'),
                income_data.get('cik'),
                income_data.get('fillingDate'),
                income_data.get('acceptedDate'),
                income_data.get('calendarYear'),
                income_data.get('revenue'),
                income_data.get('costOfRevenue'),
                income_data.get('grossProfit'),
                income_data.get('grossProfitRatio'),
                income_data.get('researchAndDevelopmentExpenses'),
                income_data.get('generalAndAdministrativeExpenses'),
                income_data.get('sellingAndMarketingExpenses'),
                income_data.get('sellingGeneralAndAdministrativeExpenses'),
                income_data.get('otherExpenses'),
                income_data.get('operatingExpenses'),
                income_data.get('costAndExpenses'),
                income_data.get('interestIncome'),
                income_data.get('interestExpense'),
                income_data.get('depreciationAndAmortization'),
                income_data.get('ebitda'),
                income_data.get('ebitdaratio'),
                income_data.get('operatingIncome'),
                income_data.get('operatingIncomeRatio'),
                income_data.get('totalOtherIncomeExpensesNet'),
                income_data.get('incomeBeforeTax'),
                income_data.get('incomeBeforeTaxRatio'),
                income_data.get('incomeTaxExpense'),
                income_data.get('netIncome'),
                income_data.get('netIncomeRatio'),
                income_data.get('eps'),
                income_data.get('epsdiluted'),
                income_data.get('weightedAverageShsOut'),
                income_data.get('weightedAverageShsOutDil'),
                income_data.get('link'),
                income_data.get('finalLink')
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

    # ==================== QUERY メソッド ====================

    def get_all_symbols(self) -> List[str]:
        """全銘柄のシンボルを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT symbol FROM stock_list ORDER BY symbol')
        return [row[0] for row in cursor.fetchall()]

    def get_stock_list(self, exchange: Optional[str] = None) -> List[Dict]:
        """銘柄リストを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if exchange:
            cursor.execute('SELECT * FROM stock_list WHERE exchangeShortName = ? ORDER BY symbol', (exchange,))
        else:
            cursor.execute('SELECT * FROM stock_list ORDER BY symbol')

        return [dict(row) for row in cursor.fetchall()]

    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """企業プロファイルを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM company_profile WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_daily_prices(self, symbol: str, from_date: Optional[str] = None,
                        to_date: Optional[str] = None) -> List[Dict]:
        """日次株価データを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM daily_prices WHERE symbol = ?'
        params = [symbol]

        if from_date:
            query += ' AND date >= ?'
            params.append(from_date)

        if to_date:
            query += ' AND date <= ?'
            params.append(to_date)

        query += ' ORDER BY date DESC'

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_realtime_quote(self, symbol: str) -> Optional[Dict]:
        """リアルタイム株価を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM realtime_quotes WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_income_statements(self, symbol: str, period: str = 'quarter',
                            limit: int = 8) -> List[Dict]:
        """損益計算書を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM income_statements
            WHERE symbol = ? AND period = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (symbol, period, limit))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== API KEY 管理 ====================

    def create_api_key(self, api_key: str, name: str, description: str = None,
                      rate_limit: int = 300, expires_at: str = None) -> int:
        """新しいAPIキーを作成"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_keys (api_key, name, description, rate_limit, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (api_key, name, description, rate_limit, expires_at))
        conn.commit()

        return cursor.lastrowid

    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """APIキーを検証"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM api_keys
            WHERE api_key = ? AND is_active = 1
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (api_key,))

        row = cursor.fetchone()

        if row:
            # 最終使用日時を更新
            cursor.execute('''
                UPDATE api_keys
                SET last_used_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row['id'],))
            conn.commit()

            return dict(row)

        return None

    def log_api_request(self, api_key_id: int, endpoint: str, params: Dict, response_code: int):
        """APIリクエストをログに記録"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_request_logs (api_key_id, endpoint, params, response_code)
            VALUES (?, ?, ?, ?)
        ''', (api_key_id, endpoint, json.dumps(params), response_code))
        conn.commit()

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()
            self.conn = None
