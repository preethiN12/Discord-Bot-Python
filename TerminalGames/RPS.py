
import random
info = {
    "game":"Rock Paper Scissors",
    "help":"A Game of Rock Paper Scissors",
    "maxPlayers":1,
    "minPlayers":1,
}

def game(input, playerID, players, send, storage):
    moves = ["rock", "paper", "scissors"]
    #Player Started Game. This serves to set up the game data obj.
    if input == "":
        send("Hi, welcome to " + info["game"] + ". ")
        storage["games"] = 0
        storage["ties"] = 0
        storage["userWins"] = 0

        return
    #Otherwise, Play the game
    compMove = moves[random.randint(0,len(moves)-1)]
    if input.lower() in moves:
        send("You Picked " + input + ", and I picked " + compMove + "\n")
        userLower = input.lower()
        if userLower == compMove:
            storage["ties"] += 1
        elif userLower == "scissors" and compMove == "paper":
            storage["userWins"] += 1
        elif userLower == "rock" and compMove == "scissors":
            storage["userWins"] += 1
        elif userLower == "paper" and compMove == "rock":
            storage["userWins"] += 1

        storage["games"] += 1
        send("You have won " + str(storage["userWins"]) + "/" + str(storage["games"]) + ", and tied " + str(storage["ties"])+".")

    elif input.lower() in ["q","quit","exit","c"]:
        
        score = storage["userWins"]
        send("Ending Game.",score)
        return score
    else:
        send("Error, "+ +"you did not pick a valid move. You valid moves are: " + ", ".join(moves))
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
