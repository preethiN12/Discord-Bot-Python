
import random
random.shuffle()
info = {
    "game":"",
    "help":"",
    "maxPlayers":,
    "minPlayers":,
}

#Input: String representing user input.
#playerID: int from 0 to rand int on interval [minPlayers-1, maxPlayers-1]
#players: int array from 0 to the same random value from above
#send: function to send back user input (you can treat it as an alias for the print() function)
#storage: dict holding all the data you want to store. Note that you can change elements, but not reassign. 
#   Ie, storage = {"foo":"bar"} is bad, but storage["foo"] = "bar" is fine

def game(input, playerID, players, send, storage):

    #Player Started Game. This serves to set up the game data obj.
    if input == "":
        #setup storage values.
        return

    #Otherwise, Play the game
    #User won? Return int representing score
    #Still going? Call send("Text to send") to respond to a user.



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
