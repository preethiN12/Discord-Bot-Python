import sqlite3,os,pickle,auth

# Connect to the DB. If it does not exist, create it.
# TODO: Currently creates DB in current directory, this will need to be changed for Docker
connection = None
cursor = None
DB_LOCATION = "games.db"

try:
    import auth
    DB_LOCATION = auth.DB_FILE
except Exception as e:
    pass
def openDb():
    global connection,cursor
    connection = sqlite3.connect(DB_LOCATION,isolation_level=None)
    # Create a cursor to interface with the database
    cursor = connection.cursor()

    # Create all necessary tables
    #cursor.execute("CREATE TABLE IF NOT EXISTS players ("
    #               "`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
    #               "`discord_id` VARCHAR(50) NOT NULL);")

    #cursor.execute("CREATE TABLE IF NOT EXISTS games ("
    #               "`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
    #               "`name` VARCHAR(50) NOT NULL);")

    cursor.execute("CREATE TABLE IF NOT EXISTS game_history ("
                "`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                "`name` VARCHAR(50) NOT NULL, "
                # "`game_id` VARCHAR(50) NOT NULL,"
                "`channel_id` VARCHAR(50) NOT NULL,"
                "`start_time` TEXT(25) DEFAULT CURRENT_TIMESTAMP,"
                "`dms` INTEGER(20) DEFAULT 0,"
                "`end_time` TEXT(25) NULL)")
                #"CONSTRAINT `game_id_fk` FOREIGN KEY (`game_id`) REFERENCES games(`id`) ON DELETE CASCADE);")

    cursor.execute("CREATE TABLE IF NOT EXISTS game_players ("
                "`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                "`game_history_id` INTEGER(20)  NOT NULL,"
                "`player_id` INTEGER(20)  NOT NULL,"
            #     "`winner` INTEGER(1) DEFAULT 0,"
                "`score` INTEGER(20) DEFAULT 0,"
                "`comments` TEXT(1000),"
                "CONSTRAINT `game_history_id_fk` FOREIGN KEY (`game_history_id`) REFERENCES game_history(`id`) ON DELETE CASCADE,"
                "CONSTRAINT `player_id_fk` FOREIGN KEY (`player_id`) REFERENCES players(`id`) ON DELETE CASCADE);")


    cursor.execute("CREATE TABLE IF NOT EXISTS game_data ("
                "`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                "`game_history_id` INTEGER(20) NOT NULL,"
                #"`key` TEXT(1000) NOT NULL,"
                "`value` BLOB,"
                "CONSTRAINT `game_history_id_fk` FOREIGN KEY (`game_history_id`) REFERENCES game_history(`id`) ON DELETE CASCADE);")

    # Commit these changes to the DB
    connection.commit()
def getGameData(game_history_id):
    cursor.execute("SELECT `value` from  `game_data` where `game_history_id`=?",[game_history_id])
    blob = cursor.fetchone()
    if blob==None:
        return {}
    return pickle.loads(blob[0])
     
def setGameData(game_history_id, value):

    blob = pickle.dumps(value)
    cursor.execute("SELECT id from `game_data` where `game_history_id`=?",[game_history_id])
    id = cursor.fetchone()
    if id==None:
        cursor.execute("INSERT INTO `game_data` (`game_history_id`,`value`) VALUES (?,?)",[game_history_id,blob])
    else:
        cursor.execute("UPDATE `game_data` set `value`=? WHERE `game_history_id` = ?",[blob, game_history_id])


def getCurrentGame(channel_id, user_id):
    cursor.execute("SELECT `game_history`.`id` from `game_history` CROSS JOIN `game_players` ON `game_players`.`game_history_id`=`game_history`.`id` WHERE `game_history`.`end_time` is null  AND `game_history`.`channel_id`=? AND `game_players`.`player_id`=?",[channel_id,user_id])
    res = cursor.fetchone()
    if res == None:
        return None
    return res[0]

def getDMGame(user_id):
    cursor.execute("SELECT `game_history`.`id` from `game_history` CROSS JOIN `game_players` ON `game_players`.`game_history_id`=`game_history`.`id` WHERE `game_history`.`end_time` is null and `game_players`.`player_id`=? AND `game_history`.`dms`=1",[user_id])
    res = cursor.fetchone()
    if res == None:
        return None
    return res[0]

def getCurrentGameInfo(game_history_id):
    cursor.execute("SELECT `name`,`dms`,`channel_id` from `game_history` where `id` = ? AND `end_time` is null",[game_history_id])
    res = cursor.fetchone()
    if res == None:
        return None
    gameName = res[0]
    dms = res[1]
    chan = res[2]
    cursor.execute("SELECT `player_id` from `game_players` where `game_history_id`=?",[game_history_id])
    players = []
    for val in cursor.fetchall():
        players.append(val[0])
    return {
        "name": gameName,
        "players": players,
        "channel":chan,
        "id":game_history_id,
        "dm":dms
    }

def createGame(channel_id, game_type, player_ids, dms):
    #cursor.execute("INSERT INTO games (`name`) VALUES (?)",[game_type])
    cursor.execute("INSERT INTO game_history (`name`,`channel_id`,`dms`) VALUES (?,?,?)",[game_type,channel_id,dms])
    gameId = cursor.lastrowid
    for id in player_ids:
        cursor.execute("INSERT INTO game_players (`game_history_id`,`player_id`) VALUES (?,?)",[gameId, id])
    return gameId

def getPlayersGames(player_id):
    cursor.execute("SELECT `name` from `game_players` LEFT JOIN `game_history` ON `game_history`.`id` = `game_players`.`game_history_id` WHERE `player_id` = ? AND `end_time` is null",[player_id])
    return [game[0] for game in cursor.fetchall()]

def getDMGames(player_id):
    cursor.execute("SELECT `name` from `game_players` LEFT JOIN `game_history` ON `game_history`.`id` = `game_players`.`game_history_id` WHERE `player_id` = ? AND `end_time` is null AND `game_history`.`dms`=1",[player_id])
    return [game[0] for game in cursor.fetchall()]

def addPlayer(game_history_id, player_id):
    cursor.execute("INSERT INTO game_players (`game_history_id`,`player_id`) VALUES (?,?)",[game_history_id, player_id])

# player_scores is [{id:1, score:1}]
def endGame(game_history_id, player_scores):
    cursor.execute("DELETE from `game_data` where `game_history_id`=?",[game_history_id])
    cursor.execute("UPDATE `game_history` set end_time=CURRENT_TIMESTAMP where `id`=?",[game_history_id])
    for player in player_scores:
        cursor.execute("UPDATE `game_players` set score=? where `player_id` = ? AND `game_history_id` = ?",[player_scores[player],player,game_history_id])

#old
def getPlayer(discord_id):
    cursor.execute("SELECT `id` from `players` where `discord_id`=?",[discord_id])
    player = cursor.fetchone()
    if player == None:
        cursor.execute("INSERT INTO `players` (`discord_id`) VALUES (?)",[discord_id])
        return cursor.lastrowid
    return player[0]


def getPlayerScoreSummary(player_id):
    cursor.execute("SELECT sum(score) from `game_players` where `player_id` = ? ",[player_id])
    res = cursor.fetchone()
    if len(res)>0:
        return res[0]
    return 0


def closeDb():
    connection.close()
