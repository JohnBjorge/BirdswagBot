from discord.ext import commands
from helpers import core_tables
from helpers import db_manager


class Basic(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await core_tables.create_core_tables(self)
        await core_tables.populate_table_date_dimension(self)

        db_tables = await db_manager.show_tables(self)
        # add check for three tables otherwise throw error?

        print("I'm ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_id = member.id
        print("hello please")
        print(member_id)

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
