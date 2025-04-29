import os
import time
import pandas as pd
from fmp.connect import fmp_bridge
from blob.blobManager import blob_manager
from tempfile import NamedTemporaryFile
import logging

fmp_data = fmp_bridge
UPDATE_THRESHOLD = 86400  # 1 day
exchanges = ['forex', 'commodities', 'crypto', 'stocks']

container_name = "tickers"

def get_name_for_ticker(ticker):
    return ticker

def transform_tickers(ticker_list):
    return [{"symbol": ticker, "name": get_name_for_ticker(ticker)} for ticker in ticker_list]

def flatten_ticker_dataframe(df):
    tickers = []
    row = df.iloc[0]
    for cell in row:
        if isinstance(cell, dict):
            tickers.append({
                "symbol": cell.get("symbol", ""),
                "name": cell.get("name", "")
            })
        else:
            tickers.append({
                "symbol": cell,
                "name": get_name_for_ticker(cell)
            })
    return tickers

def ticker_inquiry(exchange):
    if exchange == 'forex':
        return fmp_data.get_forex_list()
    elif exchange == 'commodities':
        return fmp_data.get_commodities_list()
    elif exchange == 'crypto':
        return fmp_data.get_cryptocurrencies_list()
    elif exchange == 'stocks':
        return fmp_data.get_stocks_list()
    return []

def is_blob_updated(blob_name):
    try:
        blob_client = blob_manager.get_blob_client(container_name, blob_name)
        properties = blob_client.get_blob_properties()
        last_modified = properties.last_modified.timestamp()
        return (time.time() - last_modified) < UPDATE_THRESHOLD
    except Exception as e:
        logging.info(f"Blob '{blob_name}' not found or error retrieving properties: {e}")
        return False

def save_ticker_list(blob_name, ticker_list):
    csv_content = "Index,Symbol,Name\n" + "\n".join(
        f"{index},{ticker['symbol']},{ticker['name']}" for index, ticker in enumerate(ticker_list)
    )

    # Write to temp file
    with NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Now upload using file path
    blob_manager.upload_to_blob_storage(temp_file_path, blob_name, container=container_name)

    logging.info(f"Ticker list saved to blob '{blob_name}'.")


async def initialize_tickers():
    for exchange in exchanges:
        blob_name = f"{exchange}/{exchange}_tickers.csv"

        if is_blob_updated(blob_name):
            logging.info(f"{blob_name} is up-to-date.")
        else:
            logging.info(f"{blob_name} is outdated or missing. Fetching new data...")
            
            with NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_path = tmp_file.name
                
            if blob_manager.download_from_blob_storage(blob_name, tmp_path, container_name):
                logging.info(f"Used blob file for {exchange} instead of re-fetching.")
                continue

            logging.info(f"Blob download failed. Fetching new ticker list from API...")
            ticker_list = ticker_inquiry(exchange)

            if isinstance(ticker_list, list) and ticker_list and isinstance(ticker_list[0], pd.DataFrame):
                ticker_list = ticker_list[0]
            if isinstance(ticker_list, pd.DataFrame):
                if ticker_list.empty:
                    ticker_list = []
                elif ticker_list.shape[0] == 1:
                    ticker_list = flatten_ticker_dataframe(ticker_list)
                elif 'symbol' in ticker_list.columns and 'name' in ticker_list.columns:
                    ticker_list = ticker_list.to_dict(orient="records")
                else:
                    ticker_list = transform_tickers(ticker_list.iloc[:, 0].tolist())
            elif isinstance(ticker_list, list) and ticker_list and isinstance(ticker_list[0], str):
                ticker_list = transform_tickers(ticker_list)
            elif ticker_list and isinstance(ticker_list[0], list):
                ticker_list = ticker_list[0]

            save_ticker_list(blob_name, ticker_list)
            os.remove(tmp_path)
            logging.info(f"Ticker list for {exchange} saved to blob storage.")

async def fetch_cot_list():
    blob_name = "cot/cot_tickers.csv"

    if is_blob_updated(blob_name):
        logging.info(f"{blob_name} is up-to-date.")
        return
    
    with NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        tmp_path = tmp_file.name
    
    if blob_manager.download_from_blob_storage(blob_name, tmp_path, container_name):
        logging.info(f"Used blob file for COT instead of re-fetching.")
        return
    
    logging.info(f"Blob download failed. Fetching new COT ticker list from API...")
    data = fmp_data.get_cot_list()

    if data is None:
        logging.info("No data retrieved from FMP.")
        return

    if isinstance(data, list) and data and isinstance(data[0], pd.DataFrame):
        data = data[0]

    if isinstance(data, pd.DataFrame):
        if data.empty:
            data = []
        elif data.shape[0] == 1:
            data = flatten_ticker_dataframe(data)
        elif 'trading_symbol' in data.columns and 'short_name' in data.columns:
            data = data.rename(columns={'trading_symbol': 'symbol', 'short_name': 'name'})
            data = data.to_dict(orient="records")
        elif 'symbol' in data.columns and 'name' in data.columns:
            data = data.to_dict(orient="records")
        else:
            data = transform_tickers(data.iloc[:, 0].tolist())
    elif isinstance(data, list) and data and isinstance(data[0], str):
        data = transform_tickers(data)
    elif data and isinstance(data[0], list):
        data = data[0]

    save_ticker_list(blob_name, data)
    os.remove(tmp_path)
    logging.info(f"Ticker list for COT saved to blob storage.")