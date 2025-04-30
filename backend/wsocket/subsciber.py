from fastapi.websockets import WebSocket
from typing import Dict, List, Set, Any
import logging

logger = logging.getLogger()

class SubscriptionManager:
    def __init__(self):
        # Stores per-client subscription info
        self.subscriptions: Dict[WebSocket, Dict[str, Any]] = {}

    def register_client(self, websocket: WebSocket):
        self.subscriptions[websocket] = {}

    def unregister_client(self, websocket: WebSocket):
        self.subscriptions.pop(websocket, None)

    def update_subscription(self, websocket: WebSocket, payload: Dict[str, Any]):
        filters = payload["filters"]
        if not isinstance(payload.get("exchange"), str):
            raise ValueError("Missing or invalid exchange in payload")
        if not isinstance(payload.get("filters"), dict):
            raise ValueError("Missing or invalid filters in payload")
        if "ticker" in filters and isinstance(filters["ticker"], list):
            filters["ticker"] = [t.lower() for t in filters["ticker"]]
            # Store the normalized payload
            self.subscriptions[websocket] = payload

    def clear_subscription(self, websocket: WebSocket):
        if websocket in self.subscriptions:
            self.subscriptions[websocket] = {}

    def get_matching_clients(self, market_data: Dict[str, Any]) -> List[WebSocket]:
        matched_clients = []

        data_exchange = market_data.get("exchange")
        if not data_exchange:
            return matched_clients

        for ws, config in self.subscriptions.items():
            logger.debug(f"[SUBS] client={ws} exchange={config.get('exchange')} filters={config.get('filters')}")
            if config.get("exchange") != data_exchange:
                continue

            filters = config.get("filters", {})
            if not filters:
                continue

            if self._matches_filters(market_data, filters):
                logger.debug(f"[MATCH] data ticker={market_data.get('ticker')} vs filters={filters.get('ticker')}")
                matched_clients.append(ws)

        return matched_clients


    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Evaluates if the incoming data matches the client's filters.
        Extend this method to support new filter types easily.
        """
        ticker = data.get("ticker") 
        volume = data.get("volume", 0)
        market_cap = data.get("market_cap", 0)
        sector = data.get("sector")

        # Ticker match
        if "ticker" in filters:
            tickers = filters["ticker"]
            if isinstance(tickers, list) and ticker not in tickers:
                return False

        # Sector match
        if "sector" in filters:
            sectors = filters["sector"]
            if isinstance(sectors, list) and sector not in sectors:
                return False

        # Volume range match
        if "volume_min" in filters and volume < filters["volume_min"]:
            return False
        if "volume_max" in filters and volume > filters["volume_max"]:
            return False

        # Market cap range match
        if "market_cap_min" in filters and market_cap < filters["market_cap_min"]:
            return False
        if "market_cap_max" in filters and market_cap > filters["market_cap_max"]:
            return False

        return True
    
    def get_all_symbols(self, exchange: str) -> Set[str]:
        symbols = set()
        for config in self.subscriptions.values():
            if config.get("exchange") != exchange:
                continue
            filters = config.get("filters", {})
            tickers = filters.get("ticker", [])
            if isinstance(tickers, list):
                symbols.update(tickers)
        return symbols

