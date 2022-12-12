from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("I'm ready")

    @commands.command(aliases=["r"])
    async def read(self, ctx):
        sql = ("SELECT id, name, dob "
               "FROM users "
               "WHERE name='Bob';")

        row = await self.bot.db.fetchrow(sql)
        await ctx.send(row)

#   https://stackoverflow.com/questions/5243596/python-sql-query-string-formatting
    @commands.command(aliases=["w"])
    async def write(self, ctx):
        sql = ("INSERT INTO users (id, name, dob) "
               "VALUES (2, 'John', '1993-08-27');")

        await self.bot.db.execute(sql)
        await ctx.send("I added row to db")


async def setup(bot):
    await bot.add_cog(Basic(bot))
