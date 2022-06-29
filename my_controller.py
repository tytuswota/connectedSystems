"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from  controller  import  Supervisor
import time
import socket
import json
import random


# Worlmap
mapH = 11
mapW = 11
map = [[0 for col in range(mapW)] for row in range(mapH)]

# list of locations of bots
botLocations = [[0,10], [0,0], [10,10], [10,0]]

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

# sensor setup
ds_up = robot.getDevice("ds_up")
ds_right = robot.getDevice("ds_right")
ds_down = robot.getDevice("ds_down")
ds_left = robot.getDevice("ds_left")

ds_up.enable(timestep)
ds_right.enable(timestep)
ds_down.enable(timestep)
ds_left.enable(timestep)

# LED setup
led0 = robot.getDevice("led0")
led1 = robot.getDevice("led1")
led2 = robot.getDevice("led2")
led3 = robot.getDevice("led3")

# Socket
HOST = "95.217.181.53"
PORT = 65433
s = socket.socket ()
try:
    s.connect ((HOST , PORT))
except:
    print ("Connection refused")
    exit ()


# messages 
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
            s.sendall(bytes("|", encoding="utf-8"))
        except:
            print('Error sending message')
            txMsgBuff.append(msg)

def receiveMsg():
    return s.recv(1024).decode()

def getCurrentPos():
    pos = supervisorNode.getPosition()
    posX = round (10 * pos [0]) # times  10  because  grid  size is 0.1 x 0.1 m
    posY = round (10 * pos [1])
    return ((posX, posY))
    
def getTarget():
    target = supervisorNode.getField("target")
    targetVec = target.getSFVec2f()
    xDest = int(targetVec [0])
    yDest = int(targetVec [1])
    return ((xDest,yDest))


def setDestination(dest):
    x = dest["x"]
    y = dest["y"]
    supervisorNode.getField("target").setSFVec2f([x,y])


def parseMsg(msg):
    try:
        messageID = msg["messageId"]
        
        #global messages
        if messageID == 0:  # New obstacles
            for i in range(len(msg["list"])):
                coords = msg["list"][i]
                updateMap(coords['x'], coords['y'])
            return
        if messageID == 5: #location of bots:
            
            for i in range(len(msg["list"])):
                coords = msg["list"][i]
                
                
                # map[botLocations[i][0]][botLocations[i][1]] = 0
                # botLocations[i][0] = coords['x']
                # botLocations[i][1] = coords['y']
                # map[botLocations[i][0]][botLocations[i][1]] = 2
            return
                  
        unitID = msg["unitID"]
        
        #bot specific messages
        if messageID == 4:  # New destination
            if unitID == id:
                coords = msg["coords"]
                setDestination(coords)
            return
        if messageID == 7: #noodstop
            if unitID == id:
                pos = getCurrentPos()
                supervisorNode.getField("target").setSFVec2f([pos[0],pos[1]])
            return
    except:
        print('Could not parse message')



def moveToDest(pos):
    global led0, led1, led2, led3, map

    # Here we get the target field and current Position
    currentPos = getCurrentPos()
    target = getTarget()
        
    if currentPos != target:
        moveTo = getNextStep(map, target)

        if moveTo[1] < currentPos[1]:
          resetLED()
          led1.set(1)
          
        if moveTo[0] > currentPos[0]:
          resetLED()
          led2.set(1)
          
        if moveTo[1] > currentPos[1]:
          resetLED()
          led0.set(1)

        if moveTo[0] < currentPos[0]:
          resetLED()
          led3.set(1)

        # get handle to translation field
        trans = supervisorNode.getField("translation")

        # set position; pos is a list with 3 elements: x, y and z coordinates
        trans.setSFVec3f([moveTo[0]/10, moveTo[1]/10, 0.05])
    elif currentPos[0] == target[0] and currentPos[1] == target[1]:
        targetReachedLed()



def resetLED():
  global led0, led1, led2, led3
  led0.set(0)
  led1.set(0)
  led2.set(0)
  led3.set(0)

def targetReachedLed():
  led0.set(1)
  led1.set(1)
  led2.set(1)
  led3.set(1)
  
def updateMap(mapX, mapY):
    if mapX >= mapW or mapX < 0 or mapY >= mapH or mapY < 0:
        return
    map[mapX][mapY] = 1


def isObstacleBot(pos):
    try:
        for locations in botLocations:
            if pos[0] == locations[0] and pos[1] == locations[1]:
                return True
        return False
    except:
        return False


def locateObstacles(currentPos):
    obst = []
    up = ds_up.getValue()
    down = ds_down.getValue()
    left = ds_left.getValue()
    right = ds_right.getValue()

    if right > 0:
        if not currentPos[0] >= mapW - 1:
            pos = (currentPos[0] + 1, currentPos[1])
            obst.append({'x': pos[0], 'y': pos[1]})
            updateMap(pos[0], pos[1])
    if left > 0:
        if not currentPos[0] <= 0:            
            pos = (currentPos[0] - 1, currentPos[1])
            obst.append({'x': pos[0], 'y': pos[1]})
            updateMap(pos[0], pos[1])
    if up > 0:
        if not currentPos[1] >= mapH - 1:
            pos = (currentPos[0], currentPos[1] + 1)
            obst.append({'x': pos[0], 'y': pos[1]})
            updateMap(pos[0], pos[1])
    if down > 0:
        if not currentPos[1] <= 0:  
            pos = (currentPos[0], currentPos[1] - 1)
            obst.append({'x': pos[0], 'y': pos[1]})
            updateMap(pos[0], pos[1])
    
    return obst

def getNextStep(botMap, target):
    currentPos = getCurrentPos()
    print("location x y:", currentPos[0], " ", currentPos[1])
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
    i,j = (currentPos[0],currentPos[1])
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
    return (the_path[len(the_path)-2])

def printMap():
    def rotate(array):
        R, C=len(array), len(array[0])
        newArr = [[None] * R for _ in range(C)]
        for c in range(C):
            for r in range(R-1, -1, -1):
                newArr[C-c-1][r] = array[r][c]
        return newArr
        
    transposedMap = rotate(map)
    for row in transposedMap:
        print(row)
    print(' ')
                
    
while robot.step(duration) != -1:
    currentPos = getCurrentPos()
    detectedObstacles = locateObstacles(currentPos)

    # create message and send it
    createMsg(locationMsg, currentPos)  
    for i in range(len(detectedObstacles)):
        createMsg(obstacleMsg, detectedObstacles[i])
    sendAllMsg()

    # receive message from the server
    messageFromServer = receiveMsg()
    
    for msg in messageFromServer.split("|"):
        try:   
            serverMessage = json.loads(msg)
            parseMsg(serverMessage)
            print(f"Received {serverMessage!r}")
        except ValueError:
            pass
    
    # move bot one step
    moveToDest(currentPos)
    
    #printMap()
    
    time.sleep(0.1)