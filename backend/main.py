import json
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from settings.config import settings
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from tickers import initialize_tickers, fetch_cot_list
from tickers.routes import ticker_router
from technicals.routes import technicals_router
from wsocket.manager import WebSocketManager
from wsocket.listener import FMPListener
from wsocket.subsciber import SubscriptionManager

# Initialize components
subscription_manager = SubscriptionManager()
websocket_manager = WebSocketManager(subscription_manager)

# Exchanges to support
EXCHANGES = ["company", "crypto", "forex"]

# Config logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# --- FastAPI Application Initialization ---
app = FastAPI(title="Market-Sceener")

# --- Middleware Configuration ---
origins = settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Market-Sceener API"}

# --- Start up & Shut Down --
@app.on_event("startup")
async def on_startup():
    await asyncio.gather(initialize_tickers(), fetch_cot_list())

# --- API Routes Inclusion ---
app.include_router(ticker_router, prefix='/tickers')
app.include_router(technicals_router, prefix='/technicals')

# --- Health Check and Root Endpoints ---
@app.get("/ping")
async def health_check():
    return {"message": "pong"} 

## -- Websocket --
@app.on_event("startup")
async def startup():
    for exchange in EXCHANGES:
        listener = FMPListener(
            exchange=exchange,
            subscription_manager=subscription_manager,
            websocket_manager=websocket_manager
        )
        asyncio.create_task(listener.start())

@app.websocket("/ws")
async def market_ws(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket_manager.receive_event(websocket, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        websocket_manager.disconnect(websocket)
        print(f"WebSocket error: {e}")