from fastapi.websockets import WebSocket
from typing import Dict, List
import json
from .subsciber import SubscriptionManager


class WebSocketManager:
    def __init__(self, subscription_manager: SubscriptionManager):
        self.active_clients: List[WebSocket] = []
        self.client_subscriptions: Dict[WebSocket, dict] = {} 
        self.subscription_manager = subscription_manager
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_clients.append(websocket)
        self.subscription_manager.register_client(websocket)
        await self.send_personal_message({"event": "status", "payload": "Connected to Market Screener WebSocket"}, websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_clients:
            self.active_clients.remove(websocket)
        self.subscription_manager.unregister_client(websocket)
        if websocket in self.client_subscriptions:
            del self.client_subscriptions[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            # Log the error for debugging
            print(f"Error sending message: {e}")
            self.disconnect(websocket)
        
    async def receive_event(self, websocket: WebSocket, data: dict):
        event = data.get("event")
        payload = data.get("payload", {})

        if event in {"subscribe", "update_subscription"}:
            try:
                self.subscription_manager.update_subscription(websocket, payload)
                await self.send_personal_message({
                    "event": f"{event}",
                    "payload": payload
                }, websocket)
            except Exception as e:
                await self.send_personal_message({
                    "event": "error",
                    "payload": f"Invalid payload: {e}"
                }, websocket)

        elif event == "unsubscribe":
            self.subscription_manager.clear_subscription(websocket)
            await self.send_personal_message({
                "event": "unsubscribed",
                "payload": {}
            }, websocket)

        else:
            await self.send_personal_message({
                "event": "error",
                "payload": f"Unknown event: {event}"
            }, websocket)


    async def broadcast_filtered(self, market_data: dict):
        matching_clients = self.subscription_manager.get_matching_clients(market_data)
        for websocket in matching_clients:
            await self.send_personal_message({
                "event": "update",
                "payload": market_data
            }, websocket)