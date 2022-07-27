import discord, os, json
from discord.ext import commands

client = commands.AutoShardedBot(command_prefix="ㄹ!")

user_datadb = {}
with open("./config/user.json", "r", encoding='UTF8') as db_json:  
    user_datadb = json.load(db_json)
    
client.pool = user_datadb

for ext in filter(lambda x: x.endswith('.py') and not x.startswith('_'), os.listdir('./exts')):
    client.load_extension('exts.' + os.path.splitext(ext)[0])

client.run("NzUxNjYwNTc2NTg5MjE3ODkz.G7r47R.l-6iZZOM54oitPNB1ER2f3lDD-kDQrDSg1HP9A")