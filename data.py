import json
from random import choice
from time import time

'==========================================================================================================================================='
'Constants'

jinfo = "./config/data.json"
jteams = "./config/teams.json"
jbase = "./config/baseteam.json"
jloc = "./config/locations.json"
messages = json.load(open("./config/messages.json"))

'==========================================================================================================================================='
'String editors'

def processString(teamName): # Converts unicode characters to a json friendly format
    return str(teamName.encode('ascii', 'xmlcharrefreplace'))[2:-1]

def revertString(teamName): # Reverts json friendly format to unicode characters
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


def replaceEmojis(word): # Converts unicode emojis to an empty box for scoreboard printing
    s = ''
    for char in word:
        if char.isascii():
            s += char
        else:
            s += '□'
    return s

def namesplit(code):
    names = ['mercury', 'venus', 'earth', 'jupiter', 'mars', 'pluto', 'saturn', 'uranus', 'neptune', 'apollo1', 'apollo2', 'apollo3', 'apollo4', 'apollo5', 'apollo6', 'apollo7', 'apollo8', 'apollo9', 'apollo10', 'apollo11', 'apollo12', 'apollo13', 'rocket', 'space', 'moon', 'lander', 'flight', 'fly', 'fuel', 'buzz', 'carbon', 'oxygen', 'ares', 'life', 'nasa', 'rover', 'boost', 'cosmo', 'star', 'nova', 'blkhole', 'galaxy', 'curious', 'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india', 'julliet', 'kilo', 'lima', 'mike', 'oscar', 'papa', 'romeo', 'sierra', 'tango', 'x-ray', 'zulu', 'marty', 'meteor', 'asteroid', 'astro', 'bigbang', 'dwarf', 'centaur', 'comet', 'corona', 'cosmic', 'dust', 'debris', 'node', 'epoch', 'equator', 'velocity', 'thrust', 'flare', 'gas', 'giant', 'helios', 'planet', 'kepler', 'belt', 'lunar', 'magnet', 'clouds', 'nebula', 'neutron', 'opaque', 'orbit', 'plane', 'speed', 'fast', 'phase', 'polar', 'quasar', 'radio', 'sat', 'axis', 'day', 'night', 'time', 'spiral', 'gravity', 'period', 'super', 'tidal', 'stream', 'erosion', 'twilight', 'taurus', 'gemini', 'cancer', 'leo', 'viro', 'libra', 'scorpio', 'pisces', 'lens', 'prop', 'retro', 'transit', 'journey', 'venture', 'voyage', 'pioneer', 'engineer', 'scientist', 'zenith', 'waning', 'waxing', 'tech', 'innovate', 'make', 'create', 'build', 'hubble', 'galilei', 'cassini', 'newton', 'halley', 'messier', 'herschel', 'piazzi', 'laplace', 'bessel', 'lassell', 'barnard', 'pickering', 'draper', 'lockyer', 'artemis', 'atlas', 'electron', 'falcon', 'iss', 'angara', 'ceres', 'hyperbola', 'pegasus', 'icarus', 'proton', 'simorgh', 'vega', 'unha', 'alpha', 'beta', 'gamme', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega']
    for name in names:
        if name in code:
            code = code[0:len(name)] + " " + code[len(name):]
            break
    return code

'==========================================================================================================================================='
'Accessors'

def getData():
    return json.load(open(jinfo))

def getTeams():
    return json.load(open(jteams))

def getBase():
    return json.load(open(jbase))

def getLocations():
    return json.load(open(jloc))

def printTeams():
    teams = getTeams()
    s = ''
    for team in teams:
        s += str(revertString(team)) + "\n"
    return s

def printStickers():
    stickers = getData()
    returnlist = []
    s = '```\n'
    for sticker in stickers:
        if len(s) + len(namesplit(sticker).ljust(15) + stickers[sticker]["points"] + " " + stickers[sticker]["hint"] + "\n") + 3 >= 2000:
            returnlist.append(s+"```")
            s = '```\n'
        s += namesplit(sticker).ljust(15) + stickers[sticker]["points"] + " " + stickers[sticker]["hint"] + "\n"
    returnlist.append(s+"```")
    return returnlist

# def getNumNames(teamName):
#     return getTeams()[teamName]["name_changes"]

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
        return f"Team {teamName} removed!"
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

# Adds a new location to the database
def addLocationToDatabase(building, floors):
    loc = getLocations()
    if building not in loc: # Error checking
        loc[building] = {} # Adds the location to the database
        for i in range(int(floors)):
            loc[building][i+1] = {}
        jdump(jloc, loc)
        return "Location added to database."
    return "Location already exists."

# Adds a sticker to a location
def addStickerToLocation(building, floor, sticker, location):
    building = building.upper()
    loc = getLocations()
    info = getData()
    if building in loc:
        if floor in loc[building]:
            if sticker in info:
                loc[building][floor][sticker] = location
                jdump(jloc, loc)
                return "Sticker added to location."
            return "This sticker does not exist."
        return "This floor does not exist."
    return "This building does not exist."

# Removes a sticker from a location
def removeStickerFromLocation(building, floor, sticker):
    loc = getLocations()
    if building in loc:
        if floor in loc[building]:
            if sticker in loc[building][floor]:
                loc[building][floor].pop(sticker)
                jdump(jloc, loc)
                return "Sticker removed from location."
            return "This sticker does not exist."
        return "This floor does not exist."
    return "This building does not exist."

# Removes all stickers from all locations
def removeAllStickersFromLocations(building, floor):
    loc = getLocations()
    if building in loc:
        if floor:
            if floor in loc[building]:
                loc[building][floor] = dict()
                jdump(jloc, loc)
                return "All stickers removed from location."
            return "This floor does not exist."
        else:
            for f in loc[building]:
                loc[building][f] = dict()
            jdump(jloc, loc)
            return "All stickers removed from location."
    elif building == "ALL":
        for b in loc:
            for f in loc[b]:
                loc[b][f] = dict()
        jdump(jloc, loc)
        return "All stickers removed from all locations."
    return "This building does not exist."

# Prints all locations and their stickers
def printLocations(team):
    loc = getLocations()
    teams = getTeams()
    returnlist = []
    s = '```\n'
    if team != "" and team not in teams:
        return ["This team does not exist!"]
    if len(loc) == 0:
        return ["There are no locations yet."]
    for building in loc:
        if len(s) + len(building + '\n') + 3 >= 2000:
            returnlist.append(s+"```")
            s = '```\n'
        s += building + '\n'
        for floor in loc[building]:
            if len(s) + len("\tFloor " + floor + ":\n") + 3 >= 2000:
                returnlist.append(s+"```")
                s = '```\n'
            s += "\tFloor " + floor + ":\n"
            if len(loc[building][floor]) == 0:
                if len(s) + len("\t\tNo stickers on this floor.\n") + 3 >= 2000:
                    returnlist.append(s+"```")
                    s = '```\n'
                s += "\t\tNo stickers on this floor.\n"
            for sticker in loc[building][floor]:
                if len(s) + len("\t\t" + namesplit(sticker) + ": " + loc[building][floor][sticker] + "\n") + 9 >= 2000:
                    returnlist.append(s+"```")
                    s = '```\n'
                s += "\t\t"
                if team != "":
                    if sticker in teams[team]["stickers"]:
                        s += "(1/1) "
                    else:
                        s += "(0/1) "
                s += namesplit(sticker) + ": " + loc[building][floor][sticker] + "\n"
    returnlist.append(s+ "```")
    return returnlist

# Prints progress of a team and the stickers they have found in location order
def teamprogress(team):
    returnlist = []
    teams = getTeams()
    info = getData()
    totalS = 0
    totalG = 0
    teamS = 0
    teamG = 0
    if team not in teams:
        return ["This team does not exist!"]
    for sticker in info:
        if info[sticker]["points"] == '1':
            totalS += 1
            if sticker in teams[team]:
                teamS += 1
        else:
            totalG += 1
            if sticker in teams[team]:
                teamG += 1

    s = ''
    s += "Team {} has found:\n{}/{} standard stickers\n{}/{} gold stickers\nSticker location report:".format(team, teamS, totalS, teamG, totalG)
    returnlist.append(s)
    returnlist += printLocations(team)
    return returnlist
    

'==========================================================================================================================================='
'Main Operations'

# Adds a sticker to a team's collection
def addSticker(teamName, stickerName, stickerCode):
    teams = getTeams()
    full_name = stickerName.upper() + stickerCode.upper()
    info = getData() # Outdated collection takes the code in two pieces, will probably fix eventually
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
        if any(full_name == x[0] for x in teams[teamName]["ghint"]): # Checks if the sticker found relates to the team's special hint
            s += "\nYou have cleared the special hint: {}".format(teams[teamName]["ghint"].pop(teams[teamName]["ghint"].index([full_name, getData()[full_name]["hint"]]))[1])
            teams[teamName]["ghint"] = []
            teams[teamName]["ghintcomplete"] = True
        if len(teams[teamName]["stickers"]) == len(info): # Checks if the team has found every sticker
            s += "\nYou have found all of the stickers!"
        if teams[teamName]["count"] == 20:
            teams[teamName]["ghintcomplete"] = True
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
    output = [""]
    for sticker in data: # Loops through all stickers and determines if the team can receive a hint for them
        if sticker not in team["stickers"] and [sticker, data[sticker]["hint"]] not in team["hint"] and [sticker, data[sticker]["hint"]] not in team["ghint"]:
            if data[sticker]["points"] != '10':
                hints.append((sticker, data[sticker]["hint"]))
            else:
                ghints.append((sticker, data[sticker]["hint"]))

    newh = False # Bool to see if a new hint is added
    if time() - team["lastnewhint"] >= 1800 and len(hints) > 0: # Validating
        team["hint"].append(choice(hints))
        team["lastnewhint"] = time()
        newh = True
    
    newghint = False # Bool to see if a new hint is added
    if team["count"] >= 20 and team["ghintcomplete"] and len(ghints) > 0: # Validating
        team["ghintcomplete"] = False
        team["ghint"].append(choice(ghints))
        newghint = True
    
    if len(hints) == 0: # Logic for basic hint message
        output[-1] += "You have no more hints to unlock.\n"
    elif newh:
        output[-1] += "You have a new hint!\n"
    else: 
        output[-1] += "You have {:.2f} more minutes until you can receive another standard hint.\n".format(30-((time()-team["lastnewhint"])/60))
    
    if len(team["hint"]) == 0: # Logic for listing all standard hints
        output[-1] += "You currently have no available standard hints.\n"
    elif len(team["hint"]) == 1:
        output[-1] += "You currently have one available standard hint:\n"
    else:
        output[-1] += "You have {} available standard hints:\n".format(len(team["hint"]))
    for hint in team["hint"]:
        if len(output[-1] + hint[1] + "\n") >= 2000:
            output += [""]
        output[-1] += hint[1] + "\n"
    
    if len(ghints) == 0: # Logic for basic hint message
        output[-1] += "You have no more special hints to unlock.\n"
    elif newghint:
        output[-1] += "You have a new special hint!\n"
    elif team["count"] < 20: 
        output[-1] += "You have {} more stickers to find until you can receive another special hint.\n".format(20 - (team["count"]%20))
    else:
        output[-1] += "You will recieve another special hint when you complete your current one."
    
    if len(team["ghint"]) == 0: # Logic for listing all standard hints
        output[-1] += "You currently have no available special hints.\n"
    elif len(team["ghint"]) == 1:
        output[-1] += "You currently have one available special hint:\n"
    else:
        output[-1] += "You have {} available special hints:\n".format(len(team["ghint"]))
    for hint in team["ghint"]:
        output[-1] += hint[1] + "\n"

    teams = getTeams()
    teams[teamName] = team
    jdump(jteams, teams)
    return output

# Formats all teams' scores and sticker counts into a scoreboard
def scoreBoard():
    teams = getTeams()
    scoreDict = dict()
    maxLen = 0

    if not teams:
        return ''

    for team in teams: # Finds the longest team name, and adds their score and counts to a dictionary
        team = revertString(team)
        if len(team) > maxLen:
            maxLen = len(team)

        scoreDict[replaceEmojis(team)] = getScore(team), getCount(team)

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


# timestamp, name, code, hint, points, location, building, floor,
def file_input(f):
    data = f.replace("\r", '').replace('"', '').replace("\\", '').split("\n")
    if any([len(x.split(",")) != len(data[0].split(",")) for x in data]):
        return ["Invalid input, there is an extra comma somewhere."]
    out = []
    for line in data[1:]:
        line = list(map(lambda x: x.strip(), line.split(",")))
        if addStickerToDatabase(line[1].upper() + line[2].upper(), line[4], line[3]) == "Sticker already exists.":
            out.append(f"Sticker {line[1].upper() + line[2].upper()} already exists.")
        if addStickerToLocation(line[6], line[7], line[1].upper() + line[2].upper(), line[5]) in ['This floor does not exist.', 'This building does not exist.']:
            return [f"Building {line[6]} either does not exist, or floor {line[7]} does not exist."]
    if out == '':
        return ["Successfully added all stickers."]
    else:
        return out + ["Successfully added all other stickers."]



'==========================================================================================================================================='
'Data Checkers'

def checkequivalence():
    loc = getLocations()
    data = getData()
    s = ''
    locSticks = set()
    dataSticks = set()
    for building in loc:
        for floor in loc[building]:
            for sticker in loc[building][floor]:
                locSticks.add(sticker)
    for sticker in data:
        dataSticks.add(sticker)
    if not locSticks.issubset(dataSticks):
        s += "These stickers are in the locations list, but not in the main sticker data:\n"
        for sticker in locSticks-dataSticks:
            s += sticker + " "
    if not dataSticks.issubset(locSticks):
        s += "\nThese stickers are in the main sticker data, but not in the locations list:\n"
        for sticker in dataSticks-locSticks:
            s += sticker + " "
    if not s:
        return "All stickers match!"
    return s