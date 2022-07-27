import discord, json
from discord.ext import commands 
from utils import errors, checks

class join(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        

    @commands.command(name = "가입")
    async def user_join(self, ctx):
        if str(ctx.author.id) in self.client.pool.keys():
            await ctx.send("이미 가입되어 있습니다")
            return
            
        self.client.pool[str(ctx.author.id)] = {
            "money": 0,
            "bank": 0,
            "reinforce": {},
            "blacklist": True,
            "permission": "User"
        }
        
        if ctx.author.id == 467666650183761920:
            self.client.pool[str(ctx.author.id)]["permission"] = "Master"
        
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 가입 되었습니다")
    
def setup(client):
    client.add_cog(join(client))
