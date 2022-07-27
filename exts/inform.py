import discord
from discord.ext import commands 

class inform(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "초대장")
    async def invite_(self, ctx):
        embed = discord.Embed(title = "레몬봇 초대링크",description="https://discord.com/oauth2/authorize?&client_id=715919815616757901&scope=bot+applications.commands&permissions=37014592",color=0xf4fa72)
        await ctx.send(embed=embed)
    
    @commands.command(name = "도움")
    async def _help(self, ctx):
        embed = discord.Embed(title = "레몬봇 도움", description = "레몬 멍청이", color = 0xf4fa72)
        await ctx.send(embed = embed)

    @commands.command(name = "서버")
    async def _servers(self, ctx):
        des = ""
        for i in self.client.guilds:
            des += f"**{len(i.members)}** {i.name}\n"
        await ctx.send(embed = discord.Embed(title = "레몬봇 서버", description = des, color = 0xf4fa72))


def setup(client):
    client.add_cog(inform(client)) 