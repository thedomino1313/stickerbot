import json
from random import choice
from time import time

'==========================================================================================================================================='
'Constants'

jinfo = "./config/data.json"
jteams = "./config/teams.json"
jbase = "./config/baseteam.json"
messages = json.load(open("./config/messages.json"))

'==========================================================================================================================================='
'String editors'

def processString(teamName):
    return str(teamName.encode('ascii', 'xmlcharrefreplace'))[2:-1]

def revertString(teamName):
    teamNameList = list(teamName)
    reverted = []
    for i in range(len(teamNameList) - 1):
        if teamNameList[i] == "&" and teamNameList[i + 1] == "#":
            for j in range(i, len(teamNameList)):
                if teamNameList[j] == ";":
                    reverted.append(chr(int(''.join(teamNameList[ i + 2 : j ]))))
                    teamNameList[i : j + 1] = ['' for i in range(i, j + 1)]
                    i = j + 1
                    break
        else:
            reverted.append(teamNameList[i])

    reverted.append(teamNameList[-1])
    return ''.join(reverted)

'==========================================================================================================================================='
'Accessors'

def getData():
    return json.load(open(jinfo))

def getTeams():
    return json.load(open(jteams))

def getBase():
    return json.load(open(jbase))

def printTeams():
    teams = getTeams()
    s = ''
    for team in teams:
        s += str(team) + "\n"
    return s

def printStickers():
    stickers = getData()
    s = '```'
    for sticker in stickers:
        s += sticker.ljust(15) + stickers[sticker]["points"] + " " + stickers[sticker]["hint"] + "\n"
    return s + "```"

'==========================================================================================================================================='
'JSON Modifiers'

# Updates the specified file with the new dictionary
def jdump(file, data):
    jfile = open(file, 'w')
    json.dump(data, jfile)
    jfile.close()

# Adds a new sticker to the database
def addStickerToDatabase(name, points, hint):
    info = getData()
    if name not in info: # Error checking
        info[name] = {"points": points, "found": False, "hint": hint} # Adds the sticker to the database
        jdump(jinfo, info)
        return "Sticker added to database."
    return "Sticker already exists."

# Removes a sticker from the database
def removeStickerFromDatabase(name):
    info = getData()
    if name in info: # Error checking
        info.pop(name) # Removes the sticker from the database
        jdump(jinfo, info)
        return "Sticker removed from database."
    return "Sticker does not exist."

# Changes a sticker's name
def updateStickerName(sticker, name):
    info = getData()
    if sticker in info: # Error checking
        info[name] = info[sticker] # Adds the sticker with the new name
        info.pop(sticker) # Removes the sticker with the old name
        jdump(jinfo, info)
        return "Sticker name updated."
    return "Sticker does not exist."

# Updates a sticker's hint
def updateHint(sticker, hint):
    info = getData()
    if sticker in info: # Error checking
        info[sticker]["hint"] = hint # Changes the sticker's hint
        jdump(jinfo, info)
        return "Sticker hint updated."
    return "Sticker does not exist."

# Updates a sticker's point value
def updatePoints(sticker, points):
    info = getData()
    if sticker in info: # Error checking
        info[sticker]["points"] = points # Changes the sticker's point value
        jdump(jinfo, info)
        return "Sticker cost updated."
    return "Sticker does not exist."

# Adds a team to the database
def addTeam(teamName):
    teams = getTeams()
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    if teamName not in teams: # Error checking
        teams[teamName] = getBase() # Assigns the team's value to basic team values and saves it in the database
        jdump(jteams, teams)
        return

# Removes a team from the database
def removeTeam(teamName):
    teams = getTeams()
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    if teamName in teams: # Error checking
        teams.pop(teamName) # Removes the team from the database
        jdump(jteams, teams)
        return "Team removed!"
    return "Team already does not exist."

# Changes a team's name
def updateTeamName(team, name):
    teams = getTeams()
    team = processString(team) # Converts unicode emojis into a JSON safe format
    name = processString(name)
    if team in teams: # Error checking
        teams[name] = teams[team] # Adds the team with the new name
        teams.pop(team) # Removes the team with the old name
        jdump(jteams, teams)
        return "Team name updated."
    return "Team does not exist."

# Resets all of the teams' data
def resetTeams():
    teams = getTeams()
    for team in teams:
        teams[team] = getBase() # Assigns each team's value to basic team values
    jdump(jteams, teams)
    return "Teams refreshed!"

# Adds a parameter to each team (developer function, call it in the main of this file)
def addtoteam():
    teams = getTeams()
    for team in teams:
        teams[team]["ghintcomplete"] = False # This can change
    jdump(jteams, teams)

'==========================================================================================================================================='
'Main Operations'

# Adds a sticker to a team's collection
def addSticker(teamName, stickerName, stickerCode):
    info = getData()
    teams = getTeams()
    full_name = stickerName + stickerCode # Outdated collection takes the code in two pieces, will probably fix eventually
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    if full_name not in info: # Error checking
        return "This sticker does not exist, please check your code."
    
    if full_name in teams[teamName]["stickers"]: # Error checking
        return "You have already found this sticker, you're too smart!"
    else:
        s = "Sticker recorded!"
        teams[teamName]["stickers"].append(full_name) # Updating team data
        teams[teamName]["score"] += int(info[full_name]["points"])
        teams[teamName]["count"] += 1
        teams[teamName]["lastnewhint"] = 0
        if any(full_name == x[0] for x in teams[teamName]["hint"]): # Checks if the sticker found relates to a hint that the team has unlocked
            s += "\nYou have cleared the standard hint: {}".format(teams[teamName]["hint"].pop(teams[teamName]["hint"].index([full_name, getData()[full_name]["hint"]]))[1])
        if int(info[full_name]["points"]) > 1 and len(teams[teamName]["ghint"]) > 0: # Checks if the sticker found relates to the team's golden hint
            teams[teamName]["ghintcomplete"] = True 
            s += "\nYou have cleared the golden hint: {}".format(teams[teamName]["ghint"][1])
            teams[teamName]["ghint"] = []
        if len(teams[teamName]["stickers"]) == len(info): # Checks if the team has found every sticker
            s += "\nYou have found all of the stickers!"
        jdump(jteams, teams)
        return s

# Gets a team's score
def getScore(teamName):
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    return getTeams()[teamName]["score"]

# Gets a team's sticker count
def getCount(teamName):
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    return getTeams()[teamName]["count"]

# Gets a team's score and count in a formatted message
def printScoreAndCount(teamName):
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    if teamName not in getTeams(): # Error checking
        return messages["validMessage"]
    return "Score is: " + str(getScore(teamName)) + "\nYou have found this many stickers: " + str(getCount(teamName))

# Determines if the team can receive a new hint and sends all available hints
def getHint(teamName):
    teamName = processString(teamName) # Converts unicode emojis into a JSON safe format
    team = getTeams()[teamName]
    data = getData()
    hints = []
    ghints = []
    for sticker in data: # Loops through all stickers and determines if the team can receive a hint for them
        if sticker not in team["stickers"] and [sticker, data[sticker]["hint"]] not in team["hint"]:
            if data[sticker]["points"] == '1':
                hints.append((sticker, data[sticker]["hint"]))
            else:
                ghints.append((sticker, data[sticker]["hint"]))

    newh = False # Bool to see if a new hint is added
    if time() - team["lastnewhint"] >= 1800 and len(hints) > 0: # Validating
        team["hint"].append(choice(hints))
        team["lastnewhint"] = time()
        newh = True
    
    newghint = False # Bool to see if a new hint is added
    if team["count"] >= 20 and not team["ghintcomplete"] and len(team["ghint"]) == 0 and len(ghints) > 0: # Validating
        team["ghint"] = choice(ghints)
        newghint = True
    
    output = ''
    if len(hints) == 0: # Logic for basic hint message
        output += "You have no more hints to unlock.\n"
    elif newh:
        output += "You have a new hint!\n"
    else: 
        output += "You have {:.2f} more minutes until you can receive another standard hint.\n".format(30-((time()-team["lastnewhint"])/60))
    
    if len(team["hint"]) == 0: # Logic for listing all standard hints
        output += "You currently have no available standard hints.\n"
    elif len(team["hint"]) == 1:
        output += "You currently have one available standard hint:\n"
    else:
        output += "You have {} available standard hints:\n".format(len(team["hint"]))
    for hint in team["hint"]:
        output += hint[1] + "\n"
    
    if newghint: # Logic for golden hint message
        output += "You have just unlocked a golden hint! The hint is:\n{}".format(team["ghint"][1])
    elif team["count"] >= 0 and not team["ghintcomplete"] and len(team["ghint"]) == 0 and len(ghints) == 0:
        output += "You found all of the golden stickers without a golden hint, congratulations!"
    elif len(team["ghint"]) == 0 and team["count"] < 20:
         output += "You will unlock a golden sticker hint after you find {} more stickers.\n".format(20-team["count"])
    elif not team["ghintcomplete"]:
        output += "Your golden sticker hint is:\n{}".format(team["ghint"][1])
    else:
        output += "You have already solved your golden hint, congratulations!"
    
    teams = getTeams()
    teams[teamName] = team
    jdump(jteams, teams)
    return output

# Formats all teams' scores and sticker counts into a scoreboard
def scoreBoard():
    teams = getTeams()
    scoreDict = dict()
    maxLen = 0

    for team in teams: # Finds the longest team name, and adds their score and counts to a dictionary
        if len(team) > maxLen:
            maxLen = len(team)

        scoreDict[team] = getScore(team), getCount(team)

    order = (sorted(scoreDict.items(), key = lambda x:x[1], reverse=True)) # Sorts the teams by score

    s = ""

    s += ("╔" + "═"*(maxLen +2) + "╦" + "═"*(8) +"╦" + "═"*(8) + "╗" + "\n") # Header row
    s += ("║" + "Name".center(maxLen + 2, " ") + "║" +  "Score".center(8, " ") + "║" +"Count".center(8, " ") + "║" +"\n")

    s += ("╠"+ "═"*(maxLen+2) + "╬" + "═"*(8) +  "╬" + "═"*(8)+ "║" + "\n")

    i = 0
    for t in order: # Adds the teams to the board
        s += ("║" + str(t[0]).center(maxLen + 2, " ") + "║" + str(t[1][0]).center(8, " ") + "║" + str(t[1][1]).center(8, " ") + "║" + "\n")
        if i!= len(order) - 1:
            s += ("╠"+ "═"*(maxLen+2) + "╬" + "═"*(8) +  "╬" + "═"*(8)+ "║" + "\n")
        i+=1

    s += ("╚" + "═"*(maxLen +2) + "╩" + "═"*(8) +"╩" + "═"*(8) + "╝" + "\n") # Bottom border
    return s
