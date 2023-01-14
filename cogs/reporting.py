from discord.ext import commands
import discord
import logging
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import io
from helpers import db_manager
import matplotlib.ticker as ticker



logger = logging.getLogger(__name__)


class Reporting(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def report_total_workouts(self, ctx, year_actual=None):
        user_id = ctx.author.id

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
        result = [list(row) for row in result]
        xaxis = [item[0] for item in result]
        yaxis = [item[1] for item in result]

        sns.set_theme(style="white", context="talk")

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(15, 5))

        # Generate some sequential data
        sns.barplot(x=xaxis, y=yaxis, palette=sns.color_palette('rocket'))
        ax.axhline(0, color="k", clip_on=False)
        ax.set_xlabel("Week Number")
        ax.set_ylabel("Number of Workouts")

        tick_spacing = 4

        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # Finalize the plot
        sns.despine(bottom=True)
        plt.setp(f.axes)
        plt.tight_layout(pad=1.6)
        # plt.xticks(rotation=90)
        plt.title("Number of Workouts Per Week in " + str(year_actual))

        # plt.savefig('sandbox/images/graph.png', transparent=True)
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
        embed.set_author(name="Birdswag Bot", url="",
                         icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')

        embed.set_image(url=f'attachment://graph.png')

        await ctx.send(file=image, embed=embed)


async def setup(bot):
    await bot.add_cog(Reporting(bot))
