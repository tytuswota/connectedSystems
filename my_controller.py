"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from  controller  import  Supervisor
import time
import socket
import json
import random

HOST = "95.217.181.53"
PORT = 65433

# create the Robot instance
robot = Supervisor()
supervisorNode = robot . getSelf ()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# calculate a multiple of timestep close to one second
duration = (1000 // timestep ) * timestep


distanceSensors = []



id = int(robot.getName())
txMsgBuff = []

#These are identifiers for the type of message
locationMsg = 1
obstacleMsg = 2

destination = {
    "x": 0,
    "y": 0
    }


s = socket.socket ()

try:
    s.connect ((HOST , PORT))
except:
    print ("Connection refused")
    exit ()

def createMsg(type, pos):
    msg = {
        "messageId": type,
        "unitID": int(id),
        "x": pos[0],
        "y": pos[1]
        }
    txMsgBuff.append(json.dumps(msg))

def sendAllMsg():
    for i in range(len(txMsgBuff)):
        msg = txMsgBuff.pop()
        try:
            s.sendall(bytes(msg, encoding="utf-8"))
        except:
            print('Error sending message')
            txMsgBuff.append(msg)

def receiveMsg():
    return s.recv(1024).decode()

def setDestination(dest):
    x = dest["x"]
    y = dest["y"]
    # destination.update({"x":x})
    # destination.update({"y":y})
    print("in dest func:", x)
    print("in dest func:", y)
    supervisorNode.getField("target").setSFVec2f([x,y])



def parseMsg(msg):
    print("in parse message")
    try:
        unitID = msg["unitID"]
        if unitID == id:
            messageID = msg["messageId"]
            if messageID == 4:
                coords = msg["coords"]
                print(coords)
                setDestination(coords)
    except:
        print('Could not parse message')


ds_up = robot.getDevice("ds_up")
ds_right = robot.getDevice("ds_right")
ds_down = robot.getDevice("ds_down")
ds_left = robot.getDevice("ds_left")
ds_up.enable(timestep)
ds_right.enable(timestep)
ds_down.enable(timestep)
ds_left.enable(timestep)


def moveToDest(pos):

    posX = round(10 * pos [0]) # times 10 because grid size is 0.1 x 0.1 m
    posY = round(10 * pos [1])

    #Here we take get the target field from the proto
    target = supervisorNode.getField("target")
    targetVec = target.getSFVec2f()
    tarX = int(targetVec [0])
    tarY = int(targetVec [1])

    # xDest = destination.get("x")
    # yDest = destination.get("y")

    xDest = tarX
    yDest = tarY
    trans = supervisorNode.getField("translation")

    xMov = 0
    yMov = 0
    if posX < xDest:
        xMov = +.1
        resetLED()
        led2.set(1)
    if posX > xDest:
        xMov = -.1
        resetLED()
        led3.set(1)
    if posY < yDest:
        yMov = +.1
        resetLED()
        led0.set(1)
    if posY > yDest:
        yMov = -.1
        resetLED()
        led1.set(1)

    trans.setSFVec3f([pos[0]+xMov, pos[1]+yMov, pos[2]])



# LED setup
led0 = robot.getDevice("led0")
led1 = robot.getDevice("led1")
led2 = robot.getDevice("led2")
led3 = robot.getDevice("led3")

def resetLED():
  global led0, led1, led2, led3
  led0.set(0)
  led1.set(0)
  led2.set(0)
  led3.set(0)


def locateObstacles(currentPos):
    obstacles = []
    up = ds_up.getValue()
    down = ds_down.getValue()
    left = ds_left.getValue()
    right = ds_right.getValue()
    
    target = supervisorNode.getField("target")
    
    if right > 0:
        obstacles.append((currentPos[0] + 1, currentPos[1]))
        
        print('right')
    if left > 0:
        obstacles.append((currentPos[0] - 1, currentPos[1]))
        print('left')
    if up > 0:
        obstacles.append((currentPos[0], currentPos[1] + 1))
        target.setSFVec2f([0,9])
        print('up')
    if down > 0:
        obstacles.append((currentPos[0], currentPos[1] - 1))
        print('down')
    
    return obstacles


while robot.step(duration) != -1:

# get position
    pos = supervisorNode.getPosition()

    posX = round (10 * pos [0]) # times  10  because  grid  size is 0.1 x 0.1 m
    posY = round (10 * pos [1])
    currentPosition = (posX, posY)
    

    #server communication
    # create message and send it
    createMsg(locationMsg, currentPosition)

    obstacles = locateObstacles(currentPosition)
    print(obstacles)
    # obstacleLocation = ((posX + ds0.getValue()), (posY + ds1.getValue()))
    # createMsg(obstacleMsg, obstacleLocation)
    # obstacleLocation = ((posX - ds2.getValue()), (posY - ds3.getValue()))
    # createMsg(obstacleMsg, obstacleLocation)

    sendAllMsg()

    # receive message from the server
    messageFromServer = receiveMsg()

    try:
        serverMessage = json.loads(messageFromServer)
        parseMsg(serverMessage)
        print(f"Received {serverMessage!r}")
    except ValueError:
        pass

    moveToDest(pos)

    time.sleep(2)