# market-screener
This is a financial market screener to view asset performance and overview 

## Back-end setup:

cd backend 

pip3 install -r requirements.txt

BEFORE RUNNING
please ensure that you have a .env file with all settings.config vars


**python main.py**

here is a test route for main app:
http://127.0.0.1:8000

NOTE the back end will init azure blob storafe files for tickers

here is a route to list fo all forex pairs:
http://127.0.0.1:8000/tickers/forex-list

example list data:
{
    "symbol": "AEDAUD",
    "name": "AED/AUD",
    "price": 0.42361,
    "changesPercentage": -0.35704,
    "change": -0.00151788,
    "dayLow": 0.42291,
    "dayHigh": 0.42447,
    "yearHigh": 0.45712,
    "yearLow": 0.39248,
    "marketCap": null,
    "priceAvg50": 0.43288,
    "priceAvg200": 0.42117,
    "exchange": "FOREX",
    "volume": 0.0,
    "avgVolume": 32.73684,
    "open": 0.42293,
    "previousClose": 0.42513,
    "eps": null,
    "pe": null,
    "earningsAnnouncement": null,
    "sharesOutstanding": null,
    "timestamp": 1745883360
},
