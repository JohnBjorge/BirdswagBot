import logging
from discord.ext import commands
import aiocron
from helpers import awards
from datetime import date
from helpers import db_manager


logger = logging.getLogger(__name__)


class CronJobs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        @aiocron.crontab("0 19 * * *")  # everyday at 7pm check for awards
        # @aiocron.crontab("* * * * * */10")  # every 10 seconds for testing
        async def awards_notification():
            current_date = date.today()

            sql_input = {"current_date": current_date}

            sql_date_dimension_current_date = \
                ("""
                    select day_of_week,
                    day_of_quarter,
                    day_of_year,
                    week_of_year,
                    quarter_actual,
                    year_actual
                    from date_dimension 
                    where date_actual = %(current_date)s;
                """)

            query, positional_args = db_manager.pyformat_to_psql(sql_date_dimension_current_date, sql_input)

            logger.debug(f'Returning date information for current date: {current_date}\n')

            result = await self.bot.db.fetchrow(query, *positional_args)

            if result["day_of_week"] == 7:
                await awards.award_weekly(self, result["year_actual"], result["week_of_year"])

            if result["day_of_quarter"] == 1:
                await awards.award_quarterly(self, result["year_actual"], result["quarter_actual"])

            if result["day_of_year"] == 1:
                await awards.award_yearly(self)


async def setup(bot):
    await bot.add_cog(CronJobs(bot))
