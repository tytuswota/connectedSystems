import asyncio
import websockets
import json
import socket
from _thread import *

HOST = "95.217.181.53"
PORT = 65433 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(0.0010)

txMsgBuff = []
msgBuffer = ""

def sendAllMsg():
    for i in range(len(txMsgBuff)):
        msg = txMsgBuff.pop()
        try:
            s.sendall(bytes(msg, encoding="utf-8"))
        except:
            print('Error sending message')
            txMsgBuff.append(msg)

def receiveMsg():
    message = ""
    try:
        message = s.recv(1024).decode()
        
    except socket.timeout as e:
        # If there isnt any data on the socket keep going
        pass
    return message

async def echo(websocket):
    async for message in websocket:
        try:
            
            #zet de message on naar het protocol
            #stuur de protocol message naar de server
            print("in the echo function")
            
            jsonMessage = json.loads(message)
            print("the json->", jsonMessage)
            if jsonMessage['message_id'] == 6:
                print("1111111111111")
                msg = {
                        "messageId": 6,
                        "unitID": jsonMessage['bot_id'],
                }
                txMsgBuff.append(json.dumps(msg))
                print(msg)
            if jsonMessage['message_id'] == 9:
                #jsonMessage = json.loads(message)   
                print("heeeeeeeeeeee")
                msg = {
                        "messageId": 3,
                "unitID": jsonMessage['bot_id'],
                "coords":{"x": jsonMessage['x_dest'],
                "y": jsonMessage['y_dest']
                }}
                txMsgBuff.append(json.dumps(msg))
            
                print(msg)

            sendAllMsg()
        except:
            print("aaaaaaaaaaaaaaaaaaaaa")
            pass   
        
        serverMsg = receiveMsg() 
        print("message from the server->", serverMsg)
        await websocket.send(serverMsg)

async def main():
    async with websockets.serve(echo, "95.217.181.53", 8000):
        await asyncio.Future()  # run forever
        
#loop = asyncio.get_event_loop()
#loop.run_until_complete(main)

asyncio.run(main())
