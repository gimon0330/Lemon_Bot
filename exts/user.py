import json, discord, random, typing, datetime
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
                embed.add_field(name="봇 권한", value=self.pool[str(user.id)]["permission"])
        await ctx.send(embed=embed)
        
    @commands.command(name = "돈")
    async def user_money_check(self, ctx):
        await ctx.send(str(self.client.pool[str(ctx.author.id)]["money"]) + "원")

    @commands.command(name = "은행")
    async def user_bank_check(self, ctx):
        await ctx.send(str(self.client.pool[str(ctx.author.id)]["bank"]) + "원")

    @commands.command(name = "저금")
    async def user_bank_in(self, ctx):
        self.client.pool[str(ctx.author.id)]["bank"] += self.client.pool[str(ctx.author.id)]["money"]
        self.client.pool[str(ctx.author.id)]["money"] = 0
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 저금되었습니다")
    
    @commands.command(name = "출금")
    async def user_bank_out(self, ctx):
        self.client.pool[str(ctx.author.id)]["money"] += self.client.pool[str(ctx.author.id)]["bank"]
        self.client.pool[str(ctx.author.id)]["bank"] = 0
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
        await ctx.send("성공적으로 출금되었습니다")

    @commands.command(name = "돈내놔")
    async def user_givemoney(self, ctx):
        if self.client.pool[str(ctx.author.id)]["money"] >= 100:
            await ctx.send("작작해 이자식아")
        elif self.client.pool[str(ctx.author.id)]["money"] < 0:
            await ctx.send("여기 빚쟁이가 돈 뺏어가요 엉엉")
        else:
            self.client.pool[str(ctx.author.id)]["money"] += 100
            with open("./config/user.json", "w", encoding='utf-8') as db_json:
                db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            await ctx.send("100원 입금 완료")
    
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
            
    @reinforce.command(name = "레벨")
    async def level(self, ctx):
        if str(ctx.author.id) in self.client.pool.keys():
            lev = self.client.pool[str(ctx.author.id)]["reinforce"]
            await ctx.send("현재 레벨은 %d" %lev)
        else:
            await ctx.send("가입부터 하고 와주세요")

def setup(client):
    client.add_cog(user(client))