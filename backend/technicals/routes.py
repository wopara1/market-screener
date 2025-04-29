from fastapi import APIRouter, Query
from fmp.connect import fmp_bridge
from .ratings import tickers_indicator_rating
from fastapi import BackgroundTasks

technicals_router = APIRouter()

@technicals_router.post("/get_commodities_technical_rates")
async def get_commodities_technical_rates(
    background_tasks: BackgroundTasks,
    RSI_PERIOD: int = Query(14, description="Relative Strength Index period"),
    TIMESERIES: str = Query('daily', description="Time series interval")
):
    data = fmp_bridge.get_commodities_list()
    commodities_list = fmp_bridge.handle_data_frame(data)

    symbols = [item['symbol'] for item in commodities_list]

    # Immediately calculate and return the results
    commodities_ratings = await tickers_indicator_rating(symbols, RSI_PERIOD, TIMESERIES)

    return commodities_ratings

@technicals_router.post("/get_forex_technical_rates")
async def get_forex_technical_rates(
    background_tasks: BackgroundTasks,
    RSI_PERIOD: int = Query(14, description="Relative Strength Index period"),
    TIMESERIES: str = Query('daily', description="Time series interval")
):
    data = fmp_bridge.get_forex_list()
    forex_list = fmp_bridge.handle_data_frame(data)

    symbols = [item['symbol'] for item in forex_list]

    # Immediately calculate and return the results
    forex_ratings = await tickers_indicator_rating(symbols, RSI_PERIOD, TIMESERIES)

    return forex_ratings