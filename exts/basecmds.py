import discord, typing
from discord.ext import commands

def get_embed(title, description='', color=0xccffff): 
    return discord.Embed(title=title,description=description,color=color) #이해하려 하지마세요 ㅎㅎ 어려운 코드입니다.

class BaseCmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name='ext', aliases=['확장'])
    async def _ext(self, ctx: commands.Context):
        pass

    @_ext.command(name='list', aliases=['목록'])
    async def _ext_list(self, ctx: commands.Context):
        allexts = ''
        for oneext in self.client.extensions:
            if oneext == self.__module__:
                allexts += f'🔐 {oneext}\n'
            else:
                allexts += f'✅ {oneext}\n'
        await ctx.send(embed=get_embed(f'🔌 전체 확장 목록',f"총 {len(self.client.extensions)}개의 확장\n{allexts}"))

    @commands.command(name='reload', aliases=['리'])
    async def _ext_reload(self, ctx: commands.Context, names: typing.Optional[str] = None):
        reloads = self.client.extensions
        if (not names) or ('*' in names):
            for onename in list(reloads):
                self.client.reload_extension(onename)
            await ctx.send(embed=get_embed("✅ 활성된 모든 확장을 리로드했습니다","✅ "+"\n✅ ".join(reloads)))
        else:
            try:
                names = "exts." + names
                if not names in reloads:
                    raise commands.ExtensionNotLoaded(f'로드되지 않은 확장: {names}')
                self.client.reload_extension(names)
            except commands.ExtensionNotLoaded:
                await ctx.send(f'**❓ 로드되지 않았거나 존재하지 않는 확장입니다: `{names}`**')
            else:
                await ctx.send(f'**✅ 확장 리로드를 완료했습니다: `{names}`**')

    @commands.command(name='로드')
    async def extload(self, ctx, extension):
        try: self.client.load_extension(f'exts.{extension}')
        except: await ctx.send(f"LOAD\n<a:no:702745889751433277> {extension}")
        else: await ctx.send(f"LOAD\n<a:ok:702745889839775816> {extension}")

    @commands.command(name='언로드')
    async def extunload(self, ctx, extension):
        try: self.client.unload_extension(f'exts.{extension}')
        except: await ctx.send(f"UNLOAD\n<a:no:702745889751433277> {extension}")
        else: await ctx.send(f"UNLOAD\n<a:ok:702745889839775816> {extension}")


def setup(client):
    client.add_cog(BaseCmds(client))