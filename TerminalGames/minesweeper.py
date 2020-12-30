
import random
from random import randint as r
info = {
    "game":"minesweeper",
    "help":"https://www.instructables.com/How-to-play-minesweeper/",
    "maxPlayers":1,
    "minPlayers":1,
}

#Game runtime constants
#----start----#
BOARD_SIZE = 16
MINES = 10
DIVIDER = "  "+("+---"*16)+"+"
X_AXIS = "  "+"".join(["  "+chr(65+i)+" " for i in range(16)])
FINE = 0
MINE = 1
FLAGGED = 2
REVEALED = 3
FLAGS_EMPTY = 4
SAPPER = 0
FLAGGER = 1
TOOLS = ["Sapper","Flagger"]
#----end----#

#-----Object definitions start-----#
#An object which will hold the attributes of a spot on the board
class boardSpot:
    def __init__(self):
        self.revealed = False
        self.flagged = False
        self.nearby = 0

#An object which will hold the player's minefield as well as the class
#methods used to interact with the board
class Board:
    #generates the board and sets the game's playerID (temporary)
    def __init__(self):
        self.flags = MINES
        self.board = [[boardSpot() for i in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
        self.spotsLeft = (BOARD_SIZE**2)-MINES
        self.generated = False
        self.tool = 0

    def switchTool(self):
        self.tool = not self.tool

    def generateBoard(self, firstX, firstY):
        temp = 0
        #sets the mines randomly, making sure that one doesn't get put on the
        #first coordinate that the player chooses
        while temp < MINES:
            x,y = r(0,BOARD_SIZE-1), r(0,BOARD_SIZE-1)
            if firstX == x and firstY == y:
                continue
            if self.board[y][x].nearby != -1:
                self.board[y][x].nearby = -1
                self.actOnNeighbors(x, y, self.incrementSpot)
                temp += 1
        self.reveal(firstX, firstY)
        self.generated = True

    #increments the nearby attribute of a spot on the board by 1
    def incrementSpot(self, x, y):
        spot = self.board[y][x]
        if spot.nearby != -1:
            spot.nearby += 1

    #performs a given function on all the direct neighbors of a certain spot
    def actOnNeighbors(self, x, y, func):
        for i in range(-1,2):
            for j in range(-1,2):
                if i== 0 and j == 0:
                    continue
                elif -1 < y + i and y + i < BOARD_SIZE and -1 < x + j and x + j < BOARD_SIZE:
                    #the general format for whatever function used here should be f(x,y)
                    func(x+j, y+i)

    def reveal(self, x, y):
        spot = self.board[y][x]
        if spot.flagged:
            return FLAGGED
        elif spot.revealed:
            return REVEALED
        elif spot.nearby > -1:
            self.spotsLeft -= 1
            spot.revealed = True
            if spot.nearby == 0:
                self.actOnNeighbors(x,y,self.reveal)
            return FINE
        else:
            return MINE

    def flag(self,x,y):
        spot = self.board[y][x]
        if self.flags == 0:
            return FLAGS_EMPTY
        elif spot.revealed:
            return REVEALED
        else:
            #increases or decreases the flags available depending on the spot's status
            self.flags += (1 if spot.flagged else -1)
            #sets the spot to the opposite of what it was
            spot.flagged = not spot.flagged
            return FINE

    def makeMove(self,x,y):
        if self.tool == SAPPER:
            return self.reveal(x,y)
        else:
            return self.flag(x,y)
    
    def showBoard(self, prnt, debug=False):
        prnt(X_AXIS)
        prnt(DIVIDER)
        i = 0
        for row in self.board:
            if i < 10:
                print(' ',end = '')
            prnt(f"{i}|", end=' ')
            for item in row:
                char = ''
                if item.flagged:
                    #If debug mode is active, incorrectly placed flags will be displayed as a lowercase f
                    if debug and item.nearby > -1:
                        char = 'f'
                    #Otherwise, all flags should be shown as an uppercase F regardless of their actual value
                    else:
                        char = 'F'
                elif item.revealed:
                    char = str(item.nearby) if item.nearby > 0 else ' '
                elif debug:
                    if item.nearby < 0:
                        char = 'M'
                    else:
                        char = str(item.nearby) if item.nearby > 0 else ' '
                else:
                    char = '~'
                prnt(char , end=' | ')
            i+=1
            prnt('\n'+DIVIDER)
        prnt(f"\nFlags: {self.flags}")
        prnt(f"Current Tool: {TOOLS[self.tool]}")

#-----Object definitions end-----#

#Input: String representing user input.
#playerID: int from 0 to rand int on interval [minPlayers-1, maxPlayers-1]
#players: int array from 0 to the same random value from above
#send: function to send back user input (you can treat it as an alias for the print() function)
#storage: dict holding all the data you want to store. Note that you can change elements, but not reassign. 
#   Ie, storage = {"foo":"bar"} is bad, but storage["foo"] = "bar" is fine

def game(input, playerID, players, send, storage):

    #Player Started Game. This serves to set up the game data obj.
    if input == "":
        storage["game"] = Board()
        storage["game"].showBoard(send)
        #setup storage values.
        return
    
    arguments = input.split(" ")
    if arguments[0].lower() == "tool" and storage["game"].generated:
        storage["game"].switchTool()
    elif len(arguments) >= 2:
        try:
            x = ord(arguments[0].upper())-65
            y = int(arguments[1])
        except:
            send("Please enter coordinates in format of \"[int] [char]\"")
            return
        
        if -1 < x < BOARD_SIZE and -1 < y < BOARD_SIZE:
            if storage["game"].generated:
                result = storage["game"].makeMove(x,y)
            else:
                storage["game"].generateBoard(x,y)
                result = FINE
            code = None

            if result == FINE:
                if storage["game"].spotsLeft == 0:
                    code = 0
            
            elif result == MINE:
                code = 1

            elif result == FLAGGED:
                send("That spot is flagged.")
                return
            
            elif result == FLAGS_EMPTY:
                send("You have no more flags left to place.")
                return

            elif result == REVEALED:
                send("That spot has already been revealed.")
                return
            storage["game"].showBoard(send,code)
            return code
        
        else:
            send("Please enter valid coordinates.")
            return

        
    storage["game"].showBoard(send)

    #Otherwise, Play the game
    #User won? Return int representing score
    #Still going? Call send("Text to send") to respond to a user.

#-----Personal Debugging Section Start-----#

"""
test = Board()
test.generateBoard(7,7)
test.showBoard(print,1)

print()
test.showBoard(print)
while True:
    x,y = getInput()
    if not test.tool:
        result = test.reveal(x,y)
        if result == MINE:
            test.showBoard(print,1)
            break
    else:
        print(test.flag(x,y))
    test.showBoard(print)
"""
#-----Personal Debugging Section End-----#

if __name__=="__main__":
    gameStorage = {}
    userIn = ""
    curUser = None
    players = random.randint(info["minPlayers"],info["maxPlayers"])
    while True:
        resp = game(userIn, curUser, list(range(players)), print, gameStorage)
        if resp != None:
            print("Game Finished! You Finished " + info["game"] + " with a score of " + str(resp))
            break
        while True:
            user = 0 #input("(Which Player do you want to make this response as?)")
            if 0<=int(user)<players:
                curUser = int(user)
                break
            else:
                print("Player ID must be between 0 and ", + players-1)

        userIn = input(">")