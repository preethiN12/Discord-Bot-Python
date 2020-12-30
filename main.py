import discord,os,sys,database,importlib.util, datetime
from os.path import dirname, join, abspath
BOT_TOKEN = ""
BOT_CHANNEL = ""
COMMAND_PREFIX = "$"
GAME_FOLDER = "GameModules"

#finds the length of the command prefix to allow for prefixes longer than 1 character
prefix_length = len(COMMAND_PREFIX)

# commands.Bot is an sub class of discord.client that allows commands to be used
bot = discord.Client()

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

games = {}

for file in os.listdir(GAME_FOLDER):
	try:
		filePath = abspath(join(dirname(__file__), GAME_FOLDER, file))
		moduleName = file.split(".")[0]
		mod = module_from_file(moduleName, filePath)
		print ("Adding Module ", moduleName, mod.game)
		games[moduleName.lower()] = mod
	except Exception as e:
		#pass
		print(e)

try:
	BOT_TOKEN = os.environ["BOT_TOKEN"]
	BOT_CHANNEL = os.environ["BOT_CHAN"]
except KeyError:
	try:
		import auth
		BOT_TOKEN = auth.BOT_TOKEN
		BOT_CHANNEL = auth.BOT_CHAN
	except Exception as e:
		print("Ensure you have set your variables. Ie, run as BOT_TOKEN=foo BOT_CHAN=bar python3 main.py",e)
		sys.exit(1)

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
database.openDb()

@bot.event
async def on_message(message):
	isChat = isinstance(message.channel, discord.channel.TextChannel)

	print ("Message body: " + message.content)
	# Allow responses only to a certain channel
	if (str(message.channel.id) != BOT_CHANNEL and BOT_CHANNEL != "all") and isChat:
		return
	# Checks the beginning characters (depending on length of profix) of the message content and checks if it is the same as the prefix, then resends everything after the prefix
	if not message.content[:prefix_length] == COMMAND_PREFIX:
		return
	msg = message.content[prefix_length:]
	msgLower = msg.lower()
	author = bot.get_user(message.author.id)
	dm = author.send
	if msgLower.startswith(COMMAND_PREFIX +"scores"):
		await message.channel.send("Your score is " + str(database.getPlayerScoreSummary(message.author.id)))
	elif msgLower.startswith(COMMAND_PREFIX+"ping"):
		now = datetime.datetime.now()
		time_sent = message.created_at
		diff = now-time_sent
		await message.channel.send("Milliseconds since sent is: " + str(round(diff.microseconds/1000,2)))
		await message.channel.send("Client reports " + str(round(bot.latency*1000,2)) + "ms of latency")

	elif msgLower.startswith(COMMAND_PREFIX +"list"):
		await message.channel.send("All the games installed are: " + ",".join(games.keys()))
	elif msgLower.startswith(COMMAND_PREFIX +"new"):
		if not isChat:
			await message.channel.send("You cannot start a game from dms yet")
			return
		gameStr = msgLower[4:]
		gameName = gameStr.strip().split(" ")[0]
		print("Game string", gameStr, )
		users = set([x.id for x in message.mentions])
		users.add(message.author.id)
		print ("Starting Game: ",gameName, users)
		
		#Check that game is installed
		if gameName not in games:
			await message.channel.send ("Cannot find that game.")
			print(games.keys())
			return

		game = games[gameName]
		
		await message.channel.send ("Found Game! " + game.game + ". Playing with " + str(len(users)) + " users.")
		
		#Check player count
		if len(users) < game.minPlayers or len(users) > game.maxPlayers:
			if game.minPlayers != game.maxPlayers:
				await message.channel.send("This game only supports from " + str(game.minPlayers) + " to " + str(game.maxPlayers) + " players")
			else:
				await message.channel.send("This game only supports " + str(game.minPlayers) + " player" + ("s." if game.minPlayers>1 else "."))
			return


		#Check that user isn't trying to join two games that need dms
		if game.dmResponses:
			for player in users:
				gameDMs = database.getDMGames(player)
				if len(gameDMs)>=1:
					await message.channel.send("<@!"+str(player)+"> is currently in a game requiring DMs. This game also requires DMs. Only one game per player requiring DMs can be played at once.")
					return

		#Check that no active games have these players.
		for player in users:
			print ("Checking user " + str(player) + " in channel " + str(message.channel.id))
			res = database.getCurrentGame(message.channel.id, player)
			if res:
				currentGame = database.getCurrentGameInfo(res)
				await message.channel.send("<@!"+str(player)+"> is currently in a game of " + currentGame["name"] + ". Cannot start game")
				return
		


			
		
		await message.channel.send("All Players are free, starting game")
		
		#Create a game
		id = database.createGame(message.channel.id, gameName, users, game.dmResponses)
		
		#Get the entry for the game
		storage = {}
		await game.init(message.author.id, sorted(users),dm,message.channel.send,storage)
		database.setGameData(id, storage)	
	else:
		id = 0
		if not isChat:
			id = database.getDMGame(message.author.id)
		else: 
			id = database.getCurrentGame(message.channel.id, message.author.id)
		print("Game id is", id)

		if not id:
			await message.channel.send("You are not in a game yet. Join a game with " + COMMAND_PREFIX + "new [game]")
			return
		currentGame = database.getCurrentGameInfo(id)
		game = games[currentGame["name"]]
		print("Channel is",currentGame["channel"])
		chan = bot.get_channel(int(currentGame["channel"]))
		storage = database.getGameData(id)

		res = None
		if isChat:
			res = await game.message(msg,message.author.id, sorted(currentGame["players"]),dm, message.channel.send, storage)
		else:
			res = await game.dm(msg, message.author.id,sorted(currentGame["players"]),dm, chan.send,storage)
		database.setGameData(id, storage)
		if res:
			await chan.send("Game has finished.")
			print("Finishing Game")
			database.endGame(id,res)



@bot.event
async def on_reaction_add(reaction, user):
	isChat = isinstance(reaction.message.channel, discord.channel.TextChannel)
	# Ignore reactions on messages outside of the bot set channel
	if str(reaction.message.channel.id) != BOT_CHANNEL and BOT_CHANNEL != "all" and isChat:
		return

	# Ensure the message being reacted to is a bot message and the reaction was not added by the bot itself
	if reaction.message.author.id == bot.user.id and user.id != bot.user.id:
		# Print the Message ID and Emoji
		print(f"Reaction Added\nMessage ID: {reaction.message.id}\nEmoji: {reaction.emoji}")

		id = None
		if isChat:
			id = database.getCurrentGame(reaction.message.channel.id, user.id)
		elif not isChat:
			id = database.getDMGame(user.id)
		
		if not id:
			print ("Cannot identify game this is for")
			return
		currentGame = database.getCurrentGameInfo(id)
		game = games[currentGame["name"]]
		print("Channel is",currentGame["channel"])
		chan = bot.get_channel(int(currentGame["channel"]))

		storage = database.getGameData(id)
		res = await game.reaction(reaction, reaction.message, user.id, sorted(currentGame["players"]), user.send, chan.send, not isChat, storage)
		
		database.setGameData(id, storage)
	
		if res:
			await reaction.message.send("Game has finished.")
			print("Finishing Game")
			database.endGame(id,res)

	

print("**BOT_TOKEN is ", BOT_TOKEN)
print("CHANNEL bound to is ", BOT_CHANNEL)
bot.run(BOT_TOKEN)
