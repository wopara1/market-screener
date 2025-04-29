from fastapi import FastAPI
from settings.config import settings
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
import asyncio
from tickers import initialize_tickers, fetch_cot_list
import uvicorn
import logging
from tickers.routes import ticker_router
from technicals.routes import technicals_router

# Config logging
logging.basicConfig(level=logging.DEBUG)
    
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

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="debug")
