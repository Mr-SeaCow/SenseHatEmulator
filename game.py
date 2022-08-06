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

    def isValid(self, BOUNDS):
        if BOUNDS == None:
            BOUNDS = Coordinates(6, 6)
        return self.x >= 0 and self.x <= BOUNDS.x and self.y >= 0 and self.y <= BOUNDS.y

    def move(self, moveDirection):
        tempCoords = Coordinates(self.x + moveDirection.x, self.y + moveDirection.y)
        if tempCoords.isValid(Coordinates(6, 6)):
            self.setCoords(tempCoords)

    def getNextCoords(self, moveDirection):
        return Coordinates(self.x + moveDirection.x, self.y + moveDirection.y)

    def isEqual(self, coords):
        return self.x == coords.x and self.y == coords.y
    
    def generateRandomCoords(self):
        return Coordinates(randrange(0, 6), randrange(0, 6))

    def setCoords(self, coords):
        self.x = coords.x
        self.y = coords.y

    #Shift accounts for border
    def convertToUnaryCoords(self, shift=1):
        unaryCoord = (self.x + shift)
        unaryCoord += (self.y + shift) * 8
        return unaryCoord

class Entity(Coordinates):
    def __init__(self, entityType, color, x=-1, y=-1):
        super().__init__(x, y)
        self.entityType = entityType # Player, Fruit, Enemy
        self.color = color

    @property
    def hasInitialized(self):
        return self.x != -1 and self.y != -1

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

class Game:
    def __init__(self, pointLimit=14, timeBetweenFruit=None, borderColor=lg):

        self.player = Entity('Player', r, 4, 4)
        self.fruit = Entity('Fruit', b, 3, 3)
        
        self.enemyList = []

        self.playerPoints = 0
        self.pointLimit = pointLimit

        self.board = []
        self.borderColor = borderColor

        self.hasFinished = False
       
        self.resetBoard()
        self.main()

    def main(self):
        self.updateScreen()
        while self.hasFinished == False:
            hasMoved = False
            for event in sense.stick.get_events():
                if event.action == 'pressed':
                    if event.direction == 'up':
                        self.player.move(Coordinates(0, -1))
                        hasMoved = True
                        break
                    elif event.direction == 'left':
                        self.player.move(Coordinates(-1, 0))
                        hasMoved = True
                        break
                    elif event.direction == 'down':
                        self.player.move(Coordinates(0, 1))
                        hasMoved = True
                        break
                    elif event.direction == 'right':
                        self.player.move(Coordinates(1, 0))
                        hasMoved = True
                        break
            
            if hasMoved == False:
                time.sleep(0.05)
                continue

            if self.player.hasCollided(self.enemyList):
                return self.playLoseScreen()

            if self.player.hasCollided([self.fruit]):

                self.playerPoints += 1

                if self.playerPoints >= self.pointLimit:
                    return self.playWinScreen()

                tempList = [self.player]
                self.fruit.pickRandomLocation(tempList)

                tempList.append(self.fruit)

                if self.shouldAddEnemy():
                    self.addEnemy()

                for enemy in self.enemyList:
                    enemy.pickRandomLocation(tempList)
                    tempList.append(enemy)

            self.updateScreen()
            
    def playLoseScreen(self):
        sense.clear()
        #sense.show_message("Game Over", 0.07, text_colour= c, back_colour = r)

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

       # sense.show_message("Winner!", 0.075, text_colour = (255,100,0), back_colour= g)

    def resetBoard(self):
        self.board = []
        for i in range(64):
            if i < 8 or i >= 56:
                self.board.append(self.borderColor)
            elif i % 8 == 0 or i % 8 == 7:
                self.board.append(self.borderColor)
            else:
                self.board.append((0, 0, 0))

    def shouldAddEnemy(self):
        return (7 + (len(self.enemyList) * 7)) <= self.playerPoints

    def addEnemy(self):
        self.enemyList.append(Entity('Enemy', m))

    def placeEntity(self, entity):
        idx = entity.convertToUnaryCoords()
        self.board[idx] = entity.color

    def updateScreen(self):
        self.resetBoard()

        self.placeEntity(self.player)
        self.placeEntity(self.fruit)

        for enemy in self.enemyList:
            self.placeEntity(enemy)

        sense.set_pixels(self.board)

Game()