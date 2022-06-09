import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "95.217.181.53", 8000):
        await asyncio.Future()  # run forever
        
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(main))