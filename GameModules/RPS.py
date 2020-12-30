
import random

game = "Rock Paper Scissors"
help = "A Game of Rock Paper Scissors"
maxPlayers = 1
minPlayers = 1

#If a user is playing a game with DM responses and tries to play another game with DM responses, we should not let them
dmResponses = True


async def init(playerID, players, dm, send, storage):
    await send("Hi, welcome to " + game + ". ")
    await dm("Hi! Thanks for starting a game")
    storage["games"] = 0
    storage["ties"] = 0
    storage["userWins"] = 0

async def reaction(reaction, message, playerID, players, dm, send, fromDms,storage):
    if fromDms:
        await dm("nice emoji! " + reaction.emoji)
    else:
        await send("nice reaction! " + reaction.emoji)
    return None

async def message(messageBody, playerID, players, dm, send, storage):
    moves = ["rock", "paper", "scissors"]

    #Otherwise, Play the game
    compMove = moves[random.randint(0,len(moves)-1)]
    if messageBody.lower() in moves:
        await send("You Picked " + messageBody + ", and I picked " + compMove + "\n")
        userLower = messageBody.lower()
        if userLower == compMove:
            storage["ties"] += 1
        elif userLower == "scissors" and compMove == "paper":
            storage["userWins"] += 1
        elif userLower == "rock" and compMove == "scissors":
            storage["userWins"] += 1
        elif userLower == "paper" and compMove == "rock":
            storage["userWins"] += 1

        storage["games"] += 1
        await send("You have won " + str(storage["userWins"]) + "/" + str(storage["games"]) + ", and tied " + str(storage["ties"])+".")

    elif messageBody.lower() in ["q","quit","exit","c"]:
        
        score = storage["userWins"]
        await send("Ending Game. " + str(score))
        return {playerID: storage["userWins"]}
    else:
        await send("Error, "+ +"you did not pick a valid move. You valid moves are: " + ", ".join(moves))
        return


async def dm(messageBody, playerID, players, dm, send, storage):
    await dm("Got your dm. Replying to Channel though.")
    return await message(messageBody, playerID,players, dm, send, storage)


