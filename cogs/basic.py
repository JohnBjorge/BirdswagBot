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

    # @commands.command(usage=None)
    # @settings.in_bot_channel_strict()
    @commands.command()
    async def guide(self, ctx):
        """
        Show an overview of what the bot is for

        Type `$guide` for an overview of what this bot is for and how to use it.
        """
        bot_desc = ('This bot is designed to improve Polytopia multiplayer by filling in gaps in two areas: competitive leaderboards, and matchmaking.\n'
                    f'To register as a player with the bot use __`{ctx.prefix}setname Mobile User Name`__ or  __`{ctx.prefix}steamname Steam User Name`__')

        embed = discord.Embed(title='PolyELO Bot Donation Link', url='https://www.buymeacoffee.com/nelluk', description=bot_desc)

        embed.add_field(name='Setting Goals',
            value=f'This helps players organize and find games.\nFor example, use __`{ctx.prefix}opengame 1v1`__ to create an open 1v1 game that others can join.\n'
                f'To see a list of open games you can join use __`{ctx.prefix}opengames`__. Once the game is full the host would use __`{ctx.prefix}startgame`__ to close it and track it for the leaderboards.\n'
                f'See __`{ctx.prefix}help matchmaking`__ for all commands.', inline=False)

        embed.add_field(name='Logging Workouts',
            value='Win your games and climb the leaderboards! Earn sweet ELO points!\n'
                'ELO points are gained or lost based on your game results. You will gain more points if you defeat an opponent with a higher ELO.\n'
                f'Use __`{ctx.prefix}lb`__ to view the individual leaderboards. There is also a __`{ctx.prefix}lbsquad`__ squad leaderboard. Form a squad by playing with the same person in multiple games!'
                f'\nSee __`{ctx.prefix}help`__ for all commands.', inline=False)

        embed.add_field(name='Tracking Progress',
            value=f'Use the __`{ctx.prefix}win`__ command to tell the bot that a game has concluded.\n'
            f'For example if Nelluk wins game 10150, he would type __`{ctx.prefix}win 10150 nelluk`__. The losing player can confirm using the same command. '
            'Games are auto-confirmed after 24 hours, or sooner if the losing side manually confirms.', inline=False)

        embed.add_field(name='Earning Badges',
            value=f'Use the __`{ctx.prefix}win`__ command to tell the bot that a game has concluded.\n'
            f'For example if Nelluk wins game 10150, he would type __`{ctx.prefix}win 10150 nelluk`__. The losing player can confirm using the same command. '
            'Games are auto-confirmed after 24 hours, or sooner if the losing side manually confirms.', inline=False)

        embed.set_thumbnail(url=self.bot.user.display_avatar.replace(size=512, format='webp'))
        embed.set_footer(text='Developer: JohnBjorge')
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Basic(bot))
