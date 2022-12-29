from discord.ext import commands
from helpers import core_tables
from helpers import db_manager


class Workouts(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Workouts cog ready")


    @commands.command()
    async def workout(self, ctx, start_date, *, note):
        pass

    @commands.command()
    async def workout_history(self, ctx, start_date, *, note):
        pass

    @commands.command()
    async def workout_new(self, ctx, start_date, *, note):
        pass

    @commands.command()
    async def workout_delete(self, ctx, start_date, *, note):
        pass

    @commands.command()
    async def workout_update(self, ctx, start_date, *, note):
        pass


async def setup(bot):
    await bot.add_cog(Workouts(bot))
