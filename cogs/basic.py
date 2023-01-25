from discord.ext import commands
import discord
from helpers import core_tables
from helpers import db_manager
from datetime import datetime
import logging
import json
from tabulate import tabulate


tabulate.PRESERVE_WHITESPACE = True

logger = logging.getLogger(__name__)


class Basic(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # todo: this appears to get run multiple times and not sure when or why, documentation seems to indicate it won't
    #  necessarily get run once. Where should I instantiate these tables that only need to happen once? Right now it's
    #  fine here since I say "create or replace" or "create if not exists".
    @commands.Cog.listener()
    async def on_ready(self):
        await core_tables.create_core_tables(self)
        await core_tables.populate_table_date_dimension(self)
        await core_tables.create_updated_on_trigger(self)

        db_tables = await db_manager.show_tables(self)
        # add check for three tables otherwise throw error?

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass


async def setup(bot):
    await bot.add_cog(Basic(bot))
