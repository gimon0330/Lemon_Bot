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
        
    @commands.command(name='정보')
    async def chat_info(self, ctx):
        embed = discord.Embed(title="🏷️ | **RT BOT**",description=f"RT BOT Made By **Th_Phec**\n> Made With Discord.py\n> Ver. Beta 3.5.0\n> Helpers. **None**\n**{len(self.client.guilds)}** SERVERS | **{len(self.client.users)}** USERS", color=0xCCffff)
        embed.set_footer(text="TEAM Infinite®️",icon_url='https://cdn.discordapp.com/icons/689375730483855389/89eb7bfc0dabc59dcda58e733818a4c5.webp?size=1024')
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    """@commands.command(name='핑')
    async def chat_ping(self, ctx):
        ping = [round(1000 * self.client.latency,2)]
        time_then = time.monotonic()
        pinger = await ctx.send(embed=get_embed('🏓 퐁!',f'**디스코드 지연시간: **{ping[0]}ms - {pinglev(ping[0])}\n\n**봇 메세지 지연시간**: Pinging..'))
        ping.append(round(1000*(time.monotonic()-time_then),2))
        await pinger.edit(embed=get_embed('🏓 퐁!',f'**디스코드 지연시간: **{ping[0]}ms - {pinglev(ping[0])}\n\n**봇 메세지 지연시간**: {ping[1]}ms - {pinglev(ping[1])}'))
"""


def setup(client):
    client.add_cog(inform(client)) 