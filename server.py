import os
import asyncio
import websockets
import json

PORT = int(os.environ.get("PORT", 8765))  # Use the port assigned by Railway or fallback to 8765
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
    # ✅ Change localhost to 0.0.0.0
    async with websockets.serve(handler, "0.0.0.0", PORT):  # Allow external access
        print(f"WebSocket server running on ws://0.0.0.0:{PORT}")
        await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(start_server())
