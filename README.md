# market-screener
This is a financial market screener to view asset performance and overview 

## back-end setup:

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


Websocket functionality:
connection string:
ws://127.0.0.1:8000/ws

message format:
{"event":"subscribe",
"payload":{"exchange":"crypto","filters":{"ticker":["BTCUSD"]}}}

current supported events
subscribe, update_subscription, unsubscribe

current supported exchanges:
forex, crypto, company(stocks)

filters **please ensure to implement ticker checking just incase as you will have the list of tickers**

example data point:
{"event":"update","payload":{"ticker":"btcusd","timestamp":1745985,"type":"Q","exchange":"crypto","ask_price":95054.32,"ask_size":0.0001052,"bid_price":95046.67,"bid_size":5.184e-05,"last_price":null,"last_size":null}}