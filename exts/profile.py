import discord, json, typing, datetime, asyncio
from discord.ext import commands 

def get_embed(title, description='', color=0xf4fa72): 
    return discord.Embed(title=title,description=description,color=color)

class profile(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool

    @commands.group(name = "프로필", invoke_without_command = True)
    async def _profile(self, ctx, user: typing.Optional[discord.Member] = None):
        if ctx.guild is None:
            await ctx.send(embed=get_embed("<a:no:698461934613168199> | 서버내에서만 사용가능한 명령어 입니다.",0xff0000))
            return
        if not user: user = ctx.author
        try:
            st = str(user.status)
            if st == "online": sta = ":green_circle: 온라인"
            elif st == "offline": sta = ":black_circle: 오프라인"
            elif st == "idle": sta = ":yellow_circle: 자리 비움"
            else: sta = ":no_entry: 방해 금지"
        except: sta = "불러오는데 실패"
        embcolor = self.pool[user.id]["profile"]["color"]
        embed = discord.Embed(title=f"👤 | **{user.name} 님의 프로필**", description=("" if user.name == user.display_name else f"**서버내 닉네임**: {user.display_name}\n") + f'**유저 ID**: {user.id}\n**현재 상태**: {sta}',color=embcolor)
        embed.set_thumbnail(url=user.avatar_url)
        date = datetime.datetime.utcfromtimestamp(((int(user.id) >> 22) + 1420070400000)/1000)
        embed.add_field(name="Discord 가입 일시", value=str(date.year) + "년 " + str(date.month) + "월 " + str(date.day) + "일 ")
        joat = user.joined_at.isoformat()
        embed.add_field(name="서버 가입 일시", value=joat[0:4]+'년 '+joat[5:7]+'월 '+joat[8:10]+'일')
        if user.bot:
            embed.add_field(name="봇 초대장 생성",value=f"[초대장](https://discord.com/oauth2/authorize?client_id={user.id}&scope=bot&permissions=0)")
        else:
            if user.guild_permissions.administrator: embed.add_field(name="서버 권한", value="Admin")
            else: embed.add_field(name="서버 권한", value="User")
            if str(user.id) in self.pool.keys():
                reinlist = [k for k, v in self.pool[str(user.id)]["reinforce"].items() if v["level"] >= 100]
                embed.add_field(
                    name="Lemon System", 
                    value=f">>> **Permission**: {self.pool[str(user.id)]['permission']}\n" +
                    ("\n**블랙리스트에 등재된 유저입니다!**" if self.pool[str(user.id)]['blacklist'] else 
                    f"**Money**: {self.pool[str(user.id)]['money']}원\n" + 
                    f"**bank**: {self.pool[str(user.id)]['bank']}원\n" + 
                    f"**100레벨 이상 강화 아이템 갯수** : {len(reinlist)}개\n{','.join(reinlist)}")
                )
        await ctx.send(embed=embed)
        
    @commands.command(name = "설정")
    async def _profile(self, ctx):
        msg = await ctx.send(embed=get_embed("⚙️ | 프로필 설정",""))
        emjs=[":pencil2:", ":mag_right:"]
        for i in emjs:
            await msg.add_reaction(i)
        def check(reaction, user):
            return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
            return
        else:
            e = str(reaction.emoji)
            if e == ":pencil2:":
                color = self.pool[user.id]["profile"]["color"]
                await ctx.send(f"프로필 카드 색을 변경합니다!\n현재 색은 **{color}**입니다.")
            elif e == ":mag_right:":
                await ctx.send("프로필을 비공개로 변경합니다!")
            

def setup(client):
    client.add_cog(profile(client))

