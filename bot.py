import discord
from discord.ext import commands
import json
import logging
import re
import asyncio

''' 
	Global regex strings for each of the known key types
'''
gog      = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
steamOne = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
steamTwo = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
ps3      = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
uplayOne = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
uplayTwo = '^[a-z,A-Z,0-9]{3}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
origin   = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
url      = '^http'

'''
	Description for the help command
'''
description = '''A bot that allows for the addition, retrieval, and storage of game keys in a json database for members to share with eachother.

Written by @TheSlowHipster
'''

# Log to a file
logging.basicConfig(level=logging.INFO,filename="discord.log")

# Open the proper json files for config and the database
with open("conf.json") as f:
	config = json.load(f)

with open(config["DbFile"]) as f:
	games = json.load(f)

# Set the intents and default options for @bot.command()
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=config["Prefix"], description=description, intents=intents)

# Function that updates the json database
def write_json(data, filename=config["DbFile"]):
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)



'''
	Actual Bot Functionality
'''
# List all the keys in the database as a series of embeds
@bot.command(aliases=["listkeys","list", "keys","Keys"], description="List all games in the database")
async def listKeys(ctx):
	count = 0
	gms = list(games.keys())
	while count < len(games.keys()):
		max = 20
		if count + max >= len(games.keys()):
			max = len(games.keys())-count
		embed = discord.Embed(
			title = "Current Key List",
			description = f"Games {count+1} to {count+max}"
		)
		for i in range(20):
			if count >= len(gms):
				break
			game = gms[count]
			embed.add_field(name=f"{games[game][0]['GameName']}",value=f'Platform : {games[game][0]["ServiceType"]}\nKeys Available : {len(games[game])}',inline=False)
			count += 1
			
			
		await ctx.author.send(embed=embed)

# Add a key to the database
@bot.command(usage="Prompts you for a game name and key to be added to the database.", aliases=["add","addkey","Addkey","AddKey","addGame","addgame","AddGame","Addgame"], description="Add a game key to the database")
async def addKey(ctx):
	# if at least one argument provided
	ack_0 = await ctx.send("What is the name of the game you want to send?")

	def get_gameName(m):
		return m.author == ctx.author and m.channel == ctx.channel

	info = await bot.wait_for('message', check=get_gameName)
	name = info.content
	game = info.content.replace(" ","").lower()
	ack_1 = await ctx.send(f"Awesome! What is the key associated with that game?")

	def get_serial(m):
		return m.author == ctx.author and m.channel == ctx.channel

	msg = await bot.wait_for('message', check=get_serial)
	serial = msg.content
	if re.match(gog,serial) != None:
		serv = "GoG"
	elif re.match(steamOne,serial) != None or re.search(steamTwo,serial) != None:
		serv = "Steam"
	elif re.match(ps3,serial) != None:
		serv = "PS3"
	elif re.match(uplayOne,serial) != None or re.search(uplayTwo,serial) != None:
		serv = "Uplay"
	elif re.match(origin,serial) != None:
		serv = "Origin"
	elif re.match(url,serial) != None:
		serv = "Web"
	else:
		await ctx.send(f"{ctx.author.name}, I don't recognize that key format, please try again")
		return
		
	auth = ctx.author.name
	
	
	tmp = {
			"Author"      : auth,
			"GameName"    : name,
			"Serial"      : serial,
			"ServiceType" : serv
		}
	if game not in games.keys():
		games[game] = [tmp]
	else:
		games[game].append(tmp)
	write_json(games)
	await ctx.send(f"{ctx.author.name} added a {serv} Key for {name}!")
	if not isinstance(ctx.channel, discord.channel.DMChannel):
		await msg.delete()
		await ack_1.delete()
		await info.delete()
		await ack_0.delete()
		await ctx.message.delete()
	else:
		await ctx.send(f"I do not currently have the ability to delete messages in a DM channel, but I have stored your key! So you don't try to use it later please delete your message.")

# Pop the desired key from the database
@bot.command(usage=f"Take a key from the database.", aliases=["take","takekey","TakeKey","takeGame","takegame","TakeGame"], description="Allows you to take a key from the database")
async def takeKey(ctx):
	ack_0 = await ctx.send("What game do you want to take?")
	
	def get_gameName(m):
		return m.author == ctx.author and m.channel == ctx.channel
	
	info = await bot.wait_for('message', check=get_gameName)

	game = info.content.replace(" ","").lower()
	name = info.content

	await ctx.send(f"Searching for `{game}`")

	if game not in games.keys():
		await ctx.send(f"I'm sorry {ctx.author.name}, I couldn't find a key for {name}.")
	else:
		await ctx.send(f"Have fun with your key for {name}, {ctx.author.name}!")
		tmp = games[game].pop()
		embed = discord.Embed(
			title = f"{tmp['GameName']}",
			description = f"Provided by: {tmp['Author']}"
		)
		embed.add_field(name = f"Key: {tmp['Serial']}", value= f"Store: {tmp['ServiceType']}")
		await ctx.author.send(embed=embed)
		if len(games[game]) == 0:
			del games[game]
		write_json(games)

# Search for a desired game in the database
@bot.command(usage=f"Search the database for a game.", aliases=["search","Search","Searchkey","SearchKey"], description="Searches for a specific game in the database")
async def searchKey(ctx):
	ack_0 = await ctx.send("What game are you looking for?")
	
	def get_gameName(m):
		return m.author == ctx.author and m.channel == ctx.channel
	
	info = await bot.wait_for('message', check=get_gameName)

	game = info.content.replace(" ","").lower()
	name = info.content

	if game not in games.keys():
		await ctx.send(f"I'm sorry {ctx.author.name}, I couldn't find any keys for {name}.")
	else:
		embed = discord.Embed(
			title = f"Keys found for: {name}",
			description = f"{len(games[game])} keys found for {name}"
		)
		servs = {}
		for key in games[game]:
			if key["ServiceType"] not in servs.keys():
				servs[key["ServiceType"]] = 1
			else:
				servs[key["ServiceType"]] += 1
		for service in servs.keys():
			embed.add_field(name=f"{service}",value=f"{servs[service]} keys found")
		await ctx.send(embed=embed)
		

bot.run(config["Token"])