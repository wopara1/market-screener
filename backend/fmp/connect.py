import pandas as pd
import numpy as np
from fastapi.encoders import jsonable_encoder
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import fmpsdk as fmp
from fastapi import HTTPException
import logging
from settings.config import settings

class FMPDataBridge:
    TIMESERIES = ['1min', '5min', '15min', '30min', '1hour', '4hour']

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("FMP_APIKEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set it in the environment variables.")

    def save_data_to_csv(self, data, symbol, period, end_date, market):
        # Create directory if it doesn't exist
        ## change to be internal 
        csv_dir = f'/Users/emmanuelwopara/Desktop/Code/Algo/Data/csv/{market}'
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        
        # Define the CSV file path
        csv_file = f"{csv_dir}/{symbol}-{period}-{end_date}.csv"
        
        # Reorder columns to make symbol the second column
        if 'symbol' in data.columns:
            cols = list(data.columns)
            cols.insert(1, cols.pop(cols.index('symbol')))
            data = data[cols]
        
        # Ensure data is in OHLC format
        ohlc_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        if all(col in data.columns for col in ohlc_columns):
            data = data[ohlc_columns]
        else:
            print("Data does not contain all required OHLC columns.")
            return
        
        # Reverse the order of the data
        data = data.iloc[::-1]
        
        # Save data to CSV
        data.to_csv(csv_file, index=False)
        print(f"Data saved to {csv_file}")
     
    def get_historical_intraday_data(self, symbol, exchange, interval, from_date, to_date):
        """Fetch intraday data (e.g., 1min, 5min, 1h) from a specific date range."""
        try:
            print(f"Fetching intraday data for {symbol} from {from_date} to {to_date} with interval '{interval}' on {exchange}")
            data = fmp.historical_chart(
                apikey=self.api_key,
                symbol=symbol,
                time_delta=interval,
                from_date=from_date,
                to_date=to_date
            )

            if not data:
                print(f"No data returned for {symbol} with interval '{interval}' on {exchange}")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            elif 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                raise KeyError("Neither 'date' nor 'timestamp' column found in the data.")

            df['symbol'] = symbol
            return df

        except Exception as e:
            print(f"Error fetching intraday data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_historical_period_data(self, symbol, exchange, interval, period_days):
        """Fetch historical data for a given period using a time interval."""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            period_days = int(period_days)
            start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
            print(f"Fetching period data for {symbol} from {start_date} to {end_date} with interval '{interval}' on {exchange}")
            
            data = fmp.historical_chart(
                apikey=self.api_key,
                symbol=symbol,
                time_delta=interval,
                from_date=start_date,
                to_date=end_date
            )

            if not data:
                print(f"No data returned for {symbol} with interval '{interval}' on {exchange}")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            elif 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                raise KeyError("Neither 'date' nor 'timestamp' column found in the data.")

            df['symbol'] = symbol
            return df

        except Exception as e:
            print(f"Error fetching period data for {symbol}: {e}")
            return pd.DataFrame()

        
    def get_quote(self, symbol):
        """
        Generic function to fetch quote data for stocks, ETFs, cryptocurrencies, and commodities.

        :param symbol: Ticker symbol
        :return: DataFrame with quote data
        """
        try:
            data = fmp.quote(apikey=self.api_key, symbol=symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return pd.DataFrame()

    # Stock Market Data
    def get_stocks_list(self):
        try:
            data = fmp.symbols_list(apikey=self.api_key)
            return pd.DataFrame([data])
        except Exception as e:
            print(f"Error fetching stocks list: {e}")
            return pd.DataFrame()
        
    def get_company_profile(self, symbol):
        try:
            data = fmp.company_profile(apikey=self.api_key, symbol=symbol)
            return pd.DataFrame([data])
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {e}")
            return pd.DataFrame()

    def get_financial_statements(self, symbol, statement_type):
        if statement_type == 'income':
            data = fmp.income_statement(apikey=self.api_key, symbol=symbol)
        elif statement_type == 'balance':
            data = fmp. balance_sheet_statement(apikey=self.api_key, symbol=symbol)
        elif statement_type == 'cashflow':
            data = fmp.cash_flow_statement(apikey=self.api_key, symbol=symbol)
        else:
            raise ValueError("Invalid statement type. Choose from 'income', 'balance', or 'cashflow'.")
        return pd.DataFrame(data)

    def get_stock_splits_dividends(self, symbol, data_type):
        if data_type == 'split':
            data = fmp.historical_stock_split(apikey=self.api_key, symbol=symbol)
        elif data_type == 'dividend':
            data = fmp.historical_stock_dividend(apikey=self.api_key, symbol=symbol)
        else:
            raise ValueError("Invalid data type. Choose from 'split' or 'dividend'.")
        return pd.DataFrame(data)
    

    # Forex Market
    def get_forex_pairs_list(self):
        try:
            data = fmp.available_forex(apikey=self.api_key)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching available forex pairs: {e}")
            return pd.DataFrame()
        
    def get_forex_list(self):
        try:
            data = fmp.forex_list(apikey=self.api_key)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching forex list: {e}")
            return pd.DataFrame()
    
    def get_forex_news(self, symbol, from_date, to_date, page, limit):
        try:
            data = fmp.forex_news(apikey=self.api_key, symbol=symbol, from_date=from_date, to_date=to_date, page=page, limit=limit)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching forex news for {symbol} from {from_date} to {to_date}: {e}")
            return pd.DataFrame()

    def get_available_crypto_pairs(self):
        data = fmp.available_cryptocurrencies(apikey=self.api_key)
        return pd.DataFrame(data)
    
    def get_cryptocurrencies_list(self):
        data = fmp.cryptocurrencies_list(apikey=self.api_key)
        return pd.DataFrame(data)
    
    def get_historical_daily_crypto_data(self, crypto_symbol):
        data = fmp.historical_price_full(apikey=self.api_key, symbol=crypto_symbol)
        return pd.DataFrame(data)

    def get_crypto_news(self, news_symbol, from_date, to_date, limit):
        data = fmp.crypto_news(apikey=self.api_key, symbol=news_symbol, from_date=from_date, to_date=to_date, limit=limit)
        return pd.DataFrame(data)
    
    def get_historical_daily_commodity_data(self, commodity_symbol):
        data = fmp.historical_price_full(apikey=self.api_key, symbol=commodity_symbol)
        return pd.DataFrame(data)
    
    def get_available_commodities_pairs(self):
        data = fmp.available_commodities(apikey=self.api_key)
        return pd.DataFrame(data)
    
    def get_commodities_list(self):
        data = fmp.commodities_list(apikey=self.api_key)
        return pd.DataFrame(data)
    

    def get_etf_list(self):
        """
        Query FMP /etf_list/ API for a list of ETFs.

        :return: DataFrame with list of ETFs
        """
        try:
            data = fmp.etf_list(apikey=self.api_key)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching ETF list: {e}")
            return pd.DataFrame()

    def get_available_etf_pairs(self):
        """
        Query FMP /available_etfs/ API for available ETF pairs.

        :return: DataFrame with available ETF pairs
        """
        try:
            data = fmp.available_etfs(apikey=self.api_key)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching available ETF pairs: {e}")
            return pd.DataFrame()

    def get_real_time_etf_data(self, etf_symbol):
        """
        Query FMP /etf_price_realtime/ API for real-time ETF price data.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with real-time ETF price data
        """
        try:
            data = fmp.etf_price_realtime(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching real-time ETF data for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_etf_info(self, etf_symbol):
        """
        Query FMP /etf_info/ API for ETF information.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with ETF information
        """
        try:
            data = fmp.etf_info(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching ETF info for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_etf_sector_weightings(self, etf_symbol):
        """
        Query FMP /etf_sector_weightings/ API for ETF sector weightings.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with ETF sector weightings
        """
        try:
            data = fmp.etf_sector_weightings(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching ETF sector weightings for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_etf_country_weightings(self, etf_symbol):
        """
        Query FMP /etf_country_weightings/ API for ETF country weightings.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with ETF country weightings
        """
        try:
            data = fmp.etf_country_weightings(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching ETF country weightings for {etf_symbol}: {e}")
            return pd.DataFrame()
        
    def get_historical_daily_eft_data(self, etf_symbol):
        """
        Query FMP /historical_price_full/ API for historical daily ETF prices.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with historical daily ETF prices
        """
        try:
            data = fmp.historical_price_full(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching historical daily ETF prices for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_etf_historical_dividends(self, etf_symbol):
        """
        Query FMP /historical_stock_dividend/ API for historical ETF dividends.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with historical ETF dividends
        """
        try:
            data = fmp.historical_stock_dividend(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching historical ETF dividends for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_etf_historical_splits(self, etf_symbol):
        """
        Query FMP /historical_stock_split/ API for historical ETF splits.

        :param etf_symbol: ETF ticker symbol
        :return: DataFrame with historical ETF splits
        """
        try:
            data = fmp.historical_stock_split(apikey=self.api_key, symbol=etf_symbol)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching historical ETF splits for {etf_symbol}: {e}")
            return pd.DataFrame()

    def get_technical_indicators(self, symbol, period=10, statistics_type="SMA", time_delta="daily"):
        """
        Query FMP /technical_indicator/ API.

        :param symbol: Company ticker
        :param period: Period for the technical indicator
        :param statistics_type: Type of technical indicator (e.g., 'SMA', 'EMA')
        :param time_delta: Time delta for the data ('daily' or intraday: '1min' - '4hour')
        :return: DataFrame with technical indicator data
        """
        try:
            data = fmp.technical_indicators(
                apikey=self.api_key,
                symbol=symbol,
                period=period,
                statistics_type=statistics_type,
                time_delta=time_delta
            )
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching technical indicators for {symbol}: {e}")
            return pd.DataFrame()

    def get_cot_list(self):
        """
        Query FMP /cot list/ API.

        :param api_key
        """
        try:
            data = fmp.commitment_of_traders_report_list(apikey=self.api_key)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching commiment of trader list: {e}")
            return pd.DataFrame()
        
    def get_cot_data(self, symbol, from_date, to_date):
        """
        Query FMP /cot data/ API.

        :param api_key
        """
        try:
            data = fmp.commitment_of_traders_report(
                apikey=self.api_key,
                symbol=symbol,
                from_date=from_date,
                to_date=to_date)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching cot data for {symbol}: {e}")
            
    def parse_date(self, date_str: str) -> datetime:
        """Parses a date string in YYYY-MM-DD format."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    def validate_timeseries(self, timeseries: str) -> str:
        """Validates the timeseries input."""
        valid_timeseries = ['1min', '5min', '15min', '30min', '1hour', '4hour']
        if timeseries not in valid_timeseries:
            raise HTTPException(status_code=400, detail=f"Invalid timeseries. Valid options: {valid_timeseries}")
        return timeseries

    def handle_fmp_error(self, error: Exception):
        """Handles exceptions from the FMP bridge and formats them for the API."""
        logging.info(f"FMP Bridge Error: {error}")
        raise HTTPException(status_code=500, detail=str(error))

    def handle_data_frame(self, data):
        """Returns a json from a dataframe"""
        if data.empty:
            raise HTTPException(status_code=404, detail="Data not found.")
        
        # Replace NaN, NaT, inf values with None
        data = data.replace([np.nan, np.inf, -np.inf], None)

        # Convert to JSON-safe structure
        json_safe = jsonable_encoder(data.to_dict(orient="records"))
        
        return json_safe

            
fmp_bridge = FMPDataBridge()