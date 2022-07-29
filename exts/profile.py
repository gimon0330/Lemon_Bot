import discord, json, typing, datetime, asyncio
from discord.ext import commands 
from utils import errors, checks

def get_embed(title, description='', color=0xf4fa72): 
    return discord.Embed(title=title,description=description,color=color)

class profile(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        self.checks = checks.checks(self.pool)
        
        self._profile_setup.add_check(self.checks.registered)

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
        embcolor = self.pool[str(user.id)]["profile"]["color"]
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
                if self.pool[str(user.id)]["profile"]["money_open"]:
                    reinlist = [k for k, v in self.pool[str(user.id)]["reinforce"].items() if v["level"] >= 100]
                    embed.add_field(
                        name="Lemon System", 
                        value=f">>> **Permission**: {self.pool[str(user.id)]['permission']}\n" +
                        ("\n**블랙리스트에 등재된 유저입니다!**" if self.pool[str(user.id)]['blacklist'] else 
                        f"**Money**: {self.pool[str(user.id)]['money']}원\n" + 
                        f"**bank**: {self.pool[str(user.id)]['bank']}원\n" + 
                        f"**100레벨 이상 강화 아이템 갯수** : {len(reinlist)}개\n{','.join(reinlist)}")
                    )
                else:
                    embed.add_field(
                        name = "Lemon System", 
                        value = "프로필 비공개 유저입니다!"
                    )
        await ctx.send(embed=embed)
        
    @_profile.command(name = "설정")
    async def _profile_setup(self, ctx):
        color = hex(self.pool[str(ctx.author.id)]["profile"]["color"])
        show = "공개" if self.pool[str(ctx.author.id)]["profile"]["money_open"] else "비공개"
        msg = await ctx.send(embed=get_embed("⚙️ | 프로필 설정",f"✏️ : 프로필 색 변경 (현재 색 {color})\n🔍 : 프로필 비공개 설정 (현재 {show})"))
        emjs=["✏️", "🔍"]
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
            if e == "✏️":
                
                await ctx.send(f"프로필 카드 색을 변경합니다!\n현재 색은 **{color}**입니다.\n변경할 색을 **0x를 붙인 HEX코드로** 적어주세요!")
                
                def check(author):
                    def inner_check(message): 
                        if message.author != author: return False
                        else: return True
                    return inner_check
                
                try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
                except asyncio.TimeoutError: 
                    self.gaming_list.remove(ctx.author.id)
                    await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000))
                    return
                else: 
                    n = msg.content
                    if n == str(hex(n)):
                        color = self.pool[user.id]["profile"]["color"]
                        await ctx.send(f"프로필 카드 색을 {color}로 변경하였습니다!")
                        
            elif e == "🔍":
                await ctx.send("프로필을 비공개로 변경합니다!")
            

def setup(client):
    client.add_cog(profile(client))

