from sense_emu import SenseHat
from collections import deque
from itertools import cycle
from time import sleep

import random
import math

sense = SenseHat()

class Coordinates:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def addCoords(self, Coords):
        return Coordinates(self.x + Coords.x, self.y + Coords.y)

    def moveCoords(self, Coords):
        self.x = self.x + Coords.x
        self.y = self.y + Coords.y

    def expandCoords(self):
        return Coordinates(self.x*2, self.y*2)

    def validCoords(self, width, height):
        if self.x < 0 or self.x >= width:
            return False
        if self.y < 0 or self.y >= height:
            return False

        return True

    def isEqual(self, coords):
        return coords.x == self.x and coords.y == self.y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

DIRECTIONS = [Coordinates(0, -1), Coordinates(0, 1), Coordinates(-1, 0), Coordinates(1, 0)]

class Node(Coordinates):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.connections = []
        self.visited = False
        self.walls = [0, 0, 0, 0] # U, D, R, L

    def addConnections(self, connectedNode):
        self.connections.append(connectedNode)
        self.addWall(connectedNode)
    
    def addWall(self, connectedNode):
        for i in range(len(DIRECTIONS)):
            if connectedNode.isEqual(self.addCoords(DIRECTIONS[i])) == True:
                self.walls[i] = 1
                return

    def isConnectedDirection(self, coords):
        for i in range(len(self.connections)):
            if self.connections[i].isEqual(coords):
                return True
        return False

    def mark(self):
        self.visited = True;

    def __str__(self):
        return f"({self.x}, {self.y}, {len(self.connections)})"

    def __repr__(self):
        return f"({self.x}, {self.y}, {len(self.connections)}))"

class Player(Coordinates):
    def __init__(self, start=Coordinates(1, 0)):
        super().__init__(start.x, start.y)

    def move(self, direction):
        self.moveCoords(direction)

class Maze:
    def __init__(self, w, h, start=Coordinates(0,0)):
        self.width = w
        self.height = h
        self.startCoords = start

        # Contains all nodes
        self.data = []

        # Maze with walls [Populated after DFS maze generation]
        self.mazeDisplay = []

        self.blankSpace = ' '
        self.wall = '#'

        self.initializeNodes()
        self.initMazeDisplay()

        self.createMaze()
    
    # START DEBUG PRINTS
    def display(self):
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                print(self.data[i][j].visited, end=' ')
                print(len(self.data[i][j].connections), end=' ')
            print(' ')
    
    def showMaze(self):
        print('#'*(len(self.mazeDisplay[0])+1))
        for i in range(len(self.mazeDisplay)):
            self.mazeDisplay[i].insert(0, '#')
            line = ''.join(self.mazeDisplay[i])
            print(line)
    # END DEBUG PRINTS

    # START INITIALIZE ARRAYS
    def initializeNodes(self):
        for i in range(self.height):
            rowAra = []
            for j in range(self.width):
                rowAra.append(Node(j, i))
            self.data.append(rowAra)

    def initMazeDisplay(self):
        self.mazeDisplay = [[ '#' for x in range(0,self.width*2)] for y in range(0,self.height*2)]
    #END INITIALIZE ARRAYS

    def getNode(self, coords):
        return self.data[coords.y][coords.x]

    def markNode(self, coords):
        self.getNode(coords).mark()

    # START Helper functions for @self.draw()
    def clearWall(self, coords):
        self.mazeDisplay[coords.y][coords.x] = self.blankSpace

    def addWall(self, coords):
        self.mazeDisplay[coords.y][coords.x] = '#'
    
    def setStart(self, coords):
        self.mazeDisplay[coords.y][coords.x] = 'S'

    def setEnd(self, coords):
        self.mazeDisplay[coords.y][coords.x] = 'E'

    # END Helper functions for @self.draw()

    # Populates @self.mazeDisplay
    def draw(self):
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                currentNode = self.getNode(Coordinates(j, i))
                for k in range(len(DIRECTIONS)):
                    tempPos = currentNode.addCoords(DIRECTIONS[k])
                    if not tempPos.validCoords(self.width, self.height):
                        continue
                    if currentNode.isConnectedDirection(tempPos) == True:
                        self.clearWall(currentNode.expandCoords().addCoords(DIRECTIONS[k]))
                        self.clearWall(currentNode.expandCoords())
                    else:
                        self.addWall(currentNode.expandCoords().addCoords(DIRECTIONS[k]))

        #ADD LEFT
        for i in range(len(self.mazeDisplay)):
            self.mazeDisplay[i].insert(0, '#')
        
        #ADD TOP BORDER
        tAra = []
        for i in range(len(self.mazeDisplay[0])):
            tAra.append('#')

        self.mazeDisplay.insert(0, tAra)


    def checkForUnvisitedNeighbors(self, curNode):

        directions = DIRECTIONS.copy() #[Coordinates(1, 0), Coordinates(-1, 0), Coordinates(0, 1), Coordinates(0, -1)]
        random.shuffle(directions)
        validNeighbors = []

        for i in range(len(directions)):
            tempCoords = curNode.addCoords(directions[i])

            if not tempCoords.validCoords(self.width, self.height):
                continue

            if self.getNode(tempCoords).visited:
                continue

            validNeighbors.append(self.getNode(tempCoords))

        if len(validNeighbors) == 0:
            return None
        else:
            return validNeighbors[0]

        return None

    def createMaze(self):
        startNode = self.getNode(self.startCoords)
        startNode.mark()

        path = []

        path.append(startNode)

        while len(path) > 0:

            curNode = path[0]

            nextNode = self.checkForUnvisitedNeighbors(curNode) 

            if nextNode is not None:
                nextNode = self.getNode(nextNode) # Maybe redundant get?
                nextNode.addConnections(path[0])
                path[0].addConnections(nextNode)
                nextNode.mark()
                path.insert(0, nextNode)
            else:
                path.pop(0)

    def findLongestPath(self):
        visited = []
        distance = []
        path = []
        firstNode = False

        for i in range(len(self.mazeDisplay)):
            tempRow = []
            tDistance = []
            for j in range(len(self.mazeDisplay[i])):
                if self.mazeDisplay[i][j] == ' ':
                    if firstNode == False:
                        firstNode = Coordinates(j, i)
                        self.setStart(firstNode)
                        tempRow.append(True)
                        tDistance.append(0)
                    else:
                        tempRow.append(False)
                        tDistance.append(-1)
                else:
                    tempRow.append(True)
                    tDistance.append(-1)
            visited.append(tempRow)
            distance.append(tDistance)
    
        path.append(firstNode)
        self.startCoords = firstNode
        furthestNeighbor = Coordinates(0, 0)
        longestPathLength = 0

        while len(path) > 0:
            curNode = path.pop()
            foundNeighbor = False


            for i in range(len(DIRECTIONS)):
                nextNode = curNode.addCoords(DIRECTIONS[i])
                
                if not nextNode.validCoords(len(self.mazeDisplay[0]), len(self.mazeDisplay)): 
                    continue
                
                if visited[nextNode.y][nextNode.x] == False:
                    visited[nextNode.y][nextNode.x] = True
                    path.insert(0, nextNode)
                    distance[nextNode.y][nextNode.x] = distance[curNode.y][curNode.x] + 1
                    foundNeighbor = True
            
        maxDistance = 0
        for i in range(len(distance)):
            for j in range(len(distance[i])):
                if distance[i][j] > maxDistance:
                    maxDistance = distance[i][j]
                    furthestNeighbor = Coordinates(j, i)
        
        self.setEnd(furthestNeighbor)

class Game:
    def __init__(self, w, h, rot=180):
        self.maze = Maze(w, h)

        self.initMaze()
        
        self.Player = Player(self.maze.startCoords)
        self.data = self.maze.mazeDisplay

        self.rotation = (rot % 360) # Standardize screen rotation
        self.moveDirection = deque([Coordinates(0, -1), Coordinates(-1, 0), Coordinates(0, 1), Coordinates(1, 0)]) # UP, LEFT, DOWN, RIGHT
        self.initMoveDirections()


        self.open = (0, 0, 0)
        self.closed = (255, 255, 255)
        self.start = (0, 125, 0)
        self.end = (125, 0, 0)
        self.player = (0, 0, 125)

        # DEBUG SHOW MAZE
        #self.maze.showMaze()
        for i in range(len(self.data)):
            tStr = ''
            for j in range(len(self.data[i])):
                tStr = tStr + self.data[i][j]

            print(tStr)
   
    def main(self):
        #[Coordinates(0, 1), Coordinates(1, 0), Coordinates(-1, 0), Coordinates(0, -1)]
        self.render()
        while self.winCondition() == False:
            playerMoved = False
            for event in sense.stick.get_events():
                #print(event.direction, event.action)
                if event.action == 'pressed':
                    if event.direction == 'up':
                        playerMoved = self.movePlayer(self.moveDirection[0])
                        break
                    elif event.direction == 'left':
                        playerMoved = self.movePlayer(self.moveDirection[1])
                        break
                    elif event.direction == 'down':
                        playerMoved = self.movePlayer(self.moveDirection[2])
                        break
                    elif event.direction == 'right':
                        playerMoved = self.movePlayer(self.moveDirection[3])
                        break
                           
            if playerMoved == True:   
                self.render()
                
            sleep(.01)
            
        sense.clear()
        sense.show_message("You Finished!", )
    
    def initMoveDirections(self):
        tempRotation = math.floor(self.rotation / 90)
        if self.rotation / 90 == 0:
            return

        tempRotation = 0 - tempRotation

        self.moveDirection.rotate(tempRotation)


    def render(self):

        renderPixels = []
        
        renderBoxMin = self.setRenderBoxMin()
        renderBoxMax = self.setRenderBoxMax()
        
        # Normalize render zone to an 8x8 area, around the Player
        if renderBoxMax.y - 8 < renderBoxMin.y:
            if renderBoxMin.y == 0:
                renderBoxMax.y = 8
            else:
                renderBoxMin.y = renderBoxMax.y - 8

        if renderBoxMax.x - 8 < renderBoxMin.x:
            if renderBoxMin.x == 0:
                renderBoxMax.x = 8
            else:
                renderBoxMin.x = renderBoxMax.x - 8

        for i in range(renderBoxMin.y, renderBoxMax.y):
            for j in range(renderBoxMin.x, renderBoxMax.x):
                if i == self.Player.y and j == self.Player.x:
                    renderPixels.append(self.player)
                elif self.data[i][j] == 'S':
                    renderPixels.append(self.start)
                elif self.data[i][j] == 'E':
                    renderPixels.append(self.end)
                elif self.data[i][j] == ' ':
                    renderPixels.append(self.open)
                elif self.data[i][j] == '#':
                    renderPixels.append(self.closed)
        
        sense.clear()
        sense.set_pixels(renderPixels)
        return None

    def winCondition(self):
        return self.getValue(self.Player) == 'E'

    def movePlayer_DEBUG(self): 
        priorityDir = [Coordinates(0, 1), Coordinates(1, 0), Coordinates(-1, 0), Coordinates(0, -1)]
        for i in range(len(priorityDir)):
            if self.checkWallFromPlayer(priorityDir[i]):
                self.Player.move(priorityDir[i])
                return
        return

    def movePlayer(self, direction):
        if self.checkWallFromPlayer(direction):
            self.Player.move(direction)
            return True
            
        return False
                              
    def getValue(self, coords):
        return self.data[coords.y][coords.x]

    def checkWallFromPlayer(self, direction):
        tPos = self.Player.addCoords(direction)
        if not tPos.validCoords(len(self.data[0]), len(self.data)):
            return False
        if self.getValue(tPos) != '#':
            return True

        return False

    def setRenderBoxMin(self):
        tX = 0 if self.Player.x - 3 < 0 else self.Player.x - 3
        tY = 0 if self.Player.y - 4 < 0 else self.Player.y - 4

        return Coordinates(tX, tY)

    def setRenderBoxMax(self):
        tX = len(self.data[0]) if self.Player.x + 5 > len(self.data[0]) else self.Player.x + 5
        tY = len(self.data) if self.Player.y + 4 > len(self.data) else self.Player.y + 4

        return Coordinates(tX, tY)
    
    def initMaze(self):
        self.maze.draw()
        self.maze.findLongestPath()
        #self.maze.showMaze()
        return

class Menu:
    def __init__(self, sen, lowLight=True, rot=0):

        self.sense = sen
        
        self.rotation = (rot % 360) # Standardize screen rotation
        self.rotateDirection = deque(['UP', 'LEFT', 'DOWN', 'RIGHT'])
        self.initRotateDirections()

        self.sense.clear()
        self.sense.set_rotation(rot)
        self.sense.low_light = lowLight

        self.MENUS = {
            'initMenu': 
                [
                    {
                        'TEXT': 'START',
                        'NEXT': None,
                        'FUNC': self.runMaze
                     },
                     {
                        'TEXT': 'SETTINGS',
                        'NEXT': 'settingsMenu',
                        'FUNC': None
                     },
                     {
                         'TEXT': 'EXIT',
                         'NEXT': None,
                         'FUNC': self.exitMenu
                     }
                ],
            'settingsMenu':
                [
                    {
                        'TEXT': 'WIDTH',
                        'NEXT': None,
                        'FUNC': self.changeWidth
                     },
                     {
                        'TEXT': 'HEIGHT',
                        'NEXT': None,
                        'FUNC': self.changeHeight
                     },
                     {
                        'TEXT': 'BACK',
                        'NEXT': 'initMenu',
                        'FUNC': None
                     }
                ]       
            }
    
        self.curMenu = 'initMenu'
        self.curIdx = 0

        self.shouldStop = False

        self.mazeDimensions = {'W': 4, 'H': 4}
        
        self.main()

    def initRotateDirections(self):
        tempRotation = math.floor(self.rotation / 90)
        if self.rotation / 90 == 0:
            return

        self.rotateDirection.rotate(tempRotation)


    def main(self):
        self.refreshScreen()
        while self.shouldStop == False:
            sleep(.2)
            for event in sense.stick.get_events():
                if event.action == 'pressed':
                    if event.direction == 'up':
                        self.navMenu(self.rotateDirection[0])
                        break
                    elif event.direction == 'left':
                        self.navMenu(self.rotateDirection[1])
                        break
                    elif event.direction == 'down':
                        self.navMenu(self.rotateDirection[2])
                        break
                    elif event.direction == 'right':
                        self.navMenu(self.rotateDirection[3])
                        break

    def exitMenu(self):
        self.shouldStop = True

    def changeWidth(self):
        self.changeDimension('W')

    def changeHeight(self):
        self.changeDimension('H')

    def changeDimension(self, dim):
        self.showNumber(self.mazeDimensions[dim])
        while True:
            sleep(.2)
            dir = None
            for event in sense.stick.get_events():
                if event.action == 'pressed':
                    if event.direction == 'up':
                        dir = self.rotateDirection[0]
                        break
                    elif event.direction == 'left':
                        dir = self.rotateDirection[1]
                        break
                    elif event.direction == 'down':
                        dir = self.rotateDirection[2]
                        break
                    elif event.direction == 'right':
                        dir = self.rotateDirection[3]
                        break
 
            if dir == 'UP':
                if self.mazeDimensions[dim] < 99:
                    self.mazeDimensions[dim] += 1
                    self.showNumber(self.mazeDimensions[dim])
            elif dir == 'DOWN':
                if self.mazeDimensions[dim] > 4:
                    self.mazeDimensions[dim] -= 1
                    self.showNumber(self.mazeDimensions[dim])
            elif dir == 'LEFT' or dir == 'RIGHT':
                self.refreshScreen()
                return

    def showNumber(self, numb):
        digits0_9 = [
            [2, 9, 11, 17, 19, 25, 27, 33, 35, 42],  # 0
            [2, 9, 10, 18, 26, 34, 41, 42, 43],      # 1
            [2, 9, 11, 19, 26, 33, 41, 42, 43],      # 2
            [1, 2, 11, 18, 27, 35, 41, 42],          # 3
            [3, 10, 11, 17, 19, 25, 26, 27, 35, 43], # 4
            [1, 2, 3, 9, 17, 18, 27, 35, 41, 42],    # 5
            [2, 3, 9, 17, 18, 25, 27, 33, 35, 42],   # 6
            [1, 2, 3, 9, 11, 19, 26, 34, 42],        # 7
            [2, 9, 11, 18, 25, 27, 33, 35, 42],      # 8
            [2, 9, 11, 17, 19, 26, 27, 35, 43]       # 9
        ]
    
        firstDigit = 0
        if numb >= 10:
            firstDigit = int(int(numb / 10) % 10)

        secondDigit = int(numb % 10)
 
        # set pixels for the two digits
        pixels = [(0, 0, 0) for i in range(64)]
        digitGlyph = digits0_9[firstDigit]
        for i in range(0, len(digitGlyph)):
            pixels[digitGlyph[i]] = (255, 255, 255)

        digitGlyph = digits0_9[secondDigit]
        for i in range(0, len(digitGlyph)):
            pixels[digitGlyph[i]+4] = (255, 255, 255)
        
        self.sense.set_pixels(pixels)

    def runMaze(self):
        game = Game(self.mazeDimensions['W'], self.mazeDimensions['H'], self.rotation)
        game.main()

        self.curMenu = 'initMenu'
        self.curIdx = 0

        self.refreshScreen()

    def refreshScreen(self):
        self.sense.clear()
        
        curItem = self.getCurrentMenuItem()

        self.sense.show_message(curItem['TEXT'], .05)

    def getCurrentMenuItem(self):
        return self.MENUS[self.curMenu][self.curIdx % len(self.MENUS[self.curMenu])]

    def navMenu(self, direction):
        if direction == 'UP':
            self.curIdx = self.curIdx - 1
            self.refreshScreen()
            return
        elif direction == 'DOWN':
            self.curIdx = self.curIdx + 1
            self.refreshScreen()
            return
        elif direction == 'RIGHT':
            curItem = self.getCurrentMenuItem()
            if curItem['NEXT'] != None:
                self.curIdx = 0
                self.curMenu = curItem['NEXT']
                self.refreshScreen()
                return
            
            if curItem['FUNC'] != None:
                curItem['FUNC']()
                return

Menu(sense, lowLight=False)
