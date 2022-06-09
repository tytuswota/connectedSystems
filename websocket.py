import asyncio
import websockets

async def handle_ws(websocket):
    print("someone has connected")

async def connectionFunction():
    async with websockets.serve(handle_ws, "95.217.181.53", 8000):
        await asyncio.Future() #draait het voor altijd

asyncio.run(connectionFunction())