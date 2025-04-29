# market-screener
This is a financial market screener to view asset performance and overview 

## Back-End setup:

cd backend 

pip3 install -r requirements.txt

BEFORE RUNNING
please ensure that you have a .env file with all settings.config vars

**python main.py**

here is a test route for main app:
http://127.0.0.1:8000

NOTE the back end will init azure blob storafe files for tickers

here is a route to list fo all forex pairs:
http://127.0.0.1:8000/tickers/commodities-list

example list data:
{
    "symbol": "DCUSD",
    "name": "Class III Milk Futures",
    "price": 18.28,
    "changesPercentage": 3.45218,
    "change": 0.61,
    "dayLow": 17.68,
    "dayHigh": 18.29,
    "yearHigh": 23.36,
    "yearLow": 15.52,
    "marketCap": null,
    "priceAvg50": 18.4798,
    "priceAvg200": 20.1723,
    "exchange": "COMMODITY",
    "volume": 5,
    "avgVolume": 125.0,
    "open": 18.29,
    "previousClose": 17.67,
    "eps": null,
    "pe": null,
    "earningsAnnouncement": null,
    "sharesOutstanding": null,
    "timestamp": 1745898350
},

/get_commodities_technical_rates

example list data:
"DCUSD": {
        "rsi": 1,
        "adx": 1,
        "willr": 1,
        "score": 3,
        "rating": "Strong Buy"
    },
