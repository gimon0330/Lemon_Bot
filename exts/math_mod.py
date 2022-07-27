import discord
from discord.ext import commands 
import random

class math_modules(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name="사칙연산", invoke_without_command=True)
    async def calcul(self, ctx):
        warn = discord.Embed(description="""명령어 다음 입력할 수 있는 것들은 
    **더하기**,**빼기**,**곱하기**,**나누기**
    의 세가지 뿐입니다.""",color=0xf4fa72)
        await ctx.send(embed = warn)
        return
    
    @calcul.command(name = "더하기")
    async def add(self, ctx, *arg: int):
        await ctx.send(sum(arg))
    
    @calcul.command(name = "빼기")
    async def min(self, ctx, arg1: int, *arg: int):
        for x in arg:
            arg1 -= x
        await ctx.send(arg1)

    @commands.group(name='대표값', invoke_without_command=True)
    async def dae(self, ctx):
        warn = discord.Embed(description="""명령어 다음 입력할 수 있는 것들은 
    **평균**,**중앙값**,**최빈값**
    의 세가지 뿐입니다""",color=0xf4fa72)
        await ctx.send(embed = warn)
        return

    @dae.command(name = "평균")
    async def average(self, ctx, *arg : float):
        await ctx.send(str(sum(arg) / len(arg)))
            
    @dae.command(name = "중앙값")
    async def mid(self, ctx, *arg):
            a = list(map(float , arg))
            a.sort()
            if len(a) % 2 == 1:
                await ctx.send(a[len(a)//2])
            else:
                res = (a[len(a)//2-1] + a[len(a)//2])/2
                await ctx.send(res)
                
    @dae.command(name = "최빈값")
    async def most_used(self, ctx, *arg: float):
        a = list(set(arg))
        d = []
        res = " "
        for x in a: d.append([x, arg.count(x)])
        d = sorted(d, key=lambda x:x[1])
        most = d[-1][1]
        for x in range(0, len(d)):
            if d[x][1] == most:
                res += str(d[x][0]) + " "
        await ctx.send(res)

            

    @commands.group(name = "수열", invoke_without_command = True)
    async def count(self, ctx, n: int):
        await ctx.send(" ".join(map(str, range(1, n+1))))

    @count.command(name = "소수")
    async def prime_check(self, ctx, n: int):
        a = []
        for i in range(2, n):
            if n % i == 0:
                await ctx.send("합성수입니다.")
                return
            a.append(i)
        await ctx.send(a)

                
    @commands.command(name = "약수") 
    async def div(self, ctx, n : int):
        s = " "
        for x in range(1,n+1):
            if n % x == 0:
                s += str(x) + " "
        await ctx.send(s)
    
    @commands.command(name = "주사위")
    async def rand_d6(self, ctx):
        r = [":one:",":two:",":three:",":four:",":five:",":six:"]
        msg = await ctx.send(random.choice(r))
        for i in range(random.randint(3,6)): await msg.edit(content = random.choice(r)) #?

    @commands.command(name = "뽑기")
    async def rand_choice(self, ctx, n:int): 
        msg = await ctx.send(random.randint(1,n))
        for i in range(random.randint(3,6)): await msg.edit(content = random.randint(1,n))

    @commands.command(name = "분산")
    async def spread(self, ctx, *arg:int):
        d = []
        avg = sum(arg) / len(arg)
        for x in arg:
            d.append((int(x)-avg)**2)
        d = list(map(int, d))
        a = sum(d)
        b = len(d)
        c1 = []
        c2 = []
        res = 1
        if sum(d) % len(d) == 0:
            await ctx.send(sum(d) / len(d))
        else:
            for x in range(1,sum(d)+1):
                if sum(d) % x == 0:
                    c1.append(x)
            for x in range(1,len(d)+1):
                if len(d) % x == 0:
                    c2.append(x)
            for x in range(1,len(c1)):
                for y in range(1, len(c2)):
                    if c1[x] == c2[y]:
                        res = c1[x]
                        break
                if res != 1:
                    break
            await ctx.send(str(int(sum(d)/res)) + "/" + str(int(len(d)/res)))


def setup(client):
    client.add_cog(math_modules(client))