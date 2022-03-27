import json
from random import choice
from time import time

jinfo = "./config/data.json"
jteams = "./config/teams.json"
jbase = "./config/baseteam.json"
messages = json.load(open("./config/messages.json"))

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

def resetTeams():
    teams = getTeams()
    for team in teams:
        teams[team] = getBase()
    jfile = open(jteams, 'w')
    json.dump(teams, jfile)
    jfile.close()
    return "Teams refreshed!"

def addStickerToDatabase(name, points, hint):
    info = getData()
    if name not in info:
        info[name] = {"points": points, "found": False, "hint": hint}
        jfile = open(jinfo, 'w')
        json.dump(info, jfile)
        jfile.close()
        return "Sticker added to database."
    return "Sticker already exists."

def removeStickerFromDatabase(name):
    info = getData()
    if name in info:
        info.pop(name)
        jfile = open(jinfo, 'w')
        json.dump(info, jfile)
        jfile.close()
        return "Sticker removed from database."
    return "Sticker does not exist."

def updateHint(sticker, hint):
    info = getData()
    if sticker in info:
        info[sticker]["hint"] = hint
        jfile = open(jinfo, 'w')
        json.dump(info, jfile)
        jfile.close()
        return "Sticker hint updated."
    return "Sticker does not exist."

def updateStickerName(sticker, name):
    info = getData()
    if sticker in info:
        info[name] = info[sticker]
        info.pop(sticker)
        jfile = open(jinfo, 'w')
        json.dump(info, jfile)
        jfile.close()
        return "Sticker name updated."
    return "Sticker does not exist."

def updateCost(sticker, points):
    info = getData()
    if sticker in info:
        info[sticker]["points"] = points
        jfile = open(jinfo, 'w')
        json.dump(info, jfile)
        jfile.close()
        return "Sticker cost updated."
    return "Sticker does not exist."

def updateTeamName(team, name):
    teams = getTeams()
    if team in teams:
        teams[name] = teams[team]
        teams.pop(team)
        jfile = open(jteams, 'w')
        json.dump(teams, jfile)
        jfile.close()
        return "Team name updated."
    return "Team does not exist."

def addSticker(teamName, stickerName, stickerCode):
    i = 0
    #First get data
    info = getData()
    teams = getTeams()
    full_name = stickerName + stickerCode
    #Find index for sticker
    if full_name not in info:
        return "This sticker does not exist, please check your code."
    
    if full_name in teams[teamName]["stickers"]:
        return "You have already found this sticker, you're too smart!"
    else:
        s = "Sticker recorded!"
        teams[teamName]["stickers"].append(full_name)
        teams[teamName]["score"] += int(info[full_name]["points"])
        teams[teamName]["count"] += 1
        teams[teamName]["lastnewhint"] = 0
        if any(full_name == x[0] for x in teams[teamName]["hint"]):
            s += "\nYou have cleared the standard hint: {}".format(teams[teamName]["hint"].pop(teams[teamName]["hint"].index([full_name, getData()[full_name]["hint"]]))[1])
        if int(info[full_name]["points"]) > 1 and len(teams[teamName]["ghint"]) > 0:
            teams[teamName]["ghintcomplete"] = True 
            s += "\nYou have cleared the golden hint: {}".format(teams[teamName]["ghint"][1])
            teams[teamName]["ghint"] = []
        if len(teams[teamName]["stickers"]) == len(info):
            s += "\nYou have found all of the stickers!"
        jfile = open(jteams, 'w')
        json.dump(teams, jfile)
        jfile.close()
        return s
    
def addTeam(teamName):
    teams = getTeams()
    if teamName not in teams:
        teams[teamName] = getBase()
        jfile = open(jteams, 'w')
        json.dump(teams, jfile)
        jfile.close()
        return

def removeTeam(teamName):
    teams = getTeams()
    if teamName in teams:
        teams.pop(teamName)
        jfile = open(jteams, 'w')
        json.dump(teams, jfile)
        jfile.close()
        return "Team removed!"
    return "Team already does not exist."


def getScore(teamName):
    return getTeams()[teamName]["score"]

def getCount(teamName):
    return getTeams()[teamName]["count"]

def printScoreAndCount(teamName):
    if teamName not in getTeams():
        return messages["validMessage"]
    return "Score is: " + str(getScore(teamName)) + "\nYou have found this many stickers: " + str(getCount(teamName))

def getHint(teamName):
    team = getTeams()[teamName]
    data = getData()
    hints = []
    ghints = []
    for sticker in data:
        if sticker not in team["stickers"]:
            if data[sticker]["points"] == '1':
                hints.append((sticker, data[sticker]["hint"]))
            else:
                ghints.append((sticker, data[sticker]["hint"]))
    newh = False
    if time() - team["lastnewhint"] >= 1800 and len(hints) > 0:
        team["hint"].append(choice(hints))
        team["lastnewhint"] = time()
        newh = True
    newghint = False
    if team["count"] >= 0 and not team["ghintcomplete"] and len(team["ghint"]) == 0 and len(ghints) > 0:
        team["ghint"] = choice(ghints)
        newghint = True
    output = ''
    if len(hints) == 0:
        output += "You have no more hints to unlock.\n"
    elif newh:
        output += "You have a new hint!\n"
    else: 
        output += "You have {:.2f} more minutes until you can receive another standard hint.\n".format(30-((time()-team["lastnewhint"])/60))
    if len(team["hint"]) == 0:
        output += "You currently have no available standard hints.\n"
    elif len(team["hint"]) == 1:
        output += "You currently have one available standard hint:\n"
    else:
        output += "You have {} available standard hints:\n".format(len(team["hint"]))
    for hint in team["hint"]:
        output += hint[1] + "\n"
    
    if newghint:
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
    jfile = open(jteams, 'w')
    json.dump(teams, jfile)
    jfile.close()
    return output
        
    

#Basically just updating string lengths
def updateFiles(oldFile, newFile, oldTeams, newTeams):
    oldData =  open(oldFile, "w+")
    newData = open(newFile, "r")

    for line in newData:
        oldData.write(line + "\n")

    oldT =  open(oldTeams, "w+")
    newT = open(newTeams, "r")

    for line in newT:
        oldT.write(line + "\n")

    oldData.close()
    newData.close()
    oldT.close()
    newT.close()

def scoreBoard():
    teams = getTeams()

    scoreDict = dict()

    maxLen = 0

    for team in teams:
        if len(team) > maxLen:
            maxLen = len(team)

        scoreDict[team] = getScore(team), getCount(team)
    

    order = (sorted(scoreDict.items(), key = lambda x:x[1], reverse=True))


    s = ""
    s += ("╔" + "═"*(maxLen +2) + "╦" + "═"*(8) +"╦" + "═"*(8) + "╗" + "\n")
    s += ("║" + "Name".center(maxLen + 2, " ") + "║" +  "Score".center(8, " ") + "║" +"Count".center(8, " ") + "║" +"\n")

    s += ("╠"+ "═"*(maxLen+2) + "╬" + "═"*(8) +  "╬" + "═"*(8)+ "║" + "\n")

    i = 0
    for t in order:
        s += ("║" + str(t[0]).center(maxLen + 2, " ") + "║" + str(t[1][0]).center(8, " ") + "║" + str(t[1][1]).center(8, " ") + "║" + "\n")
        
        if i!= len(order) - 1:
            s += ("╠"+ "═"*(maxLen+2) + "╬" + "═"*(8) +  "╬" + "═"*(8)+ "║" + "\n")

        i+=1

    s += ("╚" + "═"*(maxLen +2) + "╩" + "═"*(8) +"╩" + "═"*(8) + "╝" + "\n")
    return s

def addtoteam():
    teams = getTeams()
    for team in teams:
        teams[team]["ghintcomplete"] = False
    jfile = open(jteams, 'w')
    json.dump(teams, jfile)
    jfile.close()

