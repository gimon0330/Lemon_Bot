import discord, traceback, io
from discord.ext import commands 
from utils import checks

def get_embed(title, description='', color=0xf4fa72): 
    return discord.Embed(title=title,description=description,color=color)

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
    
    @commands.command(name="hawait")
    async def _hawait(self, ctx, *, arg):
        try: await eval(arg) 
        except: await ctx.send(embed=discord.Embed(title = '관리자 기능 - Await Eval',description = f"📤 EXCEPT```{traceback.format_exc()}```",color = 0xFF0000))
    
    @commands.command(name='exec')
    async def _exec(self, ctx, *, arg):
        try: await ctx.send(embed=get_embed('관리자 기능 - Exec',f"📤 OUTPUT```{exec(arg)}```"))
        except: await ctx.send(embed=get_embed('관리자 기능 - Exec',f"📤 EXCEPT```{traceback.format_exc()}```",0xFF0000))
        await self.sendlog(ctx)
    
    @commands.command(name='강화설정')
    async def reinforce_set(self, ctx, uid: str, name: str, level: int):
        self.client.pool[uid]["reinforce"][name] = level
        await ctx.send(f"{uid}님의 {name} Level을 {level}로 설정하였습니다")
        
    @commands.command(name='돈설정')
    async def _money_set(self, ctx, uid: str, n: int):
        self.client.pool[str(uid)]["money"] = n
        await ctx.send(f"{uid}님의 money을 {n}원으로 설정하였습니다")
        
    @commands.command(name='은행설정')
    async def _bank_set(self, ctx, uid: str, n: int):
        self.client.pool[str(uid)]["bank"] = n
        await ctx.send(f"{uid}님의 bank을 {n}원으로 설정하였습니다")
        
    @commands.command(name='강제가입')
    async def _force_register(self, ctx: commands.Context, uid: str):
        self.client.pool[uid] = {
            "money": 0,
            "bank": 0,
            "reinforce": {},
            "blacklist": False,
            "permission": "User"
        }
        if uid in self.client.pool.keys():
            await ctx.send(f"등록되어 있지 않은 유저 {uid}님을 강제로 가입시켰습니다")
        else: await ctx.send(f"유저({uid})를 강제 초기화 시켰습니다.")
        
    @commands.command(name='유저등록확인')
    async def _check_user_existing(self, ctx: commands.Context, uid: str): 
        str = ""
        for key, value in self.client.pool[uid].items():
            str += f"{key}: {value}\n"
        await ctx.send(str)
        
    @commands.command(name='권한설정')
    async def _add_admin(self, ctx: commands.Context, uid: str, perm: str = "Master"):
        self.client.pool[uid]["permission"] = perm
        await ctx.send(f"유저({uid})님의 권한을 {perm}으로 설정하였습니다.")
        
    @commands.command(name="블랙추가")
    async def _up_black(self, ctx, uid: str):
        self.client.pool[uid]["blacklist"] = True
        await ctx.send(f"User {uid} 를 블랙리스트에 추가하였습니다.")
        
    @commands.command(name="블랙제거")
    async def _down_black(self, ctx, uid):
        self.client.pool[uid]["blacklist"] = False
        await ctx.send(f"User {uid} 를 블랙리스트에서 제거하였습니다.")
        
    @commands.command(name='공지보내')
    async def _notice_send(self, ctx, *, arg):
        noticedb = {"621929509456838666":621932639539953664}
        lis =["SUCCEED LIST"]
        faillis = ["FAIL LIST"]
        sendctrlpannel = await ctx.send(embed=get_embed("공지 전송중",""))
        for s in self.client.guilds:
            sendedserver = s.name
            schannel = ''
            if str(s.id) in noticedb.keys():
                schannel=self.client.get_channel(noticedb[str(s.id)])
            else:
                for channel in s.text_channels:
                    if channel.permissions_for(s.me).send_messages:
                        freechannel = channel
                        if '공지' in channel.name and '봇' in channel.name:
                            schannel = channel
                            break
                        elif 'noti' in channel.name.lower() and 'bot' in channel.name.lower():
                            schannel = channel
                            break
                        elif '공지' in channel.name:
                            schannel = channel
                            break
                        elif 'noti' in channel.name.lower():
                            schannel = channel
                            break
                        elif '봇' in channel.name:
                            schannel = channel
                            break
                        elif 'bot' in channel.name.lower():
                            schannel = channel
                            break
                if schannel == '':
                    schannel = freechannel
            try: 
                await schannel.send(embed=get_embed("📢 | 레몬봇 공지",arg+"\n\n모든 문의,건의는 [레몬봇 서포트](https://discord.gg/hTZxtbC) 에서 해주세요.\n[레몬봇 초대하기](https://discordapp.com/api/oauth2/authorize?client_id=751660576589217893&permissions=8&scope=bot) "))
                lis.append('성공 ' + sendedserver)
            except: 
                faillis.append('실패 ' + sendedserver)
            await sendctrlpannel.edit(embed=get_embed("공지 전송중",f"성공 : {len(lis) - 1}\n실패 : {len(faillis) - 1}"))
        await ctx.send("성공")
        logfile = discord.File(fp=io.StringIO("\n".join(lis)+"\n\n"+"\n".join(faillis)), filename='notilog.log')
        await ctx.send(file=logfile)
    
def setup(client):
    client.add_cog(admin(client))