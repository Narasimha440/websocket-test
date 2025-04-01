import os
import asyncio
import websockets
import json

PORT = 8765  # Use a static port for now
rooms = {}  # Dictionary to store rooms and connected clients

async def handler(websocket, path):
    try:
        data = await websocket.recv()
        message = json.loads(data)

        if message["type"] == "join":
            room_code = message["room"]
            if room_code not in rooms:
                rooms[room_code] = set()
            rooms[room_code].add(websocket)
            await broadcast(room_code, f"User joined room {room_code}!")

        async for message in websocket:
            msg_data = json.loads(message)
            if msg_data["type"] == "chat":
                await broadcast(msg_data["room"], msg_data["message"])

    except websockets.exceptions.ConnectionClosed:
        for room, clients in rooms.items():
            if websocket in clients:
                clients.remove(websocket)
                await broadcast(room, "A user left the chat.")
                break

async def broadcast(room, message):
    """Send a message to all clients in a room."""
    if room in rooms:
        clients = list(rooms[room])
        for client in clients:
            try:
                await client.send(json.dumps({"message": message}))
            except websockets.exceptions.ConnectionClosed:
                clients.remove(client)

async def start_server():
    async with websockets.serve(handler, "localhost", PORT):  # ✅ FIX: Use localhost
        print(f"WebSocket server running on ws://localhost:{PORT}")
        await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(start_server())
