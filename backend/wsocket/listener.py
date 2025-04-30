import asyncio
import websockets
import json
import logging
from settings.config import settings
from typing import Dict, Set

logger = logging.getLogger()

WS_URLS = {
    "company": "wss://websockets.financialmodelingprep.com",
    "crypto": "wss://crypto.financialmodelingprep.com",
    "forex": "wss://forex.financialmodelingprep.com"
}

class FMPListener:
    def __init__(self, exchange: str, subscription_manager, websocket_manager, poll_interval: float = 1.0):
        if exchange not in WS_URLS:
            raise ValueError(f"Unsupported exchange: {exchange}")
        self.exchange = exchange
        self.subscription_manager = subscription_manager
        self.websocket_manager = websocket_manager
        self.ws_url = WS_URLS[exchange]
        self._stop = False
        self.current_subs: Dict[str, Set[str]] = {
            "company": set(),
            "crypto": set(),
            "forex": set()
        }
        self.poll_interval = poll_interval

    def stop(self):
        self._stop = True

    async def start(self):
        while not self._stop:
            try:
                logger.info(f"[FMP:{self.exchange}] Connecting to {self.ws_url}")
                async with websockets.connect(self.ws_url) as ws:
                    await ws.send(json.dumps({"event": "login", "data": {"apiKey": settings.FMP_APIKEY}}))
                    resp = await ws.recv()
                    resp_obj = json.loads(resp)
                    if not (resp_obj.get("event") == "login" and resp_obj.get("status") == 200):
                        raise RuntimeError(f"FMP login failed: {resp_obj}")

                    manage_task = asyncio.create_task(self._manage_subscriptions(ws, self.exchange))

                    allowed_types = {"T", "Q", "B"}
                    async for message in ws:
                        try:
                            raw = json.loads(message)
                            if raw.get("type") not in allowed_types:
                                continue
                            normalized = self._normalize_data(raw, self.exchange)
                            if normalized:
                                clients = self.subscription_manager.get_matching_clients(normalized)
                                logger.info(clients)
                                for client in clients:
                                    await self.websocket_manager.send_personal_message({
                                        "event": "update",
                                        "payload": normalized
                                    }, client)
                        except json.JSONDecodeError as e:
                            logger.error(f"[FMP:{self.exchange}] JSON error: {e} - {message}")
                        except Exception as e:
                            logger.warning(f"[FMP:{self.exchange}] Processing error: {e}")

                    manage_task.cancel()
            except Exception as e:
                logger.error(f"[FMP:{self.exchange}] Connection error: {e}, retrying in 3s")
                await asyncio.sleep(3)

    async def _manage_subscriptions(self, ws, exchange: str):
        while not self._stop:
            try:
                desired = set(self.subscription_manager.get_all_symbols(exchange))
                current = self.current_subs[exchange]

                to_add = list(desired - current)
                to_remove = list(current - desired)

                if to_add:
                    await ws.send(json.dumps({"event": "subscribe", "data": {"ticker": to_add}}))
                    logger.info(f"[FMP:{exchange}] Subscribed to {to_add}")
                    current.update(to_add)

                if to_remove:
                    await ws.send(json.dumps({"event": "unsubscribe", "data": {"ticker": to_remove}}))
                    logger.info(f"[FMP:{exchange}] Unsubscribed from {to_remove}")
                    current.difference_update(to_remove)

            except Exception as e:
                logger.warning(f"[FMP:{exchange}] Subscription error: {e}")
            await asyncio.sleep(self.poll_interval)

    def _normalize_data(self, raw: dict, exchange: str) -> dict:
        try:
            symbol = raw.get("s")
            if not symbol:
                return None
            symbol = symbol.lower() 
            timestamp = self._parse_timestamp(raw.get("t"))
            return {
                "ticker": symbol,
                "timestamp": timestamp,
                "type": raw.get("type"),
                "exchange": exchange, 
                "ask_price": raw.get("ap"),
                "ask_size": raw.get("as"),
                "bid_price": raw.get("bp"),
                "bid_size": raw.get("bs"),
                "last_price": raw.get("lp"),
                "last_size": raw.get("ls"),
            }
        except Exception as e:
            logger.warning(f"[FMP:{exchange}] Normalization error: {e}")
            return None

    def _parse_timestamp(self, t_raw) -> int:
        if not t_raw:
            return 0
        try:
            return int(t_raw / 1e6) if t_raw > 1e12 else int(t_raw)
        except Exception:
            return 0
