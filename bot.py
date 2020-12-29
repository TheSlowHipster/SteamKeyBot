import discord
import json

with open("conf.json") as f:
	config = json.load(f)

with open(config["DbFile"]) as f:
	keys = json.load(f)

client = discord.Client()

@client.event
async def on_ready():
	print(f"Logged in as {user}")

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content.startsWith('$hello'):
		await message.channel.send('Hello!')

client.run(config["Token"])