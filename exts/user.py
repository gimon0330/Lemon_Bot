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
            await ctx.send(embed=get_embed(self.client.no_emoji + " | 본인에게 송금은 불가합니다.","다른 사람을 멘션해주세요",0xff0000))
            return
        if n < 100:
            await ctx.send(embed = get_embed(self.client.no_emoji + " | 입력한 값이 너무 작습니다!","100이상의 정수값을 입력해주세요!",0xFF0000))
            return
        if self.pool[str(ctx.author.id)]["money"] < n:
            await ctx.send(embed = get_embed(self.client.no_emoji + " | 입력한 값이 너무 큽니다!","자신이 가진돈 이상 저금하실 수 없습니다!",0xFF0000))
            return
        try: sendmoney = int(n ** (3/4))
        except OverflowError: 
            await ctx.send(embed=get_embed(self.client.no_emoji + " | 돈이 너무 커서 송금이 불가합니다.","더 작은수를 입력해주세요.",0xff0000))
            return
        if str(muser.id) not in self.pool.keys(): raise errors.NotRegistered
        msg = await ctx.send(embed=get_embed("📝 | **송금**",f"**{ctx.author}**님이 **{muser}**님에게 송금\n**전송되는 금액 (수수료 차감)** = {sendmoney}원 (수수료 = **{n - sendmoney}원**)"))
        emjs=[self.client.yes_emoji, self.client.no_emoji]
        for em in emjs: await msg.add_reaction(em)
        def check(reaction, user): return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try: reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=20)
        except asyncio.TimeoutError: await asyncio.gather(msg.delete(), ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
        else:
            e = str(reaction.emoji)
            if e == self.client.yes_emoji:
                self.client.pool[str(ctx.author.id)]["money"] -= n
                self.client.pool[str(muser.id)]["money"] += sendmoney
                await ctx.send(embed=get_embed(f"{ctx.author.name}님이 {muser.name}님에게 송금하셨습니다",f"송금 금액 : {n}\n{ctx.author}님의 남은 금액 : {self.client.pool[str(ctx.author.id)]['money']}\n\n**받은 금액 (수수료 차감)** = {sendmoney}원 (수수료 = **{n - sendmoney}원**)\n{muser}님의 남은 금액 : {self.client.pool[str(muser.id)]['money']}"))
                return
            elif e == self.client.no_emoji:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed(self.client.no_emoji + ' | 취소 되었습니다!',"", 0xFF0000)))
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
            
    @commands.group(name='강화', aliases=['강'], invoke_without_command=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _reinforce(self, ctx, *, weapon):
        user = ctx.author.id
        if not weapon:
            await ctx.send("알티야 강화 (이름)의 형식으로 사용해주세용")
            return
        
        if weapon not in self.client.pool[str(user)]["reinforce"].keys():
            if self.client.pool[str(user)]["reinforce"].keys().__len__() > 30:
                await ctx.send("무기 제작은 최대 30개만 가능합니다!")
                return
                
            msg = await ctx.send(embed=get_embed(":hammer: | 무기 제작","새로운 무기를 제작합니다!\n가격은 {Null}입니다!\n제작하시겠습니까?"))
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    level = self.client.pool[str(user.id)]["reinforce"][weapon] = {
                        "level": 0,
                        "starforce": 0,
                        "broken": False
                    }
                    await ctx.send(embed=get_embed(":hammer: | 무기 제작","제작 완료했습니다! 다시 강화를 눌러 강화해주세요!"))
                    return
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed("{self.client.no_emoji} | 취소 되었습니다.","",0xff0000))
                    return
                
        level = self.client.pool[str(user)]["reinforce"][weapon]["level"]
        
        if level >= 100:
            msg = await ctx.send(embed=get_embed(":star: | 스타 강화","100렙을 넘으셔서 특수강화 도전을 하실수 있습니다.\n성공 : 30%\n강화 실패 : 50%\n파괴 : 20%\n도전 하시겠습니까?"))
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    rand = random.randint(0,9)
                    starforce = self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"]
                    if rand < 3:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] += 1
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon}의 스타가 **1레벨** 성장했습니다.",f"현재 레벨 : **{starforce+1}**"))
                        return
                    elif rand < 7:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] -= 1
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon}의 스타가 **1레벨** 하락했습니다.",f"현재 레벨 : **{starforce}**",0xff0000))
                        return
                    else:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] = 0
                        self.client.pool[str(user.id)]["reinforce"][weapon]["broken"] = True
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | {weapon} (이)가 파괴되었습니다.","",0xff0000))
                        return
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed("{self.client.no_emoji} | 취소 되었습니다.","",0xff0000))
                    return
        else:
            msg = await ctx.send(embed=get_embed(":hammer: | 기본 강화","강화에 도전합니다!\n가격은 무료입니다!\n\n성공 : 70% (2~15 레벨 랜덤 오름)\n실패 : 30% (실패시 파괴)\n도전 하시겠습니까?"))
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    rand = random.randint(0,9)
                    if rand < 7:
                        n = random.randint(5,20)
                        self.client.pool[str(user.id)]["reinforce"][weapon]["level"] += n
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon} (이)가 **{n}레벨** 성장했습니다.",f"현재 레벨 : **{level+n}**"))
                        return
                    else:
                        del self.client.pool[str(user.id)]["reinforce"][weapon]
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | {weapon} (이)가 파괴되었습니다.","",0xff0000))
                        return
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed("{self.client.no_emoji} | 취소 되었습니다.","",0xff0000))
                    return
            
    @_reinforce.command(name = "목록")
    async def level(self, ctx):
        reinlist = [f"**Lv{v['level']}** {':star:' * v['starforce']} {k}" for k, v in self.pool[str(ctx.author.id)]["reinforce"].items()]
        await ctx.send(embed=get_embed(f"🛠️ | {ctx.author.name}님의 강화목록입니다. (총 {len(reinlist)}개)", "\n".join(reinlist)))

def setup(client):
    client.add_cog(user(client))