from sense_emu import SenseHat
from random import randrange
import time

sense = SenseHat()
sense.clear()

r = (255,0,0)
g = (0,255,0)
b = (0,0,255)
y = (255,255,0)
c = (0,255,255)
m = (255,0,255)
w = (255,255,255)
e = (0,0,0)
lg = (0,60,0)


winAnim0 = [
    g,g,g,g,g,g,g,g,
    g,e,e,e,e,e,e,g,
    g,e,e,e,e,e,e,g,
    g,e,e,e,e,e,e,g,
    g,e,e,e,e,e,e,g,
    g,e,e,e,e,e,e,g,
    g,e,e,e,e,e,e,g,
    g,g,g,g,g,g,g,g
    ]

winAnim1 = [
    g,g,g,g,g,g,g,g,
    g,c,c,c,c,c,c,g,
    g,c,e,e,e,e,c,g,
    g,c,e,e,e,e,c,g,
    g,c,e,e,e,e,c,g,
    g,c,e,e,e,e,c,g,
    g,c,c,c,c,c,c,g,
    g,g,g,g,g,g,g,g
    ]

winAnim2 = [
    g,g,g,g,g,g,g,g,
    g,c,c,c,c,c,c,g,
    g,c,b,b,b,b,c,g,
    g,c,b,e,e,b,c,g,
    g,c,b,e,e,b,c,g,
    g,c,b,b,b,b,c,g,
    g,c,c,c,c,c,c,g,
    g,g,g,g,g,g,g,g
    ]

winAnim3 = [
    g,g,g,g,g,g,g,g,
    g,c,c,c,c,c,c,g,
    g,c,b,b,b,b,c,g,
    g,c,b,m,m,b,c,g,
    g,c,b,m,m,b,c,g,
    g,c,b,b,b,b,c,g,
    g,c,c,c,c,c,c,g,
    g,g,g,g,g,g,g,g
    ]

winAnimAra = [None, winAnim0, None, winAnim0, None, winAnim0, winAnim1, winAnim2, winAnim3]

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isValid(self, BOUNDS=None):
        if BOUNDS == None:
            BOUNDS = Coordinates(7, 7)
        return self.x >= 0 and self.x <= BOUNDS.x and self.y >= 0 and self.y <= BOUNDS.y

    def move(self, moveDirection):
        tempCoords = Coordinates(self.x + moveDirection.x, self.y + moveDirection.y)
        if tempCoords.isValid(Coordinates(7, 7)):
            self.setCoords(tempCoords)

    def getNextCoords(self, moveDirection):

        nextMoveX = self.x + moveDirection.x
        nextMoveY = self.y + moveDirection.y

        nextMoveX = self.swapSides(nextMoveX)
        nextMoveY = self.swapSides(nextMoveY)

        return Coordinates(nextMoveX, nextMoveY)

    def swapSides(self, coord):
        if coord <= -1:
            return 7
        elif coord >= 8:
            return 0
        else:
            return coord

    def isEqual(self, coords):
        return self.x == coords.x and self.y == coords.y
    
    def generateRandomCoords(self):
        return Coordinates(randrange(0, 6), randrange(0, 6))

    def setCoords(self, coords):
        self.x = coords.x
        self.y = coords.y

    def copyCoords(self):
        return Coordinates(self.x, self.y)

    #Shift accounts for border
    def convertToUnaryCoords(self, shift=1):
        unaryCoord = (self.x + shift)
        unaryCoord += (self.y + shift) * 8
        return unaryCoord
 
DIR_ARRAY = [Coordinates(0, -1), Coordinates(-1, 0), Coordinates(0, 1), Coordinates(1, 0)]

class Entity(Coordinates):
    def __init__(self, entityType, color, x=-1, y=-1):
        super().__init__(x, y)
        self.entityType = entityType # Player, Fruit, Enemy
        self.color = color

    def pickRandomLocation(self, entityLocations):
        randomCoords = self.generateRandomCoords()
        if self.validateRandomLocation(randomCoords, entityLocations):
            return self.setCoords(randomCoords)

        self.pickRandomLocation(entityLocations)
            
    def validateRandomLocation(self, randomCoords, entityLocations):       
        for entity in entityLocations:
            if randomCoords.isEqual(entity):
                return False
        return True
       
    def hasCollided(self, entityLocations):
        for entity in entityLocations:
            if self.isEqual(entity):
                return True
        return False

    def copyEntity(self):
        return Entity(self.entityType, self.color, self.x, self.y)


    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Snake(Entity):
    def __init__(self, entityType, color, x=-1, y=-1):
        super().__init__(entityType, color, x, y)
        
        self.body = [Entity('PlayerBody', color, x, y)]
        self.color = color
        self._iterIdx = -1
        
        self.moveDirection = 0

    def __iter__(self):
        self._iterIdx = -1
        return self

    def __next__(self):
        if self._iterIdx < len(self.body) - 1:
            self._iterIdx += 1
            return self.body[self._iterIdx]
        else:
            raise StopIteration

    def moveSnake(self, fruit=Coordinates(-1, -1)):

        moveDirection = DIR_ARRAY[self.moveDirection]
        nextCoords = self.body[0].getNextCoords(moveDirection)
        lastLink = self.body.pop()
        didCollectFruit = False

        if nextCoords.isEqual(fruit):
            self.body.append(lastLink)
            didCollectFruit = True

        newLink = Entity('PlayerBody', self.color, nextCoords.x, nextCoords.y)

        print(newLink)
        self.body.insert(0, newLink)

        return didCollectFruit

    def swapDirection(self):
        self.moveDirection = (self.moveDirection + 2) % 4

    def hasCollectedFruit(self, fruit):
        if fruit.hasCollided(self.body):
            return True
        return False

    def hasLost(self):
        frontLink = self.body.pop(0)
        if frontLink.hasCollided(self.body) or frontLink.isValid() == False:
            return True
        self.body.insert(0, frontLink)
        return False

    def hasWon(self):
        return len(self.body) == 64

class Game:
    def __init__(self, frameTime=0.25):

        self.player = Snake('Player', g, 4, 4)
        self.fruit = Entity('Fruit', r, 3, 3)
    

        self.frameTime = frameTime
        self.board = []
        self.hasFinished = False
       
        self.resetBoard()
        self.main()

    def main(self):
        self.updateScreen()
        while self.hasFinished == False:
            moveDir = self.player.moveDirection
            for event in sense.stick.get_events():
                if event.action == 'pressed':
                    if event.direction == 'up':
                        moveDir = 0
                        break
                    elif event.direction == 'left':
                        moveDir = 1
                        break
                    elif event.direction == 'down':
                        moveDir = 2
                        break
                    elif event.direction == 'right':
                        moveDir = 3
                        break
            
            self.player.moveDirection = moveDir
            time.sleep(self.frameTime)

            if self.player.moveSnake(self.fruit):
                self.fruit.pickRandomLocation(self.player)

            if self.player.hasWon():
               return self.playWinScreen()
        
            if self.player.hasLost():
               return self.playLoseScreen()


            self.updateScreen()
            
    def playLoseScreen(self):
        sense.clear()
        sense.show_message("Game Over", 0.07, text_colour= c, back_colour = r)

    def playWinScreen(self):
        sense.clear()
        sense.set_pixels(winAnim0)
        time.sleep(1)
        for x in winAnimAra:
            if x == None:
                sense.clear()
            else:
                sense.set_pixels(x)
            time.sleep(.3)

        sense.show_message("Winner!", 0.075, text_colour = (255,100,0), back_colour= g)

    def resetBoard(self):
        self.board = []
        for _ in range(64):
            self.board.append((0, 0, 0))

    def placeEntity(self, entity):
        idx = entity.convertToUnaryCoords(0)
        self.board[idx] = entity.color

    def updateScreen(self):
        self.resetBoard()

        for entity in self.player:
            self.placeEntity(entity)
            
        self.placeEntity(self.fruit)

        sense.set_pixels(self.board)

Game()