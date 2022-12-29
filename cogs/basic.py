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

        print("Basic cog ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass


async def setup(bot):
    await bot.add_cog(Basic(bot))
