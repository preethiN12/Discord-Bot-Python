
import random
info = {
    "game":"Battleship",
    "help":"A Game of Battleship",
    "maxPlayers":2,
    "minPlayers":1,
}
gui = {
    "blue square": "b",
    "blank": "B",
    "hit": ":orange_square:",
    "destroyed": "H",
    "miss": "M",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "A": "A",
    "B": "B",
    "C": "C",
    "D": "D",
    "E": "E"
}
# gui = {
#     "ocean": ":ocean:",
#     "blue square": ":blue_square:",
#     "blank": ":black_square:",
#     "hit": ":orange_square:",
#     "destroyed": ":red_square:",
#     "miss": ":radio_button:",
#     "1": ":one:",
#     "2": ":two:",
#     "3": ":three:",
#     "4": ":four:",
#     "5": ":five:",
#     "A": ":regional_indicator_a:",
#     "B": ":regional_indicator_b:",
#     "C": ":regional_indicator_c:",
#     "D": ":regional_indicator_d:",
#     "E": ":regional_indicator_e:"
# }
labels = 1
yLabels = [gui["A"], gui["B"], gui["C"], gui["D"], gui["E"]]
yCoords = ["A", "B", "C", "D", "E"]
playerOneWin = False
playerTwoWin = False

#Input: String representing user input.
#playerID: int from 0 to rand int on interval [minPlayers-1, maxPlayers-1]
#players: int array from 0 to the same random value from above
#send: function to send back user input (you can treat it as an alias for the print() function)
#storage: dict holding all the data you want to store. Note that you can change elements, but not reassign. 
#   Ie, storage = {"foo":"bar"} is bad, but storage["foo"] = "bar" is fine

def game(input, playerID, players, send, storage):
    global gridOne
    global gridTwo
    global playerOneWin
    global playerTwoWin

    #Player Started Game. This serves to set up the game data obj.
    if input == "":
        #setup storage values.
        send("Hi, welcome to " + info["game"] + ". \n")

        DisplayGrid(send) #EDITED

        return

    # Otherwise, Play the game
    if not playerOneWin and not playerTwoWin:

        # Process coordinates
        coords = input.split(",")
        x = int(coords[0])
        y = ValidLetter(coords[1], False)

        # Player 1
        if playerID == 0:
            # Check if it hit a ship
            if gridTwo[y+labels][x] != gui["blue square"]:
                # Destroy the ship
                gridTwo = DestroyShip(gridTwo, gridTwo[y+labels][x])

                # Check if all the ships have been destroyed
                if GameOver(gridTwo):
                    playerOneWin = True
            else:
                # Miss
                gridTwo[y+labels][x] = gui["miss"]

        # Player 2
        elif playerID == 1:
            # Check if it hit a ship
            if gridOne[y+labels][x] != gui["blue square"]:
                # Destroy the ship
                gridOne = DestroyShip(gridOne, gridOne[y+labels][x])

                # Check if all the ships have been destroyed
                if GameOver(gridOne):
                    playerTwoWin = True
            else:
                # Miss
                gridOne[y+labels][x] = gui["miss"]

        # Check if a bot is needed
        if len(players) < 2:
            # Generate a random position to shoot at
            x = random.randint(1, gridSize)
            y = random.randint(1, gridSize)

            # Prevents it from generating already hit/destroyed/miss positions
            while gridOne[y][x] != gui["blue square"]:
                x = random.randint(1, gridSize)
                y = random.randint(1, gridSize)

            # Check if it hit a ship
            if gridOne[y][x] != gui["blue square"]:
                # Destroy the ship
                gridOne = DestroyShip(gridOne, gridOne[y][x])

                # Check if all the ships have been destroyed
                if GameOver(gridOne):
                    playerTwoWin = True
            else:
                # Miss
                gridOne[y][x] = gui["miss"]

        DisplayGrid(send)

        if playerOneWin:
            send("GAME OVER! PLAYER 1 WINS")
        elif playerTwoWin:
            send("GAME OVER! PLAYER 2 WINS")

    #User won? Return int representing score
    #Still going? Call send("Text to send") to respond to a user.
    else:
        send("GAME IS OVER")

        playerOneID = 0 #TEMP
        playerTwoID = 1 #TEMP

        # Player 1 Wins
        if playerOneWin:
            return {playerOneID: 1, playerTwoID: 0}
        elif playerTwoWin:
            return {playerOneID: 0, playerTwoID: 1}
        else:
            return {playerOneID: 0}

def CreateGrid(size):
    rows, cols = (size+labels, size+labels)

    # Create a grid
    grid = [[gui["blue square"] for i in range(cols)] for j in range(rows)]

    # Place x and y labels
    grid[0][0] = gui["blank"]
    # Loops through the grid to place the labels
    for rows in range(len(grid)):
        for cols in range(len(grid)):
            # X labels
            if rows == 0 and cols > 0:
                grid[rows][cols] = gui[str(cols)]

            # Y labels
            if cols == 0 and rows > 0:
                grid[rows][cols] = yLabels[rows-1]

    # Spawn Ships
    grid = SpawnShips(grid)

    # Return the grid
    return grid

def SpawnShips(grid):
    gridSize = len(grid) - labels

    # Determine the type and quantity of ships to spawn based on the size of the grid
    if gridSize == 5:
        grid = CreateShip(grid, "*", 1)
        grid = CreateShip(grid, "&", 2)
        grid = CreateShip(grid, "%", 3)
    else:
        grid = CreateShip(grid, "*", 1)
        grid = CreateShip(grid, "&", 2)
        grid = CreateShip(grid, "%", 3)

    # Return the now ship filled grid
    return grid

def CreateShip(grid, shipID, shipLength):
    direction = -1
    gridSize = len(grid) - labels

    # Generate a random position to create a ship
    x = random.randint(0, gridSize)
    y = random.randint(0, gridSize)

    # Look for a valid spot to create a ship
    try:
        # Continues to generate random positions until it finds one with a valid direction to create a ship
        while direction == -1:
            # Continues to generate random positions until it lands on an empty space
            while grid[y+labels][x+labels] != gui["blue square"]:
                # Generate another random position to create a ship
                x = random.randint(0, gridSize)
                y = random.randint(0, gridSize)

            # Checks if there is a valid direction to spawn a ship, if so it will return the index of that direction
            # Else it returns -1, signifying there were no directions to create a ship
            direction = Direction(grid, x, y, shipLength)
    except:
        CreateShip(grid, shipID, shipLength)

    # Spawn ship in based on the index of the valid direction
    for i in range(shipLength):
        if direction == 0:      # East
            grid[y+labels][(x+labels)+i] = shipID
        elif direction == 1:    # North
            grid[(y+labels)-i][x+labels] = shipID
        elif direction == 2:    # West
            grid[y+labels][(x+labels)-i] = shipID
        elif direction == 3:    # South
            grid[(y+labels)+i][x+labels] = shipID

    # Return the grid with the newly spawned ship into it
    return grid

def Direction(grid, x, y, shipLength):
    directions = [False, False, False, False]
    _x, _y = (0, 0)

    # Checks if there is space to create the ship in any of the given directions
    for dir in range(len(directions)):
        # Loops through the amount of space needed to create the ship
        for pos in range(shipLength):
            # Update the next position to verify based on the direction
            if dir == 0:      # East
                _x = x + pos
            elif dir == 1:    # North
                _y = y - pos
            elif dir == 2:    # West
                _x = x - pos
            elif dir == 3:    # South
                _y = y + pos

            # In case it checks out of range of the array
            try:
                # North/South
                if dir == 1 or dir == 3:
                    # Checks if all the spaces are empty
                    if grid[_y+labels][x+labels] == gui["blue square"]:
                        directions[dir] = True
                    # If there is even one space that is not empty, the entire direction is invalid
                    else:
                        directions[dir] = False
                        break
                # East/West
                elif dir == 0 or dir == 2:
                    # Checks if all the spaces are empty
                    if grid[y+labels][_x+labels] == gui["blue square"]:
                        directions[dir] = True
                    # If there is even one space that is not empty, the entire direction is invalid
                    else:
                        directions[dir] = False
                        break
            except:
                # Since it goes out of range, the direction is invalid
                directions[dir] = False

    # Check if any directions are valid
    direction = -1
    # Loops through all the directions and checks if any are valid
    for dir in range(len(directions)):
        # If there is a valid direction, the direction variable will equal to the index of said direction
        if directions[dir]:
            direction = dir
            break

    # Return a valid direction OR -1 if there are no valid directions
    return direction

def DestroyShip(grid, shipID):
    # Loop through the grid
    # Loops through each row
    for row in range(len(grid)-labels):
        # Loops through each column
        for col in range(len(grid)-labels):
            # Look for the ship's unique ID, and if it matches destroy that portion of the ship
            if grid[row+labels][col+labels] == shipID:
                grid[row+labels][col+labels] = gui["destroyed"]

    # Returns the grid with the newly destroyed ship
    return grid

def ValidLetter(letter, verify):
    # Loop through the yCoord array based on the size of the grid
    for i in range(gridSize):
        # Check if the letter is in the domain of alphabets displayed on the y labels
        if letter.upper() == yCoords[i]:
            # Check if its being used to verify the letter or to return the index of the letter
            if verify:
                return True
            else:
                return i

    # Check if its being used to verify the letter
    if verify:
        return False
    else:
        return

def DisplayGrid(send):
    # Display variable to hold all the string that needs to be displayed
    space = "\t\t\t\t\t\t"
    display = "Player 1:" + space + "Player 2:\n"

    # Loop through each row of the grids
    for row in range(gridSize+labels):
        # Loop through grid one's columns first
        for col in range(gridSize+labels):
            display += gridOne[row][col] + "\t"

        # Create space between the two grids
        display += "\t\t"

        # Loop through grid two's columns last
        for col in range(gridSize+labels):
            display += gridTwo[row][col] + "\t"

        # Next row
        display += "\n"

    # Space for other info
    display += "\n"

    # Display the string in the display variable
    send(display)
    return

def GameOver(grid):
    gameOver = True
    for row in range(len(grid)-labels):
        for col in range(len(grid)-labels):
            if grid[col+labels][row+labels] != gui["blue square"] and grid[col+labels][row+labels] != gui["destroyed"] and grid[col+labels][row+labels] != gui["miss"]:
                gameOver = False

    if gameOver:
        return True
    else:
        return False

if __name__=="__main__":
    gameStorage = {}
    userIn = ""
    curUser = None
    players = random.randint(info["minPlayers"],info["maxPlayers"])

    # Create Grids #EDITED
    gridSize = 5 #EDITED
    gridOne = CreateGrid(gridSize) #EDITED
    gridTwo = CreateGrid(gridSize) #EDITED

    while True:
        resp = game(userIn, curUser, list(range(players)), print, gameStorage)
        if resp != None:
            print("Game Finished! You Finished " + info["game"] + " with a score of " + str(resp))
            break
        while True:
            user = input("(Which Player do you want to make this response as?)")
            if 0<=int(user)<players:
                curUser = int(user)
                break
            else:
                print("Player ID must be between 0 and ", + players-1)

        userIn = input("Enter X and Y in this format: Numerical,Alphabetical >") #EDITED
