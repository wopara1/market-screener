from fastapi import APIRouter
from fastapi import BackgroundTasks
from . import initialize_tickers, fetch_cot_list
from fmp.connect import fmp_bridge
import logging

ticker_router = APIRouter()

@ticker_router.post("/update-tickers")
async def update_tickers(background_tasks: BackgroundTasks):
    background_tasks.add_task(initialize_tickers)
    return {"message": "Ticker update task triggered."}

@ticker_router.post("/update-cot")
async def update_cot(background_tasks: BackgroundTasks):
    background_tasks.add_task(fetch_cot_list)
    return {"message": "COT list update task triggered."}


# route is really expensive due to amount of data
@ticker_router.get("/stocks-list")
def get_stocks_list():
    """Fetches the list of available stocks."""
    try:
        data = fmp_bridge.get_stocks_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
       fmp_bridge. handle_fmp_error(e)

@ticker_router.get("/forex-list")
def get_forex_list():
    """Fetches the list of available forex."""
    try:
        data = fmp_bridge.get_forex_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
        fmp_bridge.handle_fmp_error(e)

# route is really expensive due to amount of data
@ticker_router.get("/cryptocurrencies-list")
def get_cryptocurrencies_list():
    """Fetches the list of available cryptocurrencies."""
    try:
        data = fmp_bridge.get_cryptocurrencies_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
        fmp_bridge.handle_fmp_error(e)

@ticker_router.get("/commodities-list")
def get_commodities_list():
    """Fetches the list of available commodities."""
    try:
        data = fmp_bridge.get_commodities_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
        fmp_bridge.handle_fmp_error(e)

@ticker_router.get("/etf-list")
def get_etf_list():
    """Fetches the list of available ETFs."""
    try:
        data = fmp_bridge.get_etf_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
        fmp_bridge.handle_fmp_error(e)
        
@ticker_router.get("/cot-list")
def get_cot_list():
    """Fetches the list of COT reports."""
    try:
        data = fmp_bridge.get_cot_list()
        return fmp_bridge.handle_data_frame(data)
    except Exception as e:
        fmp_bridge.handle_fmp_error(e)