import discord
from discord.ext import commands
import json
import logging
import re

gog      = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
steamOne = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
steamTwo = '^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$'
ps3      = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
uplayOne = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
uplayTwo = '^[a-z,A-Z,0-9]{3}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
origin   = '^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$'
url      = '^http'



description = '''A bot that allows for the addition, retrieval, and storage of game keys
in a json database for members to share with eachother.'''

logging.basicConfig(level=logging.INFO,filename="discord.log")

with open("conf.json") as f:
	config = json.load(f)

with open(config["DbFile"]) as f:
	games = json.load(f)

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

def write_json(data, filename=config["DbFile"]):
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)

@bot.command()
async def listkeys(ctx):
	count = 0
	gms = list(games.keys())
	while count < len(games.keys()):
		embed = discord.Embed(
			title = "Current Key List",
			description = f"Games {count} to {count+20}"
		)
		for i in range(20):
			if count >= len(gms):
				break
			game = gms[count]
			embed.add_field(name=f"{games[game][0]['GameName']}",value=f'Platform : {games[game][0]["ServiceType"]}\nKeys Available : {len(games[game])}',inline=False)
			count += 1
			
			
		await ctx.author.send(embed=embed)

@bot.command()
async def addKey(ctx, *args):
	serial = args[len(args)-1]
	auth = ctx.author.name
	name = ""
	game = ""
	for word in args[:len(args)-1]:
		name += word + " "
		game += word
	name = name[:len(name)-1]
	game = game.lower()
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
		serv = "Unknown"
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
	await ctx.message.delete()

bot.run(config["Token"])