import asyncio
import logging
import pandas as pd
from fmp.connect import fmp_bridge

# Dynamically size semaphore to no more than symbol‐count
def make_semaphore(symbols, max_size=4):
    size = min(len(symbols), max_size)
    return asyncio.Semaphore(size)

logger = logging.getLogger(__name__)

def classify_score(score):
    score_mapping = {
        3: 'Strong Buy',  2: 'Buy',  1: 'Weak Buy',
        0: 'Neutral', -1: 'Weak Sell', -2: 'Sell', -3: 'Strong Sell'
    }
    return score_mapping.get(score, 'Strong Sell')

async def fetch_indicator_data(symbol, period, time_series, indicator_type):
    """
    Fetch indicator data via asyncio.to_thread.
    """
    try:
        df = await asyncio.to_thread(
            fmp_bridge.get_technical_indicators,
            symbol, period, indicator_type, time_series
        )
        return pd.DataFrame(df)
    except Exception as e:
        logger.error(f"[Error] {symbol} - {indicator_type}: {e}")
        return pd.DataFrame()

async def fetch_indicators(symbol, period, time_series, semaphore):
    """
    Fetch RSI, ADX, Williams %R concurrently under one semaphore.
    """
    async with semaphore:
        # fire all three fetches at once :contentReference[oaicite:6]{index=6}
        rsi_df, adx_df, willr_df = await asyncio.gather(
            fetch_indicator_data(symbol, period, time_series, 'rsi'),
            fetch_indicator_data(symbol, period, time_series, 'adx'),
            fetch_indicator_data(symbol, period, time_series, 'williams'),
        )

        # fast scalar extraction :contentReference[oaicite:7]{index=7}
        rsi_val  = rsi_df['rsi'].iat[-1]     if not rsi_df.empty else None
        adx_val  = adx_df['adx'].iat[-1]     if not adx_df.empty else None
        willr_val= willr_df['williams'].iat[-1] if not willr_df.empty else None

        rsi_score   = 1 if rsi_val  is not None and rsi_val  < 30 else (-1 if rsi_val  is not None and rsi_val  > 70 else 0)
        adx_score   = 1 if adx_val  is not None and adx_val  >= 25 else (-1 if adx_val  is not None and adx_val  < 20 else 0)
        willr_score= 1 if willr_val is not None and willr_val < -80 else (-1 if willr_val is not None and willr_val > -20 else 0)

        total_score = rsi_score + adx_score + willr_score
        return symbol, {
            "score": total_score,
            "rating": classify_score(total_score)
        }

async def tickers_indicator_rating(symbols, period, time_series):
    """
    Calculate ratings for symbols, using optimized fetch.
    """
    semaphore = make_semaphore(symbols, max_size=10)
    tasks = [
        fetch_indicators(sym, period, time_series, semaphore)
        for sym in symbols
    ]
    results = await asyncio.gather(*tasks)  # overall concurrency control
    return dict(results)
