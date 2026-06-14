
import time
import board
import adafruit_dht
import sqlite3
from datetime import datetime
import asyncio
import json
import websockets



# Database setup
conn = sqlite3.connect('dht11_readings.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        temp_f REAL NOT NULL,
        temp_c REAL NOT NULL,
        humidity REAL NOT NULL
    )
''')
conn.commit()


# Initialise the dht device, with data pin connected to GPIO 4:
dht_device = adafruit_dht.DHT11(board.D4)

print("Starting DHT11 readings with WebSocket streaming... Press Ctrl+C to exit.\n")

clients = set()

async def read_sensor():
    loop = asyncio.get_event_loop()
    try:
        temperature_c = await loop.run_in_executor(None, lambda: dht_device.temperature)
        humidity = await loop.run_in_executor(None, lambda: dht_device.humidity)
        temperature_f = temperature_c * (9 / 5) + 32
        temperature_c = round(temperature_c, 1)
        temperature_f = round(temperature_f, 1)
        return temperature_c, temperature_f, humidity
    except RuntimeError as error:
        print(f"Reading error: {error.args[0]}")
        return None, None, None
    except Exception as error:
        dht_device.exit()
        conn.close()
        raise error

async def sensor_loop():
    while True:
        temperature_c, temperature_f, humidity = await read_sensor()
        if temperature_c is not None and humidity is not None:
            timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
            c.execute(
                "INSERT INTO sensor_data (timestamp, temp_f, temp_c, humidity) VALUES (?, ?, ?, ?)",
                (timestamp, temperature_f, temperature_c, humidity)
            )
            conn.commit()
            data = {
                "temp_c": temperature_c,
                "temp_f": temperature_f,
                "humidity": humidity
            }
            message = json.dumps(data)
            # Broadcast to all connected clients
            if clients:
                await asyncio.gather(*(client.send(message) for client in clients))
            print(f"Sent: {message}")
        await asyncio.sleep(60)

async def handler(websocket, path=None):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def main():
    import websockets
    server = await websockets.serve(handler, "10.0.4.60", 9080)
    print("WebSocket server started on ws://10.0.4.60:9080/")
    await sensor_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        dht_device.exit()
        conn.close()

    # The DHT11 needs at least 1-2 seconds between readings
    time.sleep(30)