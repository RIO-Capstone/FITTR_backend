import asyncio
import websockets
import pandas as pd
from typing import Optional

class WebSocketHandler:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.websocket = None
        self.is_connected = False

    async def connect(self):
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.is_connected = True
            print(f"Connected to WebSocket server at ws://{self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")

    async def disconnect(self):
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
            print("WebSocket connection closed.")

    async def send(self, message: str):
        if self.websocket and self.is_connected:
            await self.websocket.send(message)

    async def receive(self) -> Optional[str]:
        if self.websocket and self.is_connected:
            try:
                return await self.websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed unexpectedly.")
        return None