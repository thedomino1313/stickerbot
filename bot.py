# bot.py

import json

from os.path import exists

import discord
from discord.ext import commands    # gets the bot commands archive
from discord.utils import get       # gets the finding functions
from discord.ext import commands

import data

from time import time

# Makes sure that the bot has been initialized correctly
def check_configured():
    if not exists("./config/config.json"):
        return "Please create the config.json file, or ensure that it is correctly named."
    if not exists("./config/teams.json"):
        return "Please create the teams.json file, or ensure that it is correctly named."
    if not exists("./config/data.json"):
        return "Please create the data.json file, or ensure that it is correctly named."
    if not exists("./config/locations.json"):
        return "Please create the locations.json file, or ensure that it is correctly named."
    config = json.load(open("./config/config.json"))
    if config["token"] == "inserttokentocontinue":
        return "Please enter a token to connect to your bot!"
    if config["guild"] == "Guild Name Goes Here":
        return "Please enter a guild name to connect to your server!"
    if config["backup"] == "backupChannelId (int, not a string)":
        return "Please set up your backup channel in the config file!"
    if config["scoreboard"] == ["list of valid scoreboard channels (ints, not strings)"]:
        return "Please set up your scoreboard channels in the config file!"
    return ""

# Ensure that the user has set up the needed config files.
if check_configured() != "":
    exit(check_configured())

MESSAGES = json.load(open("./config/messages.json"))
LISTS = json.load(open("./config/lists.json"))
CONFIG = json.load(open("./config/config.json"))

TOKEN = CONFIG["token"]
GUILD = CONFIG["guild"]


intents = discord.Intents.default()
intents.members = True # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

'==========================================================================================================================================='
'Event Handlers'

# Connection Information
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(MESSAGES["bootMessage"].format(bot.user, guild.name, guild.id))

    members = '\n - '.join([member.name for member in guild.members])
    roles = '\n - '.join([channel.name for channel in guild.channels])
    print(f'Guild Members:\n - {members}')
    print(f'Guild Roles:\n - {roles}')
    print(f'WelcomeBot Is Online!')

# Sending the Informational DM to the New User!
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(MESSAGES["welcomeMessage"].format(member.name))

# Allows bot to read commands in edited messages
@bot.event
async def on_raw_message_edit(msg):
    channel = await bot.fetch_channel(msg.data["channel_id"])
    msg_full = await channel.fetch_message(msg.message_id)
    await bot.process_commands(msg_full)

'==========================================================================================================================================='
'Bot Debug Commands'

# Checking Bot Ping
@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send('Welcome Bots Latency: {0}'.format(round(bot.latency, 2)))

# Checks if Responsive
@bot.command(pass_context=True)
async def status(ctx):
    await ctx.send(MESSAGES["statusMessage"])

'==========================================================================================================================================='
'Moderation Commands'

# Mod Help
@bot.command(pass_context=True)
async def modhelp(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    await ctx.channel.send(MESSAGES["modHelpMessage"])

# Creating A Private Text Channel 
@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True, manage_roles=True)
async def createchannel(ctx, *, ChannelName_Role=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    if ChannelName_Role == '': # Error checking
        await ctx.send("Please list a channel name to create.")
    
    if "#" in ChannelName_Role:
        await ctx.send("No hashtags allowed in team names >:(")
        return

    guild = ctx.guild
    role = ChannelName_Role
    authorize_role = await guild.create_role(name=role)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False), # Those without the team role can't see the channel
        
        guild.me: discord.PermissionOverwrite(read_messages=True),  # Ensures bot has permissions to see and speak in the channel
        guild.me: discord.PermissionOverwrite(send_messages=True), 

        authorize_role: discord.PermissionOverwrite(read_messages=True), # Enables users with the team role to see the channel
        authorize_role: discord.PermissionOverwrite(send_messages=True)  # Enables users with the team role to talk in the channel
    }
    await guild.create_text_channel(ChannelName_Role, overwrites=overwrites)

# Giving a member a role!
@bot.command(pass_context=True)
async def giverole(ctx, user, *, role):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    user = ctx.message.mentions[0] # Obtains user

    if get(ctx.message.guild.roles, name=role): # Ensures that the role exists
        await user.add_roles(get(ctx.message.guild.roles, name=role)) 
        await ctx.send(f"<@{user.id}> has been given the role <@&{get(ctx.message.guild.roles, name=role).id}>")
    
    else:
        await ctx.send("This role does not exist.")

# File dump and exit
@bot.command(pass_context=True)
async def keepinventory(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    await ctx.send("Goodbye for now. <3")
    channel = discord.utils.get(ctx.guild.channels, id=CONFIG["backup"]) # Gets file dump file
    for f in LISTS["files"]: # Dumps file
        await channel.send(file=discord.File(f))
    exit("All done!")

# Exit without file dump
@bot.command(pass_context=True)
async def kill(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    await ctx.send("Goodbye for now. <3")
    exit("All done!")

# Delete a team
@bot.command(pass_context=True)
async def removeteam(ctx, *, team=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif team == '': # Error Checking
        await ctx.send("Please list a team name to remove.")
    
    else:
        while "  " in team: # Removes excess spaces
            team = team.replace("  ", " ")
        while "--" in team: # Removes excess dashes
            team = team.replace("--", "-")
        team = team.replace(" ", "-").lower() # Converts to channel friendly format
        results = data.removeTeam(team)
        if results == "Team removed!": # Ensures that the team exists in the database
            channel = discord.utils.get(ctx.guild.channels, name=team)
            await channel.delete() # Removes the team channel
            role = discord.utils.get(ctx.guild.roles, name=team)
            await role.delete() # Removes the team role
        await ctx.send(results)

# Scoreboard Generation
@bot.command(pass_context=True)
async def scoreboard(ctx):
    if ctx.message.channel.id not in CONFIG["scoreboard"]: # Error checking
        await ctx.send("Looks like this isn't the right channel for that, try again in the correct location!")
        return
    
    scores = "```" + data.scoreBoard() + "```"

    embedded = discord.Embed(title = "LeaderBoard", description=scores, color = 0xF1C40F)
    await ctx.send(embed=embedded)

# Send the list of stickers
@bot.command(pass_context=True)
async def stickerlist(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    else:
        stickers = data.printStickers()
        for message in stickers:
            await ctx.send(message)

# Send the list of teams
@bot.command(pass_context=True)
async def teamlist(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    else:
        await ctx.send(data.printTeams())

# Outputs all locations
@bot.command(pass_context=True)
async def showlocations(ctx, team=""):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif ctx.message.channel.id not in CONFIG["modchannels"]:
        await ctx.send("No can do, that would show everyone every sticker location!")
        return
    
    else:
        locs = data.printLocations(team)
        for loc in locs:
            await ctx.send(loc)

# Outputs a team's info
@bot.command(pass_context=True)
async def teamprogress(ctx, team=""):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    if team == '':
        await ctx.send("Invalid input, make sure your input is in format `!teaminfo <team>`")
        return

    elif ctx.message.channel.id not in CONFIG["modchannels"]:
        await ctx.send("No can do, that would show everyone every sticker location!")
        return
    
    else:
        progress = data.teamprogress(team)
        for msg in progress:
            await ctx.send(msg)

@bot.command(pass_context=True)
async def checkdata(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    await ctx.send(data.checkequivalence())

'==========================================================================================================================================='
'Data Editing Commands'

# Adds a sticker to the database
@bot.command(pass_context=True)
async def addsticker(ctx, name='', code='', points='', *, hint=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, points, hint] or not points.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!addsticker <sticker> <authCode> <points> <hint>`")
        return
    
    else:
        await ctx.send(data.addStickerToDatabase(name.upper()+code.upper(), points, hint))

@bot.command(pass_context=True)
async def addstickers(ctx, *, stickers):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    for sticker in stickers:
        sticker = sticker.strip().split()
        if len(sticker) < 4 or not sticker[2].isdigit(): # Error checking
            await ctx.send("Invalid input for input number {}, make sure your input is in format `<sticker> <authCode> <points> <hint>`".format(sticker[0].upper() + " " + sticker[1].upper()))
            continue
        output = data.addStickerToDatabase(sticker[0].upper()+sticker[1].upper(), sticker[2], " ".join(sticker[3:]))
        await ctx.send(output[:7] + " {}".format(sticker[0].upper() + " " + sticker[1].upper()) + output[7:])

# Removes a sticker from the database
@bot.command(pass_context=True)
async def removesticker(ctx, name='', code=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!removesticker <sticker> <authCode>`")
        return
    
    else:
        await ctx.send(data.removeStickerFromDatabase(name.upper()+code.upper()))

# Changes a sticker's name
@bot.command(pass_context=True)
async def changestickername(ctx, name='', code='', newname='', newcode =''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, newname, newcode]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!changestickername <sticker> <authCode> <new sticker> <new authCode>`")
        return

    elif name.upper()+code.upper() == newname.upper()+newcode.upper(): # Error checking
        await ctx.send("You have entered the same name, please try again.")

    else:
        await ctx.send(data.updateStickerName(name.upper()+code.upper(), newname.upper()+newcode))

# Updates a sticker's hint
@bot.command(pass_context=True)
async def changestickerhint(ctx, name='', code='', *, hint=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, hint]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!changestickerhint <sticker> <authCode> <hint>`")
        return

    else:
        await ctx.send(data.updateHint(name.upper()+code.upper(), hint))

# Updates a sticker's point value
@bot.command(pass_context=True)
async def changestickerpoints(ctx, name='', code='', points=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, hint] or not points.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!changestickerpoints <sticker> <authCode> <points>`")
        return

    else:
        await ctx.send(data.updatePoints(name.upper()+code.upper(), points))

# Changes a team's name
@bot.command(pass_context=True)
async def changeteamname(ctx, name='', *, newname=''):
    while "  " in newname: # Removes excess spaces
        newname = newname.replace("  ", " ")
    
    while "--" in newname: # Removes excess dashes
        newname = newname.replace("--", "-")

    name = name.lower()
    newname = newname.replace(" ", "-").lower() # Converts to channel friendly format

    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, newname]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!changeteamname <team> <new team>`")
        return

    elif name == newname: # Error checking
        await ctx.send("You have entered the same name, please try again.")

    else:
        results = data.updateTeamName(name, newname)
        if results == "Team name updated.":
            guild = ctx.guild
            role = discord.utils.get(guild.roles, name=name)
            channel = discord.utils.get(guild.channels, name=name)
            descript = (MESSAGES["newTeamMessage"]) # Creating the embed message
            embedmessage=discord.Embed(title=f"Welcome to the {newname}'s Teams DM", description=descript, color=0x5bcdee)
            embedmessage.set_footer(text="Good Luck!")
            welcome_embed_id = data.getTeams()[data.processString(newname)]["welcome_embed"]
            team_channel_id = data.getTeams()[data.processString(newname)]["team_channel"]
            channel = await bot.fetch_channel(team_channel_id)
            message = await channel.fetch_message(welcome_embed_id)
            await message.edit(embed=embedmessage)
            await role.edit(name=newname)
            await channel.edit(name=newname)
            # data.getTeams()[newname]["message_id"]
        await ctx.send(results)

# Adds a location to the database
@bot.command(pass_context=True)
async def addlocation(ctx, building='', floors=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [building, floors] or not floors.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!addlocation <building> <floors>`")
        return
    
    else:
        await ctx.send(data.addLocationToDatabase(building.upper(), floors))

# Adds a sticker to a location
@bot.command(pass_context=True)
async def addstickertolocation(ctx, building='', floor='', name='', code='', *, location=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [building, floor, name, code, location] or not floor.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!addstickertolocation <building> <floor> <name> <code> <location>`")
        return
    
    else:
        await ctx.send(data.addStickerToLocation(building.upper(), floor, name.upper()+code.upper(), location))

# Adds stickers to a location
@bot.command(pass_context=True)
async def addstickerstolocation(ctx, *, stickers):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    stickers = stickers.split(",")
    for sticker in stickers:
        sticker = sticker.strip().split()
        if len(sticker) < 5 or not sticker[1].isdigit(): # Error checking
            await ctx.send("Invalid input for input number {}, make sure your input is in format `<building> <floor> <name> <code> <location>`".format(sticker[2].upper() + " " + sticker[3].upper()))
            continue

        await ctx.send("Sticker {}: ".format(sticker[2].upper() + " " + sticker[3].upper()) + data.addStickerToLocation(sticker[0].upper(), sticker[1], sticker[2].upper()+sticker[3].upper(), " ".join(sticker[4:])))

# Removes a sticker from a location
@bot.command(pass_context=True)
async def removestickerfromlocation(ctx, building='', floor='', name='', code=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles and ctx.message.author.id not in CONFIG["admins"]: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [building, floor, name, code] or not floor.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!removestickerfromlocation <building> <floor> <name> <code> <location>`")
        return
    
    else:
        await ctx.send(data.removeStickerFromLocation(building.upper(), floor, name.upper()+code.upper()))


'==========================================================================================================================================='
'Standard User Commands'

# Sticker code input
@bot.command(pass_context=True)
async def code(ctx, codeword='', key=''):
    t = time()
    if t < 1649682000:
        await ctx.send("The hunt hasn't started yet!")
        return
    
    elif (t > 1649725200 and t < 1649768400) or (t > 1649811600 and t < 1649854800) or (t > 1649898000 and t < 1649941200) or (t > 1649984400 and t < 1650027600):
        await ctx.send("The hunt is currently closed, please wait until 9 AM to enter codes again.")
        return
    
    elif t > 1650070800:
        await ctx.send("The hunt has closed, all scores are now final!")

    team = ctx.message.channel

    if team.name not in data.getTeams(): # Error checking
        await ctx.send(MESSAGES["validMessage"])
        return

    if codeword == '' or key == '': # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!code <sticker> <authCode>`")
        return

    await ctx.send(data.addSticker(ctx.channel.name, codeword, key))

# Creates a new team and adds the founding member 
@bot.command(pass_context=True)
async def createteam(ctx,*,role_name=''):
    if role_name == '': # Error checking
        await ctx.send("Please list a team name to create.")
        return
    
    if "#" in role_name:
        await ctx.send("No hashtags allowed in team names >:(")
        return

    while "  " in role_name: # Removes excess spaces
        role_name = role_name.replace("  ", " ")

    while "--" in role_name: # Removes excess dashes
        role_name = role_name.replace("--", "-")

    role_name = role_name.replace(" ", "-").lower() # Converts to channel friendly format
    
    author = ctx.author 
    guild = ctx.guild

    check_for_duplicate = get(ctx.message.guild.roles, name=role_name) # check if that role already exists

    if check_for_duplicate == None:
        authorize_role  = await guild.create_role(name=role_name, colour=discord.Colour(0x0000FF))

        sPeople =  discord.utils.get(guild.roles, name="@Sticker People")
        codePeople =  discord.utils.get(guild.roles, name="Leather Jacket Enthusiast and Helper")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Those without the team role can't see the channel
            
            guild.me: discord.PermissionOverwrite(read_messages=True), # Ensures bot has permissions to see and speak in the channel
            guild.me: discord.PermissionOverwrite(send_messages=True), 
            
            authorize_role: discord.PermissionOverwrite(read_messages=True), # Enables users with the team role to see the channel
            authorize_role: discord.PermissionOverwrite(send_messages=True)   # Enables users with the team role to talk in the channel
        }

        newChan = await guild.create_text_channel(role_name, overwrites=overwrites)

        await newChan.set_permissions(authorize_role, send_messages=True, read_messages = True) # May be redundant idk
        await newChan.set_permissions(sPeople, send_messages=True, read_messages = True) # May be redundant idk
        await newChan.set_permissions(codePeople, send_messages=True, read_messages = True) # May be redundant idk

        await author.add_roles(authorize_role) # Adds the role to the user

        descript = (MESSAGES["newTeamMessage"]) # Creating the embed message
        embedmessage=discord.Embed(title=f"Welcome to the {role_name}'s Teams DM", description=descript, color=0x5bcdee)
        embedmessage.set_footer(text="Good Luck!")

        # edit this embed when changing team name
        
        welcome = await newChan.send(embed=embedmessage)  # Sends DM to channel 
         # message id
        # await welcome.edit
        
        data.addTeam(role_name)

        team_channel_id = newChan.id
        new_data = data.getTeams()
        new_data[data.processString(role_name)]["welcome_embed"] = welcome.id
        new_data[data.processString(role_name)]["team_channel"] = team_channel_id
        data.jdump("./config/teams.json", new_data)
        
        await ctx.send("Your shiny new team awaits you! <#{}>".format(team_channel_id))
        
    else: # Error checking
        await ctx.send(f"This team/role already exists try another name!")

# Help function
@bot.command(pass_context=True)
async def help(ctx):
    await ctx.send(MESSAGES["helpMessage"])

# Outputs hints
@bot.command(pass_context=True)
async def hint(ctx):
    t = time()
    if t < 1649682000:
        await ctx.send("The hunt hasn't started yet!")
        return
    
    elif (t > 1649725200 and t < 1649768400) or (t > 1649811600 and t < 1649854800) or (t > 1649898000 and t < 1649941200) or (t > 1649984400 and t < 1650027600):
        await ctx.send("The hunt is currently closed, please wait until 9 AM to enter codes again.")
        return
    
    elif t > 1650070800:
        await ctx.send("The hunt has closed, all scores are now final!")
    
    team = ctx.message.channel

    if team.name not in data.getTeams(): # Error checking
        await ctx.send(MESSAGES["validMessage"])
        return

    await ctx.send(data.getHint(team.name))

# Adds user to an existing team
@bot.command(pass_context=True)
async def jointeam(ctx, roleName=''):
    if roleName == '': # Error checking
        await ctx.send("Please list a team name to join.")
        return

    forbiddenRoles = LISTS["forbidden"]
    if roleName in forbiddenRoles: # Error checking
        await ctx.send("Don't worry, we're smarter than that.")
        return

    author = ctx.message.author
    if any(role.name == roleName for role in author.roles): # Error checking
        await ctx.send("You already have a team! Contact a Sticker Person.")

    else:
        roleToAdd = discord.utils.get(ctx.guild.roles, name=roleName)
        if(roleToAdd == None): # Error checking
            await ctx.send("This is not a role!")
            
        else:
            await ctx.author.add_roles(roleToAdd)
            await ctx.send("Role has been added!")

# Outputs score
@bot.command(pass_context=True)
async def score(ctx):
    await ctx.send(data.printScoreAndCount(ctx.message.channel.name))

'==========================================================================================================================================='

bot.run(TOKEN) # end of bot
