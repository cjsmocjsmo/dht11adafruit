import asyncio
import websockets

async def receive_data():
    uri = "ws://10.0.4.60:9080/"
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        try:
            while True:
                message = await websocket.recv()
                print("Received:", message)
        except websockets.ConnectionClosed:
            print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(receive_data())