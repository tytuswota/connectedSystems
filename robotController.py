from  controller  import  Supervisor
import time
import socket
import json

HOST = "95.217.181.53"
PORT = 65432 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


robot = Supervisor ()
supervisorNode = robot.getSelf ()
timestep = int(robot.getBasicTimeStep ())
duration = (1000  //  timestep) * timestep

id = int(robot.getName())

txMsgBuff = []

locationMsg = 1
obstacleMsg = 2

destination = {
    "x": 0,
    "y": 0
    }

def sendAllMsg():
    for i in range(len(txMsgBuff)):
        msg = txMsgBuff.pop()
        try:
            s.sendall(bytes(msg, encoding="utf-8"))
        except:
            print('Error sending message')
            txMsgBuff.append(msg)
        
def createMsg(type, pos):
    msg = {
        "messageId": type,
        "unitID": int(id),
        "x": pos[0],
        "y": pos[1]
        }
    txMsgBuff.append(json.dumps(msg))

def receiveMsg():
    return s.recv(1024).decode()

def setDestination(dest):
    x = dest["x"]
    y = dest["y"]
    destination.update({"x":x})
    destination.update({"y":y})

def parseMsg(msg):
    try:
        unitID = msg["unitID"]
        if unitID == id:
            messageID = msg["messageId"]
            if messageID == 4:
                coords = msg["coords"]
                print(coords)
                setDestination(coords)
    except:
        pass

def moveToDest(pos):
    xPos = pos[0] * 10
    yPos = pos[1] * 10
    
    xDest = destination.get("x")
    yDest = destination.get("y")
    trans = supervisorNode.getField("translation")
    
    # print(destination)
    
    xMov = 0
    yMov = 0
    if xPos < xDest:
        xMov = +.1
    elif xPos > xDest:
        xMov = -.1
    
    if yPos < yDest:
        yMov = +.1
    elif yPos > yDest:
        yMov = -.1
    
    trans.setSFVec3f([pos[0]+xMov, pos[1]+yMov, pos[2]])

#execute  every  second
while  robot.step(duration) !=  -1: 
    # get  position
    pos = supervisorNode.getPosition()
    posX = round (10 * pos [0]) # times  10  because  grid  size is 0.1 x 0.1 m
    posY = round (10 * pos [1])
    currentPosition = (posX, posY)
    
    # server communication
    createMsg(locationMsg, currentPosition)
    sendAllMsg()
    answer = json.loads(receiveMsg())
    parseMsg(answer)
    print(f"Received {answer!r}")
    
    # get handle to translation field & set pos(x, y, z)
    
    moveToDest(pos)
    
    time.sleep(2)