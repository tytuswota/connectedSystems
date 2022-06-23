"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from  controller  import  Supervisor
import time
import socket
import json
import random

# save current position
currentPosition = ()

# save target of bot
# target = (3,9)

# Worlmap
mapH = 10
mapW = 10
map = [[0 for col in range(mapW)] for row in range(mapH)]

# create the Robot instance
robot = Supervisor()
supervisorNode = robot . getSelf ()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# calculate a multiple of timestep close to one second
duration = (1000 // timestep ) * timestep

# 
id = int(robot.getName())
distanceSensors = []
txMsgBuff = []

#These are identifiers for the type of message
locationMsg = 1
obstacleMsg = 2

destination = {
    "x": 0,
    "y": 0
    }

# Socket
HOST = "95.217.181.53"
PORT = 65433
s = socket.socket ()
try:
    s.connect ((HOST , PORT))
except:
    print ("Connection refused")
    exit ()

def createMsg(type, pos):
    if type == locationMsg:
        msg = {
            "messageId": type,
            "unitID": int(id),
            "x": pos[0],
            "y": pos[1]
            }
    elif type == obstacleMsg:
        msg = {
            "messageId": type,
            "unitID": int(id),
            "x": pos['x'],
            "y": pos['y']
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
    supervisorNode.getField("target").setSFVec2f([x,y])

def updateMap(obstacle):
    map[obstacle['y']][obstacle['x']] = 1
                
def parseMsg(msg):
    try:
        messageID = msg["messageId"]
        if messageID == 0:
            for i in range(len(msg["list"])):
                updateMap(msg["list"][i])
        if messageID == 4:
            unitID = msg["unitID"]
            if unitID == id:
                coords = msg["coords"]
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

    global currentPosition, led0, led1, led2, led3, map

    posX = round(10 * pos [0]) # times 10 because grid size is 0.1 x 0.1 m
    posY = round(10 * pos [1])

    currentPosition = (posX, posY)
    
    #Here we take get the target field from the proto
    target = supervisorNode.getField("target")
    targetVec = target.getSFVec2f()
    xDest = int(targetVec [0])
    yDest = int(targetVec [1])

    if currentPosition != target:

        moveTo = getNextStep(map, (xDest, yDest))


        # turn on the right LED for direction
        if moveTo == (posY-1, posX):
          resetLED()
          led0.set(1)
        elif moveTo == (posY, posX+1):
          resetLED()
          led1.set(1)
        elif moveTo == (posY+1, posX):
          resetLED()
          led2.set(1)
        elif moveTo == (posY, posX-1):
          resetLED()
          led3.set(1)   

        # get handle to translation field
        trans = supervisorNode.getField("translation")

        # set position; pos is a list with 3 elements: x, y and z coordinates
        trans.setSFVec3f([moveTo[0]/10, moveTo[1]/10, pos[2]])
    else:
        resetLED()


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

def updateObsMap(mapX, mapY):
    if mapX >= mapW or mapX < 0 or mapY >= mapH or mapY < 0:
        return
    if map[mapX][mapY] != 1:
        map[mapX][mapY] = 1

def locateObstacles(currentPos):
    obst = []
    up = ds_up.getValue()
    down = ds_down.getValue()
    left = ds_left.getValue()
    right = ds_right.getValue()
    
    if right > 0:
        if not currentPos[0] >= mapW - 1:
            obst.append({'x': currentPos[0] + 1, 'y': currentPos[1]})
            updateObsMap(currentPos[0] + 1, currentPos[1])
    if left > 0:
        if not currentPos[0] <= 0:
            obst.append({'x': currentPos[0] - 1, 'y': currentPos[1]})
            updateObsMap(currentPos[0] - 1, currentPos[1])
    if up > 0:
        if not currentPos[1] >= mapH - 1:
            obst.append({'x': currentPos[0], 'y': currentPos[1] + 1})
            updateObsMap(currentPos[0], currentPos[1] + 1)
    if down > 0:
        if not currentPos[1] <= 0:
            obst.append({'x': currentPos[0], 'y': currentPos[1] - 1})
            updateObsMap(currentPos[0], currentPos[1] - 1)
    
    return obst

def getNextStep(botMap, target):
    global currentPosition
    def make_step(k):
      for i in range(len(m)):
        for j in range(len(m[i])):
          if m[i][j] == k:
            if i>0 and m[i-1][j] == 0 and botMap[i-1][j] == 0:
              m[i-1][j] = k + 1
            if j>0 and m[i][j-1] == 0 and botMap[i][j-1] == 0:
              m[i][j-1] = k + 1
            if i<len(m)-1 and m[i+1][j] == 0 and botMap[i+1][j] == 0:
              m[i+1][j] = k + 1
            if j<len(m[i])-1 and m[i][j+1] == 0 and botMap[i][j+1] == 0:
               m[i][j+1] = k + 1

    m = []
    for i in range(len(botMap)):
        m.append([])
        for j in range(len(botMap[i])):
            m[-1].append(0)
    i,j = currentPosition
    m[i][j] = 1
  
    k = 0
    while m[target[0]][target[1]] == 0:
        k += 1
        make_step(k)
  
  
    i, j = target
    k = m[i][j]
    the_path = [(i,j)]
    while k > 1:
        if i > 0 and m[i - 1][j] == k-1:
            i, j = i-1, j
            the_path.append((i, j))
            k-=1
        elif j > 0 and m[i][j - 1] == k-1:
            i, j = i, j-1
            the_path.append((i, j))
            k-=1
        elif i < len(m) - 1 and m[i + 1][j] == k-1:
            i, j = i+1, j
            the_path.append((i, j))
            k-=1
        elif j < len(m[i]) - 1 and m[i][j + 1] == k-1:
            i, j = i, j+1
            the_path.append((i, j))
            k -= 1
  
    # return next step
    # print (the_path)
    # print(the_path[len(the_path)-2])
    return (the_path[len(the_path)-2])


while robot.step(duration) != -1:

    # get position
    # print(map)
    pos = supervisorNode.getPosition()
    posX = round (10 * pos [0]) # times  10  because  grid  size is 0.1 x 0.1 m
    posY = round (10 * pos [1])
    currentPosition = (posX, posY)
    

    #server communication
    # create message and send it
    createMsg(locationMsg, currentPosition)
    
    detectedObstacles = locateObstacles(currentPosition)

    for i in range(len(detectedObstacles)):
        createMsg(obstacleMsg, detectedObstacles[i])
   
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