import discord, traceback, sys
from itertools import cycle
from discord.ext import commands, tasks
from utils import permutil, errors

def get_embed(title, description = '', color=0xFF0000, no_emoji = "<a:no:1001365885426073690> | "): 
    return discord.Embed(title=no_emoji + title,description=description,color=color)

class events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bg_change_playing.start()
        self.gamecycle = cycle([])

    @tasks.loop(seconds=10)
    async def bg_change_playing(self):
        await self.client.change_presence(activity=discord.Game(f"LemonBot V2.1.0 // {len(self.client.guilds)} Servers│{len(self.client.pool.keys())} Users"))

    @commands.Cog.listener()
    async def on_ready(self):
        print("==================\nLemonBOT ONLINE\n==================")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        allerrs = (type(error), type(error.__cause__))
        if commands.errors.MissingRequiredArgument in allerrs:
            return
        
        elif isinstance(error, errors.NotMaster):
            await ctx.send(embed=get_embed("봇에 엑세스할 권한이 부족합니다!","필요한 권한 : `BOT ADMINISTRATOR`"))
            return

        elif isinstance(error, errors.NotRegistered):
            await ctx.send(embed=get_embed('가입 되어 있지 않습니다!',"<알티야 가입> 으로 가입해주세요"))
            return

        elif isinstance(error, errors.NoMoney):
            await ctx.send(embed=get_embed("돈이 부족합니다!",''))
            return

        elif isinstance(error, errors.AlreadyRegistered):
            await ctx.send(embed=get_embed("이미 가입 되어 있습니다!",""))
            return

        elif isinstance(error, errors.morethan1):
            await ctx.send(embed=get_embed('1원 이상의 정수값을 입력해주세요!',""))
            return
        
        ###################################################################################################

        elif isinstance(error, discord.NotFound):
            return

        elif isinstance(error, commands.errors.CommandNotFound):
            return

        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(embed=get_embed("명령어 양식을 지켜주세요!","입력한 명령어가 올바른지 확인해주세요"))
            return

        elif isinstance(error, commands.MissingPermissions):
            perms = [permutil.format_perm_by_name(perm) for perm in error.missing_perms]
            embed = get_embed("멤버 권한 부족!",
                f"{self.ctx.author.mention}, 이 명령어를 사용하려면 다음과 같은 길드 권한이 필요합니다!\n> **`"
                + "`, `".join(perms)
                + "`**",
            )
            await ctx.send(embed=get_embed('멤버 권한 부족!',f'{ctx.author.mention}, 이 명령어를 사용하려면 다음과 같은 길드 권한이 필요합니다!\n`'+ '`, `'.join(perms) + '`'))
            return

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=get_embed("서버내 사용 가능 명령어입니다!","서버에서만 사용해주세요"))
            return

        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(embed=get_embed("DM 전용 명령어입니다!","디엠에서만 사용해주세요"))
            return
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if int(error.retry_after) > 1:
                await ctx.send(embed=get_embed("명령어를 조금만 천천히 써주세요!",'{:.2f}초만 기다려주세요!'.format(error.retry_after)))
            return

        elif isinstance(error, commands.errors.MissingPermissions):
            return

        elif isinstance(error.__cause__, discord.HTTPException):
            if error.__cause__.code in [50013, 50001]:
                try: 
                    missing_perms = []
                    fmtperms = [permutil.format_perm_by_name(perm) for perm in missing_perms]
                    if missing_perms:
                        embed = get_embed(
                            "봇 권한 부족!",
                            "이 명령어를 사용하는 데 필요한 봇의 권한이 부족합니다!\n`"
                            + "`, `".join(fmtperms)
                            + "`",
                        )
                    else:
                        embed = get_embed(
                            "봇 권한 부족!",
                            "이 명령어를 사용하는 데 필요한 봇의 권한이 부족합니다!\n부족한 권한이 무엇인지 감지하는 데 실패했습니다.",
                        )
                    await ctx.send(embed=embed)
                except discord.Forbidden:
                    embed = get_embed("메시지를 보낼 수 없습니다!",
                        f"""\
                            방금 [명령어]({ctx.message.jump_url})를 입력하신 채널에서 알티봇에 `메시지 전송하기` 또는 `링크 전송` 권한이 없어 메시지를 보낼 수 없습니다. 서버 관리자에게 문의해주세요.
                            **(`{ctx.guild}` 서버의 `{ctx.channel}` 채널)**
                        """,
                    )
                    await ctx.author.send(embed=embed)
                return

            elif error.__cause__.code == 50035:
                await ctx.send(embed=get_embed('메시지 전송 실패','보내려고 하는 메시지가 너무 길어 전송에 실패했습니다.'))
                return

            elif error.__cause__.code == 50005:
                await ctx.send(embed=get_embed('메시지 수정 실패','타인의 메세지는 수정불가합니다.'))
                return

            elif error.__cause__.code == 50003:
                await ctx.send(embed=get_embed('Cannot execute action on a DM channel','DM에서 할수 없는 명령어 입니다.'))
                return

            elif error.__cause__.code == 50007:
                embed = get_embed('메시지 전송 실패', 'DM(개인 메시지)으로 메시지를 전송하려 했으나 실패했습니다.\n혹시 DM이 비활성화 되어 있지 않은지 확인해주세요!')
                await ctx.send(ctx.author.mention, embed=embed)
                return
            
            elif error.__cause__.code == 10008:
                return

            else:
                embed = get_embed('알 수 없는 에러', '오류 코드: ' + str(error.__cause__.code))
                await ctx.send(embed=embed)
                return

        await ctx.send(embed=get_embed('**Unknown ERROR**!',f'Id : {ctx.author.id}\nContent : {ctx.message.content}```python\n{traceback.format_exception(type(error), error, error.__traceback__)}```',0xFF0000))

def setup(client):
    client.add_cog(events(client))