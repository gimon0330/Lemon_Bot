import json, discord, random, typing, datetime, asyncio
from discord.ext import commands
from utils import errors, checks

def get_embed(title, description='', color=0xf4fa72): 
    return discord.Embed(title=title,description=description,color=color)

class user(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        
        self.checks = checks.checks(self.pool)
        
        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)
            
    @commands.command(name = "탈퇴")
    async def user_exit(self, ctx):
        del self.client.pool[str(ctx.author.id)]
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 탈퇴되었습니다")
        
    @commands.command(name = "프로필")
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
        embed = discord.Embed(title=f"👤 | **{user.name} 님의 프로필**", description=("" if user.name == user.display_name else f"**서버내 닉네임**: {user.display_name}\n") + f'**유저 ID**: {user.id}\n**현재 상태**: {sta}',color=0xCCFFFF)
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
                reinlist = [k for k, v in self.pool[str(user.id)]["reinforce"].items() if v >= 30]
                embed.add_field(
                    name="Lemon System", 
                    value=f">>> **Permission**: {self.pool[str(user.id)]['permission']}\n" +
                    ("\n**블랙리스트에 등재된 유저입니다!**" if self.pool[str(user.id)]['blacklist'] else 
                    f"**Money**: {self.pool[str(user.id)]['money']}원\n" + 
                    f"**bank**: {self.pool[str(user.id)]['bank']}원\n" + 
                    f"**30레벨 이상 강화 아이템 갯수** : {len(reinlist)}개\n{','.join(reinlist)}")
                )
        await ctx.send(embed=embed)
        
    @commands.command(name = "돈")
    async def user_money_check(self, ctx, user: typing.Optional[discord.Member] = None):
        if not user: user = ctx.author
        if str(user.id) not in self.pool.keys(): raise errors.NotRegistered
        
        money = self.pool[str(user.id)]["money"]
        
        if money < 10000 ** 10:
            suffix=['','만', '억', '조', '경', '해', '자', '양', '구', '간', '정', '재']
            a=10000 ** 12
            str_result = ''
            for i in range(0,13):
                if money >= a:
                    str_result += f"{int(money // a)}{suffix[-i]} "
                    money = money % a
                a=a//10000
            money = str_result.strip()
            if not money: money = 0

        await ctx.send(embed=get_embed(f'💸 | {user} 님의 지갑',f"{money} 원"))

    @commands.command(name = "은행")
    async def user_bank_check(self, ctx):
        await ctx.send(str(self.client.pool[str(ctx.author.id)]["bank"]) + "원")

    @commands.group(name = "저금", invoke_without_command=True)
    async def user_bank_in(self, ctx, n: int):
        if n <= 0:
            await ctx.send(embed = get_embed("입력한 값이 너무 작습니다!","0을 초과하는 정수값을 입력해주세요!",0xFF0000))
            return
        if self.pool[str(ctx.author.id)]["money"] < n:
            await ctx.send(embed = get_embed("입력한 값이 너무 큽니다!","자신이 가진돈 이상 저금하실 수 없습니다!",0xFF0000))
            return
        self.client.pool[str(ctx.author.id)]["bank"] += n
        self.client.pool[str(ctx.author.id)]["money"] -= n
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 저금되었습니다")
        
    @user_bank_in.command(name='전체', aliases=['다','올인',"전부","최대"])
    async def user_bank_in_all(self, ctx):
        self.client.pool[str(ctx.author.id)]["bank"] += self.client.pool[str(ctx.author.id)]["money"]
        self.client.pool[str(ctx.author.id)]["money"] = 0
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 저금되었습니다")
    
    @commands.group(name = "출금", aliases = ["인출"], invoke_without_command=True)
    async def user_bank_out(self, ctx, n: int):
        if n <= 0:
            await ctx.send(embed = get_embed("입력한 값이 너무 작습니다!","0을 초과하는 정수값을 입력해주세요!",0xFF0000))
            return
        if self.pool[str(ctx.author.id)]["money"] < n:
            await ctx.send(embed = get_embed("입력한 값이 너무 큽니다!","자신이 가진돈 이상 저금하실 수 없습니다!",0xFF0000))
            return
        self.client.pool[str(ctx.author.id)]["bank"] += n
        self.client.pool[str(ctx.author.id)]["money"] -= n
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 출금되었습니다.")
        
    @user_bank_out.command(name='전체', aliases=['다','올인',"전부","최대"])
    async def user_bank_out_all(self, ctx):
        self.client.pool[str(ctx.author.id)]["money"] += self.client.pool[str(ctx.author.id)]["bank"]
        self.client.pool[str(ctx.author.id)]["bank"] = 0
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 출금되었습니다")

    @commands.command(name = "돈내놔")
    async def user_givemoney(self, ctx):
        if self.client.pool[str(ctx.author.id)]["money"] >= 10000:
            await ctx.send("작작해 이자식아")
        elif self.client.pool[str(ctx.author.id)]["money"] < 0:
            await ctx.send("여기 빚쟁이가 돈 뺏어가요 엉엉")
        else:
            self.client.pool[str(ctx.author.id)]["money"] += 10000
            with open("./config/user.json", "w", encoding='utf-8') as db_json:
                db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            await ctx.send("10000원 입금 완료")
            
    @commands.command(name='송금', aliases=['입금'])
    @commands.guild_only()
    async def _give_money(self, ctx, muser: discord.Member, n: int):
        if muser == ctx.author:
            await ctx.send(embed=get_embed("<a:no:1001365885426073690> | 본인에게 송금은 불가합니다.","다른 사람을 멘션해주세요",0xff0000))
            return
        if n <= 0:
            await ctx.send(embed = get_embed("입력한 값이 너무 작습니다!","0을 초과하는 정수값을 입력해주세요!",0xFF0000))
            return
        if self.pool[str(ctx.author.id)]["money"] < n:
            await ctx.send(embed = get_embed("입력한 값이 너무 큽니다!","자신이 가진돈 이상 저금하실 수 없습니다!",0xFF0000))
            return
        try: sendmoney = int(n ** (3/4))
        except OverflowError: 
            await ctx.send(embed=get_embed("<a:no:1001365885426073690> | 돈이 너무 커서 송금이 불가합니다.","더 작은수를 입력해주세요.",0xff0000))
            return
        if str(muser.id) not in self.pool.keys(): raise errors.NotRegistered
        msg = await ctx.send(embed=get_embed("📝 | **송금**",f"**{ctx.author}**님이 **{muser}**님에게 송금\n**전송되는 금액 (수수료 차감)** = {sendmoney} (수수료 = {n - sendmoney})"))
        emjs=['<a:ok:1001365881160466472>','<a:no:1001365885426073690>']
        for em in emjs: await msg.add_reaction(em)
        def check(reaction, user): return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try: reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=20)
        except asyncio.TimeoutError: await asyncio.gather(msg.delete(), ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
        else:
            e = str(reaction.emoji)
            if e == '<a:ok:1001365881160466472>':
                self.client.pool[str(ctx.author.id)]["money"] -= n
                self.client.pool[str(muser.id)]["money"] += sendmoney
                await ctx.send(embed=get_embed(f"{ctx.author.name}님이 {muser.name}님에게 송금하셨습니다",f"송금 금액 : {n}\n{ctx.author}님의 남은 금액 : {self.client.pool[str(ctx.author.id)]['money']}\n\n받은 금액 (수수료 차감) : {sendmoney} (수수료 = {n - sendmoney})\n{muser}님의 남은 금액 : {self.client.pool[str(muser.id)]['money']}"))
                return
            elif e == '<a:no:1001365885426073690>':
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('<a:no:698461934613168199> | 취소 되었습니다!',"", 0xFF0000)))
                return
    
    @commands.group(name = "도박", invoke_without_command=True)
    async def lottery(self, ctx, n):
        try: n = int(n)
        except:
            await ctx.send(embed = get_embed("입력한 값이 올바른지 확인해주세요!","0을 초과하고 자신이 가진 돈의 10분의 1을 넘지않는 정수값을 입력해주세요!",0xFF0000))
            return
        if self.pool[str(ctx.author.id)]["money"] // 10 < n:
            await ctx.send(embed = get_embed("입력한 값이 너무 큽니다!","자신이 가진돈의 10분의 1이상 사용하실 수 없습니다!",0xFF0000))
            return
        elif 0 >= n:
            await ctx.send(embed = get_embed("입력한 값이 너무 작습니다!","0을 초과하는 값을 입력해주세요!",0xFF0000))
            return
        a = random.randint(-8, 8)
        self.pool[str(ctx.author.id)]["money"] = self.client.pool[str(ctx.author.id)]["money"] + a * n
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send(f"{a}배!\n남은 돈은 {self.pool[str(ctx.author.id)]['money']}원 입니다!")
            
    @lottery.command(name = "올인")
    async def all_in(self, ctx):
        a = random.randint(-6,10)
        if a <= 0:
            a = 0
            await ctx.send("도박 실패...\n남은돈은 0원 입니다!")
        else: 
            await ctx.send(str(a)+"배!")
        self.client.pool[str(ctx.author.id)]["money"] = self.client.pool[str(ctx.author.id)]["money"] * a
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            
    @commands.command(name = "환전")
    async def change_money(self, ctx):
        await ctx.send("환전되었습니다.")
        self.client.pool[str(ctx.author.id)]["money"] = 0
        await ctx.send("예기치 못한 오류로 인해 송금 과정에서 오류가 났습니다.")
            
    @commands.group(name = "강화", invoke_without_command = True)
    async def reinforce(self, ctx, name):
        a = random.randint(1,100)
        b = random.randint(1,10)
        if name not in self.client.pool[str(ctx.author.id)]["reinforce"]:
            await ctx.send(embed = get_embed(f"{name}는 "))
        lev = self.client.pool[str(ctx.author.id)]["reinforce"]["name"]
        if a == 1:
            await ctx.send("파괴되었습니다 ㅅㄱㅋ")
            self.client.pool[str(ctx.author.id)]["reinforce"] = 0
            with open("./config/user.json", "w", encoding='utf-8') as db_json:
                db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        elif a>1 and a<=20:
            if lev < b:
                await ctx.send("강화에 실패하여 0렙으로 되돌아왔습니다.")
                self.client.pool[str(ctx.author.id)]["reinforce"] = 0
                with open("./config/user.json", "w", encoding='utf-8') as db_json:
                    db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            else:
                await ctx.send("강화에 실패하여 %d 만큼 하락했습니다" %b)
                self.client.pool[str(ctx.author.id)]["reinforce"] -= b
                with open("./config/user.json", "w", encoding='utf-8') as db_json:
                    db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        else:
            await ctx.send("성공! %d 만큼 레벨 상승!" %b)
            self.client.pool[str(ctx.author.id)]["reinforce"] += b
            with open("./config/user.json", "w", encoding='utf-8') as db_json:
                db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            
    @reinforce.command(name = "목록")
    async def level(self, ctx):
        reinlist = [f"**Lv{v}** {k}" for k, v in self.pool[str(ctx.author.id)]["reinforce"].items()]
        await ctx.send(embed=get_embed(f"🛠️ | {ctx.author.name}님의 강화목록입니다. (총 {len(reinlist)}개)", "\n".join(reinlist)))

def setup(client):
    client.add_cog(user(client))