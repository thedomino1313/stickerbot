# bot.py

import json

from os.path import exists
from tabnanny import check

import discord
from discord.ext import commands    # gets the bot commands archive
from discord.utils import get       # gets the finding functions
from discord.ext import commands

import data

# Makes sure that the bot has been initialized correctly
def check_configured():
    if not exists("./config/config.json"):
        return "Please create the config.json file, or ensure that it is correctly named."
    if not exists("./config/teams.json"):
        return "Please create the teams.json file, or ensure that it is correctly named."
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
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    await ctx.channel.send(MESSAGES["modHelpMessage"])

# Creating A Private Text Channel 
@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True, manage_roles=True)
async def createchannel(ctx, *, ChannelName_Role=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    
    if ChannelName_Role == '': # Error checking
        await ctx.send("Please list a channel name to create.")
    
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
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
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
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
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
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
        return
    await ctx.send("Goodbye for now. <3")
    exit("All done!")

# Delete a team
@bot.command(pass_context=True)
async def removeteam(ctx, *, team=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif team == '': # Error Checking
        await ctx.send("Please list a team name to remove.")
    
    else:
        team = team.lower()
        await ctx.send(data.removeTeam(team)) # Removes the team from the json
        channel = discord.utils.get(ctx.guild.channels, name=team.replace(" ", "-"))
        await channel.delete() # Removes the team channel
        role = discord.utils.get(ctx.guild.roles, name=team)
        await role.delete() # Removes the team role

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
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    else:
        await ctx.send(data.printStickers())

# Send the list of teams
@bot.command(pass_context=True)
async def teamlist(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    else:
        await ctx.send(data.printTeams())

'==========================================================================================================================================='
'Data Editing Commands'

# Adds a sticker to the database
@bot.command(pass_context=True)
async def addsticker(ctx, name='', code='', points='', *, hint=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, points, hint] or not points.isdigit(): # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!addsticker <sticker> <authCode> <points> <hint>")
        return
    
    else:
        await ctx.send(data.addStickerToDatabase(name.upper()+code, points, hint))

# Removes a sticker from the database
@bot.command(pass_context=True)
async def removesticker(ctx, name='', code=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!removesticker <sticker> <authCode>")
        return
    
    else:
        await ctx.send(data.removeStickerFromDatabase(name.upper()+code))

# Changes a sticker's name
@bot.command(pass_context=True)
async def changestickername(ctx, name='', code='', newname='', newcode =''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, newname, newcode]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!removesticker <sticker> <authCode>")
        return

    elif name.upper()+code == newname.upper()+newcode:
        await ctx.send("You have entered the same name, please try again.")

    else:
        await ctx.send(data.updateStickerName(name.upper()+code, newname.upper()+newcode))

# Updates a sticker's hint
@bot.command(pass_context=True)
async def changestickerhint(ctx, name='', code='', *, hint=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles: # Ensures that user has proper permissions
        await ctx.send(MESSAGES["noAccess"])
    
    elif '' in [name, code, hint]: # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!removesticker <sticker> <authCode>")
        return

    else:
        await ctx.send(data.updateHint(name.upper()+code, hint))

'==========================================================================================================================================='
'Standard User Commands'

# Sticker code input
@bot.command(pass_context=True)
async def code(ctx, codeword='', key=''):
    team = ctx.message.channel

    if team.name not in data.getTeams(): # Error checking
        await ctx.send(MESSAGES["validMessage"])
        return

    if codeword == '' or key == '': # Error checking
        await ctx.send("Invalid input, make sure your input is in format `!code <sticker> <authCode>")
        return

    await ctx.send(data.addSticker(ctx.channel.name, codeword, key))

# Creates a new team and adds the founding member 
@bot.command(pass_context=True)
async def createteam(ctx,*,role_name=''):
    if role_name == '': # Error checking
        await ctx.send("Please list a team name to create.")
        return
    
    while "  " in role_name: # Removes excess spaces
        role_name = role_name.replace("  ", " ")
    
    
    author = ctx.author 
    guild = ctx.guild

    check_for_duplicate = get(ctx.message.guild.roles, name=role_name) # check if that role already exists

    if check_for_duplicate == None:
        authorize_role  = await guild.create_role(name=role_name, colour=discord.Colour(0x0000FF))

        sPeople =  discord.utils.get(guild.roles, name="@Sticker People")

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

        await author.add_roles(authorize_role) # Adds the role to the user

        descript = (MESSAGES["newTeamMessage"]) # Creating the embed message
        embedmessage=discord.Embed(title=f"Welcome to the {role_name}'s Teams DM", description=descript, color=0x5bcdee)
        embedmessage.set_footer(text="Good Luck!")
        
        await newChan.send(embed=embedmessage)  # Sends DM to channel

        data.addTeam(role_name)

        team_channel_id = newChan.id
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
