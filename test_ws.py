import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://127.0.0.1:8000/ws/museum"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server!")
            await websocket.send(json.dumps({"test": "data"}))
            print("Sent data")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
