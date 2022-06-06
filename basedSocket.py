import socket
import json
from _thread import *
import os

HOST = "95.217.181.53"
PORT = 65432

obstacles = []

listOfUnits = [{"x":0,"y":0},
               {"x":0,"y":0},
               {"x":0,"y":0},
               {"x":0,"y":0}]

clients = []

def multi_threaded_client(conn):
    while True:
        try:
            data = conn.recv(2048)

            message = json.loads(data.decode("utf-8"))
            messageId = message["messageId"]
            print(messageId)
            if messageId == 1:
                id = message["unitID"]
                
                listOfUnits[id - 1]["x"] = message["x"]
                listOfUnits[id - 1]["y"] = message["y"]

                print("current location given")
                print("current list of units")
                print("====================")
                for unit in listOfUnits:
                    print(unit)
                print("====================")
            elif messageId == 2:
                print("location of obstacle was given")
                id = message["unitID"]
                print(message["x"])
                exists = False
                for obstacle in obstacles:
                    if len(obstacles) > 0:
                        if (obstacle["x"] == message["x"]) and (obstacle["y"] == message["y"]):
                            exists = True
                if(not exists):
                    obstacles.append({"x":message["x"],"y":message["y"]})
                
                # update list of obstacles
                messageForBot = {"messageId":0, "list":obstacles}
            
                try:
                    for c in clients:
                        c.sendall(bytes(json.dumps(messageForBot), encoding="utf-8"))
                except ValueError:
                    pass
                print(messageForBot)
                
            elif messageId == 3:
                coords = message["coords"]
                unitID = message["unitID"]
                messageForBot = {"messageId":4, "unitID":unitID, "coords":coords}

                try:
                    for c in clients:
                        c.sendall(bytes(json.dumps(messageForBot), encoding="utf-8"))
                except ValueError:
                    pass
            else:
                print("unknown message id")
        except ValueError:
            clients.pop(0)
            pass
        conn.sendall(data)
  
    clients.pop(0)
    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    while True:
        s.listen(5)
        conn, addr = s.accept()
        clients.append(conn)
        start_new_thread(multi_threaded_client, (conn, ))

            