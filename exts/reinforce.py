import json, discord, random, typing, asyncio
from discord.ext import commands
from utils import errors, checks
from math import trunc

def get_embed(title, description='', color=0xf4fa72): 
    return discord.Embed(title=title,description=description,color=color)

class reinforce(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pool = self.client.pool
        
        self.checks = checks.checks(self.pool)
        
        for cmds in self.get_commands():
            cmds.add_check(self.checks.registered)

    @commands.group(name='강화', aliases=['강'], invoke_without_command=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _reinforce(self, ctx, *, weapon):
        user = ctx.author.id
        if not weapon:
            await ctx.send("ㄹ!강화 (이름)의 형식으로 사용해주세용")
            return
        
        if weapon not in self.client.pool[str(user)]["reinforce"].keys():
            if self.client.pool[str(user)]["reinforce"].keys().__len__() > 7:
                await ctx.send("무기 제작은 최대 8개만 가능합니다!")
                return
                
            msg = await ctx.send(embed=get_embed(":hammer: | 무기 제작","새로운 무기를 제작합니다!\n가격은 {Null}입니다!\n제작하시겠습니까?"), reference = ctx.message)
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    level = self.client.pool[str(user.id)]["reinforce"][weapon] = {
                        "level": 0,
                        "starforce": 0,
                        "broken": False
                    }
                    await ctx.send(embed=get_embed(":hammer: | 무기 제작","제작 완료했습니다! 다시 강화를 눌러 강화해주세요!"), reference = ctx.message)
                    user = ctx.author.id
                    
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed(f"{self.client.no_emoji} | 취소 되었습니다.","",0xff0000), reference = ctx.message)
                    return
                
        level = self.client.pool[str(user)]["reinforce"][weapon]["level"]
        
        if level >= 100:
            starforce = self.client.pool[str(user)]["reinforce"][weapon]["starforce"]
            if self.client.pool[str(user)]["reinforce"][weapon]["broken"]:
                msg = await ctx.send(embed=get_embed(f"{self.client.no_emoji} | 이 무기는 파괴된 무기입니다.",f"무기를 복구하시겠습니까?\n복구를 위해선 {starforce - 1}의 스타 레벨을 가진 무기를 제물로 사용해야합니다!",0xff0000), reference = ctx.message)
                emjs = [self.client.yes_emoji, self.client.no_emoji]
                await msg.add_reaction(emjs[0])
                await msg.add_reaction(emjs[1])
                def check(reaction, user):
                    return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
                try:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message))
                    return
                else:
                    e = str(reaction.emoji)
                    if e == self.client.yes_emoji:
                        await ctx.send(embed = get_embed("제물로 사용할 무기이름을 입력해주세요!"), reference = ctx.message)
                        def check(author):
                            def inner_check(message): 
                                if message.author != author: return False
                                else: return True
                            return inner_check
                        
                        try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
                        except asyncio.TimeoutError: 
                            self.gaming_list.remove(ctx.author.id)
                            await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message)
                            return
                        else: 
                            name = msg.content
                            
                            if name not in self.pool[str(ctx.author.id)]["reinforce"]:
                                await ctx.send(embed=get_embed(f"{self.client.no_emoji} | 존재하지 않는 무기입니다.","",0xff0000), reference = ctx.message)
                                return
                            
                            lv = self.pool[str(ctx.author.id)]["reinforce"][name]
                            if lv["starforce"] == starforce - 1 and lv["level"] >= 100:
                                del self.pool[str(ctx.author.id)]["reinforce"][name]
                                self.pool[str(ctx.author.id)]["reinforce"][weapon]["broken"] = False
                                await ctx.send(embed=get_embed("복구 성공!"))
                                
                            else:
                                await ctx.send(embed=get_embed(f"{self.client.no_emoji} | 올바른 스타 레벨의 무기를 선택해주세요.","",0xff0000), reference = ctx.message)
                                
                            return
                    elif e == self.client.no_emoji:
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | 취소 되었습니다.","",0xff0000), reference = ctx.message)
                        return
                        
            
            if starforce == 0: s_status = [100, 0, 0, 0]
            elif starforce <= 3: s_status = [70, 30, 0, 0]
            elif starforce <= 5: s_status = [50, 40, 10, 0]
            elif starforce <= 16: s_status = [30, 50, 19, 1]
            elif starforce <= 19: s_status = [20, 60, 17, 3]
            elif starforce <= 24: s_status = [15, 65, 27, 3]
            else: 
                await ctx.send("이미 강화가 최대치입니다!")
                return
            
            msg = await ctx.send(embed=get_embed(":star: | 스타 강화",f"100렙을 넘으셔서 특수강화 도전을 하실수 있습니다.\n강화 대상 : {weapon}\n**확률**\n> 성공 : {s_status[0]}%, 강화 실패 : {s_status[1]}%, 파괴 : {s_status[2]}%, 소멸 : {s_status[3]}%\n\n도전 하시겠습니까?"), reference = ctx.message)
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    
                    rand = random.choices(["성공", "실패", "파괴", "소멸"], weights = s_status)
                    
                    if rand == ["성공"]:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] += 1
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon}의 스타가 **1레벨** 성장했습니다.",f"현재 레벨 : **{starforce+1}**"), reference = ctx.message)
                        return
                    
                    elif rand == ["실패"]:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] -= 1
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon}의 스타가 **1레벨** 하락했습니다.",f"현재 레벨 : **{starforce-1}**",0xff0000), reference = ctx.message)
                        return
                    
                    elif rand == ["파괴"]:
                        self.client.pool[str(user.id)]["reinforce"][weapon]["starforce"] -= 3
                        self.client.pool[str(user.id)]["reinforce"][weapon]["broken"] = True
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | {weapon} (이)가 파괴되었습니다.","",0xff0000), reference = ctx.message)
                        return
                    
                    elif rand == ["소멸"]:
                        del self.client.pool[str(user.id)]["reinforce"][weapon]
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | {weapon} (이)가 소멸되었습니다.","",0xff0000), reference = ctx.message)
                        return
                    
                    else: await ctx.send("?")
                    
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed("{self.client.no_emoji} | 취소 되었습니다.","",0xff0000), reference = ctx.message)
                    return
                
        else:
            msg = await ctx.send(embed=get_embed(":hammer: | 기본 강화","강화에 도전합니다!\n가격은 무료입니다!\n\n성공 : 70% (5~16 레벨 랜덤 오름)\n실패 : 30% (실패시 파괴)\n도전 하시겠습니까?"), reference = ctx.message)
            emjs=[self.client.yes_emoji, self.client.no_emoji]
            await msg.add_reaction(emjs[0])
            await msg.add_reaction(emjs[1])
            def check(reaction, user):
                return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message))
                return
            else:
                e = str(reaction.emoji)
                if e == self.client.yes_emoji:
                    rand = random.choices([True, False], weights = [70, 30])
                    if rand:
                        n = random.randint(5,16)
                        self.client.pool[str(user.id)]["reinforce"][weapon]["level"] += n
                        await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon} (이)가 **{n}레벨** 성장했습니다.",f"현재 레벨 : **{level+n}**"), reference = ctx.message)
                        if self.client.pool[str(user.id)]["reinforce"][weapon]["level"] > 100:
                            self.client.pool[str(user.id)]["reinforce"][weapon]["level"] = 100
                            await ctx.send(embed=get_embed(f"{self.client.yes_emoji} | {weapon}의 레벨이 100레벨을 넘어 100레벨로 자동 조정됩니다!","최대 레벨에 도달하신것을 축하드립니다! 다시 강화를 눌러 스타 강화를 진행하실 수 있습니다!\n현재 레벨 : **100**"))
                        return
                    
                    else:
                        del self.client.pool[str(user.id)]["reinforce"][weapon]
                        await ctx.send(embed=get_embed(f"{self.client.no_emoji} | {weapon} (이)가 파괴되었습니다.","",0xff0000), reference = ctx.message)
                        return
                    
                elif e == self.client.no_emoji:
                    await ctx.send(embed=get_embed("{self.client.no_emoji} | 취소 되었습니다.","",0xff0000), reference = ctx.message)
                    return
                
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            
    @_reinforce.command(name = "목록")
    async def level(self, ctx, user: typing.Optional[discord.Member] = None):
        if not user: user = ctx.author
        if str(user.id) not in self.pool.keys(): raise errors.NotRegistered
        
        reinlist = []
        lis = sorted(self.pool[str(user.id)]["reinforce"].items(), key = lambda x: x[1]["level"] + x[1]["starforce"], reverse = True)
        for k, v in lis:
            f_star_num = trunc(v["starforce"] / 5)
            star_num = v["starforce"] % 5
            str_ = f"**Lv{v['level']}** {':star2:' * f_star_num + ':star:' * star_num} {k}"
            if v["broken"]: str_ = "**(파괴됨)** " + str_
            reinlist.append(str_)
        await ctx.send(embed=get_embed(f"🛠️ | {user.name}님의 강화목록입니다. (총 {len(reinlist)}개)", "\n".join(reinlist)))
        
    @_reinforce.command(name = "삭제")
    @commands.cooldown(1, 100, commands.BucketType.user)
    async def _delete(self, ctx, *, weapon):
        if weapon not in self.client.pool[str(ctx.author.id)]["reinforce"].keys():
            await ctx.send(embed=get_embed("{self.client.no_emoji} | 존재하지 않는 무기입니다.","",0xff0000), reference = ctx.message)
            return
        
        msg = await ctx.send(embed = get_embed("무기를 삭제하시겠습니까?",f"대상 무기: {weapon}\n삭제시 다시는 복구하지 못합니다."), reference = ctx.message)
        emjs = [self.client.yes_emoji, self.client.no_emoji]
        await msg.add_reaction(emjs[0])
        await msg.add_reaction(emjs[1])
        def check(reaction, user):
            return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message))
            return
        else:
            e = str(reaction.emoji)
            if e == self.client.yes_emoji:
                del self.client.pool[str(ctx.author.id)]["reinforce"][weapon]
                await ctx.send(embed = get_embed("무기를 삭제했습니다!"), reference = ctx.message)
            elif e == self.client.no_emoji:
                await ctx.send(embed = get_embed(self.client.no_emoji + " | 취소했습니다."), reference = ctx.message)
                
        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
                
    @_reinforce.command(name = "이름변경")
    @commands.cooldown(1, 100, commands.BucketType.user)
    async def _rename(self, ctx, *, weapon):
        if weapon not in self.client.pool[str(ctx.author.id)]["reinforce"].keys():
            await ctx.send(embed=get_embed("{self.client.no_emoji} | 존재하지 않는 무기입니다.","",0xff0000), reference = ctx.message)
            return
        
        await ctx.send(embed = get_embed("변경하실 무기 이름을 적어주세요",f"대상 무기: {weapon}"), reference = ctx.message)
        
        def check(author):
            def inner_check(message): 
                if message.author != author: return False
                else: return True
            return inner_check
        
        try: msg = await self.client.wait_for('message',check=check(ctx.author),timeout=20)
        except asyncio.TimeoutError: 
            self.gaming_list.remove(ctx.author.id)
            await ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000), reference = ctx.message)
            return
        else: 
            name = msg.content
            if name in self.client.pool[str(ctx.author.id)]["reinforce"].keys():
                await ctx.send(embed=get_embed('이미 존재하는 무기 이름입니다!',"", 0xFF0000), reference = ctx.message)
                return
            
            self.client.pool[str(ctx.author.id)]["reinforce"][name] = self.client.pool[str(ctx.author.id)]["reinforce"][weapon]
            del self.client.pool[str(ctx.author.id)]["reinforce"][weapon]
            await ctx.send(embed = get_embed("이름 변경을 완료 했습니다!",f"{weapon} ==> {name}"), reference = ctx.message)

        with open("./config/user.json", "w", encoding='utf-8') as db_json:
            db_json.write(json.dumps(self.client.pool, ensure_ascii=False, indent=4))
            
    @_reinforce.command(name = "순위")
    async def _rank(self, ctx, n: typing.Optional[int] = 1):
        lis = []
        for k, v in self.client.pool.items():
            for weapon, lev in v["reinforce"].items():
                try: name = self.client.get_user(int(k)).name
                except: name = k
                lis.append([name, weapon, lev["level"], lev["starforce"], lev["starforce"] + lev["level"]])
        lis = sorted(lis, key = lambda x: x[4], reverse = True)
        
        alis = []
        a = (n - 1) * 6 
        medal = ['<:gold_trophy:1003670021672800256>', '<:silver_trophy:1003670023203737760>', '<:bronze_trophy:1003670024730464256>', '<:green_trophy:1003670026336882688>']
        for r in lis:
            if a == 0: m = medal[0]
            elif a == 1: m = medal[1]
            elif a == 2: m = medal[2]
            elif a < 10: m = medal[3]
            else: m =""
            
            alis.append(f"{m} | **{r[0]}**\n> **Lv{r[2]}** {r[1]}\n\n")
            a += 1
            if a >= 10: break
            
        await ctx.send(embed=get_embed(":bar_chart: | 전체 강화 순위","".join(alis)))
        
        
def setup(client):
    client.add_cog(reinforce(client))