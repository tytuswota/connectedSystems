import socket
import json
from _thread import *
import os
import websockets
import asyncio
import select

HOST = "95.217.181.53"
PORT = 65433
WEBSOCKETPORT = 8000

obstacles = []

listOfUnits = [{"x":0,"y":10},
               {"x":0,"y":0},
               {"x":10,"y":10},
               {"x":10,"y":0}]

clients = {}

clientCount = 0

def multi_threaded_client(conn, clientIndex):
    unknownMsg = False
    while True:
        
        data = conn.recv(2048)
        messageToClient = {}

        if data == "":
            print("connection lost", conn.getpeername())
            break

        for messageString in data.decode("utf-8").split("|"):
            if len(messageString) > 0:
                print("client msg->", messageString)
                message = json.loads(messageString)
                messageId = message["messageId"]
                
                if messageId == 1:
                    id = message["unitID"]
                    
                    listOfUnits[id - 1]["x"] = message["x"]
                    listOfUnits[id - 1]["y"] = message["y"]

                    messageToClient = {"messageId":5, "list":listOfUnits}
                    
                elif messageId == 2:
                    id = message["unitID"]
                    exists = False
                    for obstacle in obstacles:
                        if len(obstacles) > 0:
                            if (obstacle["x"] == message["x"]) and (obstacle["y"] == message["y"]):
                                exists = True
                                break
                    if not exists:
                        obstacles.append({"x":message["x"],"y":message["y"]})
                    # update list of obstacles
                        messageToClient = {"messageId":0, "list":obstacles}
                    
                elif messageId == 3:
                    coords = message["coords"]
                    unitID = message["unitID"]
                    messageToClient = {"messageId":4, "unitID":unitID, "coords":coords}
                    # try:
                    #     conn.sendall(bytes((json.dumps({"messageId":4, "unitID":unitID, "coords":coords})), encoding="utf-8"))
                    # except (ValueError, BrokenPipeError, IOError):
                    #     pass
                    print("hij zit in messageID 4 ding")

                elif messageId == 6:
                    unitID = message["unitID"]
                    messageToClient = {"messageId":7, "unitID":unitID}

                else:
                    unknownMsg = True
                    print("unknown message id")

                try:
                    if not unknownMsg:
                        for c in clients.values():
                            c.sendall(bytes((json.dumps(messageToClient)), encoding="utf-8"))
                            c.sendall(bytes("|", encoding="utf-8"))
                    else:
                        unknownMsg = False

                except (ValueError, BrokenPipeError, IOError):
                    print("Connection  lost to", conn.getpeername ())
                    break  
    del clients[clientIndex]
    clientCount  -= 1
    if  clientCount  == 0:
        print("All  clients  disconnected; resetting")
    
        

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    while True:
        s.listen(5)
        conn, addr = s.accept()
        #clients.append(conn)
        clientIndex = len(clients)-1
        
        #if conn != NULL:
        clients[clientIndex] = conn
        clientCount += 1
        start_new_thread(multi_threaded_client, (conn, clientIndex,))
messages = {}



