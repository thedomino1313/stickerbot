# bot.py

import os
import json

import discord
from discord.ext import commands    # gets the bot commands archive
from discord.utils import get       # gets the finding functions
from discord.ext import commands

import Data

messages = json.load(open("./config/messages.json"))
lists = json.load(open("./config/lists.json"))
config = json.load(open("./config/config.json"))

if config["token"] == "inserttokentocontinue":
    exit("Please enter a token to connect to your bot!")
TOKEN = config["token"]

if config["guild"] == "Guild Name Goes Here":
    exit("Please enter a guild name to connect to your server!")
GUILD = config["guild"]


intents = discord.Intents.default()
intents.members = True # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

## EVENTS
@bot.event # Connection Information
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(messages["bootMessage"].format(bot.user, guild.name, guild.id))

    members = '\n - '.join([member.name for member in guild.members])
    roles = '\n - '.join([channel.name for channel in guild.channels])
    print(f'Guild Members:\n - {members}')
    print(f'Guild Roles:\n - {roles}')

    print(f'WelcomeBot Is Online!')

@bot.event  # Sending the Informational DM to the New User!
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(messages["welcomeMessage"].format(member.name))

## CORE BLOCK COMMANDS
@bot.event
async def on_raw_message_edit(msg):
    channel = await bot.fetch_channel(msg.data["channel_id"])
    msg_full = await channel.fetch_message(msg.message_id)
    await bot.process_commands(msg_full)

'==========================================================================================================================================='
'Bot Debug Commands'

# Checking Bot Ping
@bot.command(name='ping', help="Gives bot's ping.",pass_context=True)
async def ping(ctx):
    await ctx.send('Welcome Bots Latency: {0}'.format(round(bot.latency, 2)))

@bot.command(name='status', help="Gives bot's status.",pass_context=True)
async def status(ctx):
    # Checks if Responsive
    await ctx.send(messages["statusMessage"])

'==========================================================================================================================================='
'Moderation Commands'

# Mod Help
@bot.command(name="modhelp")
async def modhelp(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
        return
    
    await ctx.channel.send(messages["modHelpMessage"])

# Creating A Private Text Channel 
@bot.command(name='createchannel', help="Creates the private team channel")
@commands.has_permissions(manage_channels=True, manage_roles=True)
async def createchannel(ctx, *, ChannelName_Role=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
        return
    
    if ChannelName_Role == '':
        await ctx.send("Please list a channel name to create.")
    guild = ctx.guild
    role =  ChannelName_Role
    autorize_role = await guild.create_role(name=role)
    overwrites = {
        # normies just joining cant see it!
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        # guild.me is the bot so it keeps the bot from taking commands in new channel
        guild.me: discord.PermissionOverwrite(read_messages=True), 
        guild.me: discord.PermissionOverwrite(send_messages=True), 
        # People with a specific role can see it
        #ctx.author : discord.PermissionOverwrite(read_messages=True),
        autorize_role: discord.PermissionOverwrite(read_messages=True),
        autorize_role: discord.PermissionOverwrite(send_messages=True)
    }
    await guild.create_text_channel(ChannelName_Role, overwrites=overwrites)
    # await ctx.author.add_roles(autorize_role)

# Giving a member a role!
@bot.command(name='giverole', help="Gives a member a specific role/assigns team",pass_context=True)
async def giverole(ctx, user: discord.Member, role: discord.Role): # !giverole [Member] [Role]
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
        return
    
    # Adds the Role to the user 
    await user.add_roles(role)

    # Sends confirmation message
    await ctx.send(f"The User {ctx.author.name}, {user.name} has been giving a role called: {role.name}") ##FOR DEBUGGING REMOVE THIS LINE

# File dump and exit
@bot.command(help="Makes it die and dumps all its files.", pass_context=True)
async def keepinventory(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
        return
    
    if config["backup"] == "backupChannelId (int, not a string)":
        await ctx.send("Please set up your backup channel in the config file!")
        return
    
    await ctx.send("Goodbye for now. <3")
    channel = discord.utils.get(ctx.guild.channels, id=config["backup"])
    for f in lists["files"]:
        await channel.send(file=discord.File(f))
    exit("All done!")

# Exit without file dump
@bot.command(help="Makes it die.", pass_context=True)
async def kill(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
        return
    await ctx.send("Goodbye for now. <3")
    exit("All done!")

# Delete a team
@bot.command(help="Removes a team from the server and database", pass_context=True)
async def removeteam(ctx, *, team=''):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
    
    elif team == '':
        await ctx.send("Please list a team name to remove.")
    
    else:
        team = team.lower()
        await ctx.send(Data.removeTeam(team))
        channel = discord.utils.get(ctx.guild.channels, name=team.replace(" ", "-"))
        await channel.delete()
        role = discord.utils.get(ctx.guild.roles, name=team)
        await role.delete()

# Scoreboard Generation
@bot.command(help="Formats the scoreboard with the most up to date information", pass_context=True)
async def scoreboard(ctx):
    if config["scoreboard"] == ["list of valid scoreboard channels (ints, not strings)"]:
        await ctx.send("Please set up your scoreboard channels in the config file!")
        return

    if ctx.message.channel.id not in config["scoreboard"]:
        await ctx.send("Looks like this isn't the right channel for that, try again in the correct location!")
        return
    
    scores = "```" + Data.scoreBoard() + "```"

    embedded = discord.Embed(title = "LeaderBoard", description=scores, color = 0xF1C40F)
    await ctx.send(embed=embedded)

# Send the list of teams
@bot.command(help="View the full list of teams", pass_context=True)
async def teamlist(ctx):
    if discord.utils.get(ctx.guild.roles, name="@Sticker People") not in ctx.message.author.roles:
        await ctx.send(messages["noAccess"])
    
    else:
        await ctx.send(Data.printTeams())

'==========================================================================================================================================='
'Standard User Commands'

# Sticker code input
@bot.command(help="Submit a code you have found: <name> <key>", pass_context=True)
async def code(ctx, codeword='', key=''):
    team = ctx.message.channel

    if team.name not in Data.getTeams():
        await ctx.send(messages["validMessage"])
        return

    if codeword == '' or key == '':
        await ctx.send("Invalid input, make sure you input is in format `!code <sticker> <authCode>")
        return

    await ctx.send(Data.addSticker(ctx.channel.name, codeword, key))

# Creates a new team and adds the founding member 
@bot.command(help="Create a new team!", pass_context=True)
async def createteam(ctx,*,role_name=''):
    if role_name == '':
        await ctx.send("Please list a team name to create.")
        return
    while "  " in role_name:
        role_name = role_name.replace("  ", " ")
    
    # role_name = "".join([x for x in role_name if x.isascii()]).lower()
    
    # Getting the Command Users ID
    author = ctx.author 
    guild = ctx.guild               # server name 

    # check if that role already exists
    check_for_duplicate = get(ctx.message.guild.roles, name=role_name)

    if check_for_duplicate == None: # if the role doesn't exist
        # create the role and store role id in authorize role!
        authorize_role  = await guild.create_role(name=role_name, colour=discord.Colour(0x0000FF))

        sPeople =  discord.utils.get(guild.roles, name="@Sticker People")

        # Overwrites is a list of commands to send to the guild to change permissions
        overwrites = {
        # normies just joining cant see it!
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        # guild.me is the bot so it keeps the bot from taking commands in new channel
        guild.me: discord.PermissionOverwrite(read_messages=True), 
        guild.me: discord.PermissionOverwrite(send_messages=True), 
        # People with a specific role can see it
        authorize_role: discord.PermissionOverwrite(read_messages=True)
        }

        newChan = await guild.create_text_channel(role_name, overwrites=overwrites)

        await newChan.set_permissions(authorize_role, send_messages=True, read_messages = True)
        await newChan.set_permissions(sPeople, send_messages=True, read_messages = True)

        # Adding Team Creator to Role and Team chat!
        
        await author.add_roles(authorize_role) # adds the role to the user

        # Dming the New Chat with info!

        descript = (messages["newTeamMessage"])
        embedmessage=discord.Embed(title=f"Welcome to the {role_name}'s Teams DM", description=descript, color=0x5bcdee)
        embedmessage.set_footer(text="Good Luck!")
        
        await newChan.send(embed=embedmessage)  # Sends DM to Channel

        Data.addTeam(role_name)

        team_channel_id = newChan.id
        await ctx.send("Your shiny new team awaits you! <#{}>".format(team_channel_id))
        
    else: # TEAM ALREADY EXISTS BREAK OFF!
        await ctx.send(f"This team/role already exists try another name!")  # Checks for error!

# Help function WORK ON THIS
@bot.command(help="The worse help function", pass_context=True)
async def help(ctx):
    await ctx.send(messages["helpMessage"])

# Outputs hints
@bot.command(help='Request a hint, as well as viewing your current hints.',pass_context=True)
async def hint(ctx):
    team = ctx.message.channel

    if team.name not in Data.getTeams():
        await ctx.send(messages["validMessage"])
        return

    await ctx.send(Data.getHint(team.name))

# Adds user to an existing team
@bot.command(help="Join a preexisting team", pass_context=True)
async def jointeam(ctx, roleName=''):
    if roleName == '':
        await ctx.send("Please list a team name to join.")
        return

    forbiddenRoles = lists["forbidden"]
    if roleName in forbiddenRoles:
        await ctx.send("Don't worry, we're smarter than that.")
        return

    author = ctx.message.author # grabs the member id that used command
    if any(role.name == roleName for role in author.roles):
        await ctx.send("You already have a team! Contact a Sticker Person.")

    else:
        roleToAdd = discord.utils.get(ctx.guild.roles, name=roleName)
        if(roleToAdd == None):
            await ctx.send("This is not a role!")
            
        else:
            await ctx.author.add_roles(roleToAdd)
            await ctx.send("Role has been added!")

# Outputs score
@bot.command(help="Displays your team's score", pass_context=True)
async def score(ctx):
    await ctx.send(Data.printScoreAndCount(ctx.message.channel.name))

'==========================================================================================================================================='

bot.run(TOKEN) # end of bot
