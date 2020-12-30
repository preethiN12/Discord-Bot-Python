import random
info = {
    "game":"Connect Four",
    "help":"A Game of Connect Four",
    "maxPlayers":2,
    "minPlayers":1,
}
def printBoard(board, send):
    for i in range(len(board)):
        for j in range(len(board)):
            send("|" + board[i][j], end ="")
        send("|")

def checkWins(board, char):
    
    for col in range(6):
        for row in range(3):
            if board[row][col] == char and board[row+1][col] == char and board[row+2][col] == char and board[row+3][col] == char:
                return True
                
    for row in range(6):
        for col in range(3):
            if board[row][col] == char and board[row][col+1] == char and board[row][col+2] == char and board[row][col+3] == char:
                return True
    
    for row in range(3):
        for col in range(3,6):
            if board[row][col] == char and board[row+1][col-1] == char and board[row+2][col-2] == char and board[row+3][col-3] == char:
                return True
    
    for row in range(3):
        for col in range(3):
            if board[row][col] == char and board[row+1][col+1] == char and board[row+2][col+2] == char and board[row+3][col+3] == char:
                return True

def game(input, playerID, players, send, storage):
    moves = ["0", "1", "2", "3", "4", "5"]
    #Player Started Game. This serves to set up the game data obj.
    if input == "":
        send("Hi, welcome to " + info["game"] + ". ")
        
        board = [["-","-","-","-","-","-","-"],["-","-","-","-","-","-","-"], ["-","-","-","-","-","-","-"], ["-","-","-","-","-","-","-"], ["-","-","-","-","-","-","-"], ["-","-","-","-","-","-","-"]]
        printBoard(board, send)
        
        storage["board"] = board
        storage["games"] = 0
        storage["ties"] = 0
        storage["userWins"] = 0

        return
        
    board = storage["board"]
    #Otherwise, Play the game
    compMove = moves[random.randint(0,len(moves)-1)]
    if input in moves:
        send("You Picked " + input + ", and I picked " + compMove + "\n")
        
        #change the column value to an integer
        userCol = int(input)
        compCol = int(compMove)
        userMove = (0,0)
        compMove = (0,0)
        
        #place the users token in the appropriate column in an empty row, starting from the bottom up
        for i in range(len(moves)-1,-1,-1):  
            if board[i][userCol] == "-":
                board[i][userCol] = "x"
                userMove = [i, userCol]
                break                
        for i in range(len(moves)-1,-1,-1):  
            if board[i][compCol] == "-":
                board[i][compCol] = "o"
                compMove = [i, userCol]
                break
                
        if checkWins(board, "x"):
            send("User Wins")
            return
        if checkWins(board, "o"):
            send("Computer Wins")
            return
        printBoard(board, send)   

    elif input.lower() in ["q","quit","exit","c"]:
        
        score = storage["userWins"]
        send("Ending Game.",score)
        return score
    else:
        send("Error, you did not pick a valid move. You valid moves are: " + ", ".join(moves))
    return


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
            user = input("(Which Player do you want to make this response as?)")
            if 0<=int(user)<players:
                curUser = int(user)
                break
            else:
                print("Player ID must be between 0 and ", + players-1)

        userIn = input(">")