import discord
from discord.ext import commands
from . import errors

class checks:
    def __init__(self, pool: dict):
        self.pool = pool

    async def money0up(self, ctx: commands.Context):
        if str(ctx.author.id) in self.pool.keys():
            if self.pool[str(ctx.author.id)]["money"] > 0:
                return True
            raise errors.NoMoney
        raise errors.NotRegistered

    async def master(self, ctx: commands.Context):
        if self.pool[str(ctx.author.id)]["permission"] == 'Master':
            return True
        raise errors.NotMaster
    
    async def beta_tester(self, ctx: commands.Context):
        if self.pool[str(ctx.author.id)]["permission"] == 'BetaTester':
            return True
        raise errors.NotTester
    
    async def registered(self, ctx: commands.Context):
        if str(ctx.author.id) in self.pool.keys():
            return True
        raise errors.NotRegistered
