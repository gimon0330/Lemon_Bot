import discord, json
from discord.ext import commands 

class assacinate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="암살")
    async def assacinate(self, ctx, user: discord.Member, *, arg): #user: discord.Member를 통해 멘션되는 유저를 받아 올수 있음. (Member 객체)
        await ctx.send(user.name,"님을 죽였습니다.\n사인 : ",arg)         #def a(*, arg) 로 arg에 뛰어쓰기 무시하고 받는 인자 싹다 str로받아옴.

    
def setup(client):
    client.add_cog(assacinate(client))

