import asyncio
import websockets
import json
import socket

HOST = "95.217.181.53"
PORT = 65432 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

txMsgBuff = []

def sendAllMsg():
    for i in range(len(txMsgBuff)):
        msg = txMsgBuff.pop()
        try:
            s.sendall(bytes(msg, encoding="utf-8"))
        except:
            print('Error sending message')
            txMsgBuff.append(msg)

async def echo(websocket):
    async for message in websocket:
        try:
            
            #zet de message on naar het protocol
            #stuur de protocol message naar de server
            jsonMessage = json.loads(message)

            msg = {
            "messageId": 4,
            "unitID": jsonMessage['bot_id'],
            "x": jsonMessage['x_dest'],
            "y": jsonMessage['y_dest']
            }
            txMsgBuff.append(json.dumps(msg))
            
            sendAllMsg()
        except:
            pass
        #await websocket.send(message)

async def main():
    async with websockets.serve(echo, "95.217.181.53", 8000):
        await asyncio.Future()  # run forever
        
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(main))