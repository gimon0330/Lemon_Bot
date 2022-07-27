import discord, traceback
from discord.ext import commands 
from utils import checks

class admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        self.checks = checks.checks(self.pool)

        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)
            cmds.add_check(self.checks.master)

    @commands.command(name="eval")
    async def _eval(self, ctx, *, arg):
        try: await ctx.send(embed=discord.Embed(title = '관리자 기능 - Eval', description = f"📤 OUTPUT```{eval(arg)}```", color = 0xf4fa72))
        except: await ctx.send(embed=discord.Embed(title = '관리자 기능 - Eval', description = f"📤 EXCEPT```{traceback.format_exc()}```", color = 0xFF0000))

    @commands.command(name="await")
    async def _await(self, ctx, *, arg):
        try: res = await eval(arg) 
        except: await ctx.send(embed=discord.Embed(title = '관리자 기능 - Await Eval',description = f"📤 EXCEPT```{traceback.format_exc()}```",color = 0xFF0000))
        else: await ctx.send(embed=discord.Embed(title = '관리자 기능 - Await Eval', description = f"📤 OUTPUT```{res}```", color = 0xf4fa72))
    
def setup(client):
    client.add_cog(admin(client))