from discord.ext import commands
import discord
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import io
from helpers import db_manager
import matplotlib.ticker as ticker
import pandas as pd


# todo: general cleanup of both reports in here
logger = logging.getLogger(__name__)


class Reports(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def report_total_workouts(self, ctx, year_actual=None):
        """
            Report total number of workouts per week

            Include argument for the year to report on. If no year provided then return current year.

            ex: `$report_total_workouts`
        """
        user_id = ctx.author.id
        username = ctx.author

        if year_actual is None:
            year_actual = datetime.now().year

        sql_report_total_workouts = \
            ("""
                select xaxis.week_of_year as xaxis,
                coalesce(yaxis.total_workouts, 0) as yaxis
                from (
                    select distinct week_of_year, year_actual
                    from date_dimension dd
                ) xaxis
                left join(
                    select
                    dd.week_of_year,
                    dd.year_actual,
                    count(*) as total_workouts
                    from workout w
                    inner join
                    date_dimension dd
                    on w.date = dd.date_actual
                    where w.user_id = %(user_id)s
                    group by
                    w.user_id, dd.week_of_year, dd.year_actual
                ) yaxis
                on xaxis.week_of_year = yaxis.week_of_year
                and xaxis.year_actual = yaxis.year_actual
                where xaxis.year_actual = %(year_actual)s
                order by xaxis.week_of_year;
             """)

        sql_input = {"user_id": user_id, "year_actual": year_actual}

        query, positional_args = db_manager.pyformat_to_psql(sql_report_total_workouts, sql_input)

        logger.debug(f'Fetching workout report for user_id: {user_id} and year_actual: {year_actual}')

        result = await self.bot.db.fetch(query, *positional_args)
        result = [dict(row) for row in result]

        df = pd.DataFrame.from_dict(result)

        sns.set_theme(style="white", context="talk")

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(15, 5))

        # Generate some sequential data
        sns.barplot(data=df, x="xaxis", y="yaxis", palette=sns.color_palette("crest"))

        ax.axhline(0, color="k", clip_on=False)
        ax.set_xlabel("Week Number")
        ax.set_ylabel("Number of Workouts")

        tick_spacing = 4

        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # Finalize the plot
        sns.despine(bottom=True)
        plt.setp(f.axes)
        plt.tight_layout(pad=1.6)
        plt.title("Number of Workouts Per Week in " + str(year_actual))

        plt.savefig('sandbox/images/graph.png')
        plt.close(f)

        with open('sandbox/images/graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        image = discord.File(file, filename='graph.png')

        embed = discord.Embed(title="Report",
                              url='',
                              description="Weekly Total Workouts",
                              color=0x1036cb,
                              timestamp=datetime.today())
        embed.set_author(name=username, url="",
                         icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')

        embed.set_image(url=f'attachment://graph.png')

        await ctx.send(file=image, embed=embed)

    @commands.command()
    async def report_workout_mix(self, ctx, year_actual=None):
        """
            Report total number of workouts per quarter by workout type

            Include argument for the year to report on. If no year provided then return current year.

            ex: `$report_workout_mix`
        """
        user_id = ctx.author.id
        username = ctx.author

        if year_actual is None:
            year_actual = datetime.now().year

        sql_report_workout_mix = \
            ("""
                select xaxis.quarter_actual as xaxis,
                xaxis.type_of_workout,
                coalesce(yaxis.total_workouts, 0) as yaxis
                from (
                    select distinct quarter_actual, year_actual, type_of_workout.type_of_workout
                    from date_dimension dd
                    cross join (
                        select distinct type_of_workout from workout
                    ) type_of_workout
                ) xaxis
                left join(
                    select dd.quarter_actual,
                    dd.year_actual,
                    w.type_of_workout,
                    count(*) as total_workouts
                    from workout w
                    inner join date_dimension dd
                    on w.date = dd.date_actual
                    where w.user_id = %(user_id)s
                    group by w.user_id, dd.quarter_actual, dd.year_actual, w.type_of_workout
                ) yaxis
                on xaxis.quarter_actual = yaxis.quarter_actual
                and xaxis.year_actual = yaxis.year_actual
                and xaxis.type_of_workout = yaxis.type_of_workout
                where xaxis.year_actual = %(year_actual)s
                order by xaxis.quarter_actual;
             """)

        sql_input = {"user_id": user_id, "year_actual": year_actual}

        query, positional_args = db_manager.pyformat_to_psql(sql_report_workout_mix, sql_input)

        logger.debug(f'Fetching workout report for user_id: {user_id} and year_actual: {year_actual}')

        result = await self.bot.db.fetch(query, *positional_args)
        result = [dict(row) for row in result]

        df = pd.DataFrame.from_dict(result)

        sns.set_theme(style="white", context="talk")

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(15, 5))

        sns.barplot(data=df, x="xaxis", y="yaxis", hue="type_of_workout", palette=sns.color_palette("bright"))

        ax.axhline(0, color="k", clip_on=False)
        # ax.set_xlabel("Quarter of Year")
        # ax.set_ylabel("Number of Workouts")

        # Finalize the plot
        sns.despine(bottom=True)
        plt.setp(f.axes)
        plt.tight_layout(pad=1.6)
        plt.title("Number of Workouts Per Quarter in " + str(year_actual))
        plt.xlabel("Quarter of Year")
        plt.ylabel("Number of Workouts")
        plt.legend(title='Type of Workout')

        # plt.savefig('sandbox/images/graph.png', transparent=True)
        plt.savefig('sandbox/images/graph.png')
        plt.close(f)

        with open('sandbox/images/graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        image = discord.File(file, filename='graph.png')

        embed = discord.Embed(title="Report",
                              url='',
                              description="Quarterly Total Workouts",
                              color=0x1036cb,
                              timestamp=datetime.today())
        embed.set_author(name=username, url="",
                         icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')

        embed.set_image(url=f'attachment://graph.png')

        await ctx.send(file=image, embed=embed)


async def setup(bot):
    await bot.add_cog(Reports(bot))
