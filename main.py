import discord, os, json
from discord.ext import commands

client = commands.AutoShardedBot(command_prefix=["ㄹ!","레몬아 ",'레 ',"f!"])

user_datadb = {}
with open("./data/user.json", "r", encoding='UTF8') as db_json:  
    user_datadb = json.load(db_json)
with open("./data/guild.json", "r", encoding='UTF8') as db_json:  
    guild_datadb = json.load(db_json)
    
client.pool = user_datadb
client.guilddb = guild_datadb
client.yes_emoji = "<a:ok:1001365881160466472>"
client.no_emoji = "<a:no:1001365885426073690>"

for ext in filter(lambda x: x.endswith('.py') and not x.startswith('_'), os.listdir('./exts')):
    client.load_extension('exts.' + os.path.splitext(ext)[0])

client.run("Token")
