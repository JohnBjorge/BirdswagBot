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
        bot_desc = ('This bot is designed to help you on your fitness journey by tracking your goals and tracking your'
                    f'workouts. To register with the bot use `$join`.')

        embed = discord.Embed(title='Fitness Bot', url='', description=bot_desc)

        embed.add_field(name='Setting Goals',
                        value='We want to keep track of our goals in order to give purpose to our workouts.\n'
                        f'To see a list of your goals you can use `$goal_history` or to see your most recent goal'
                        f'use `$goal`', inline=False)

        embed.add_field(name='Logging Workouts',
                        value='We want to log our workouts to keep track of our progress. We also publicly log our'
                        f'workouts because your consistency will also motivate them to be consistent too!\n'
                        f'To log a workout use `$workout_new` or to see a list of past workouts use `$workout_history`.'
                        f'If you need to search for a past workout, try using `$workout_search`.', inline=False)

        embed.add_field(name='Tracking Progress',
                        value='We want to focus on two themes: consistency and effort\n'
                        f'To see how consistent you\'ve been use `$report_total_workouts` or to see what types of'
                        f'workouts you\'ve been prioritizing use `$report_workout_mix`. To see how much effort you\'ve'
                        f'been putting in use (commands coming)...', inline=False)

        embed.add_field(name='Earning Badges',
                        value='We want to reward those that accomplish consistency over long periods of time.\n'
                        f'The benchmark is 4 workouts per week (they can be any type and any difficulty). The important'
                        f'thing is that we are consistent.', inline=False)

        embed.set_thumbnail(url=self.bot.user.display_avatar.replace(size=512, format='webp'))
        # embed.set_footer(text='Developer: JohnBjorge')
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Basic(bot))
