import logging
from helpers import db_manager


logger = logging.getLogger(__name__)


def award_workouts_scoreboard():
    sql_workouts_scoreboard = \
    ("""
        with workouts_scoreboard as (
            select w.user_id,
            dd.week_of_year,
            dd.quarter_actual,
            dd.year_actual,
            count(*) as total_workouts,
            sum(difficulty) as total_difficulty,
            case when count( * ) >= 4 then 1 else 0 end as consistency_flag
            from workout w
            inner join date_dimension dd
            on w.date = dd.date_actual
            group by w.user_id, dd.week_of_year, dd.quarter_actual, dd.year_actual
        )\n\n
    """)

    return sql_workouts_scoreboard


# todo: has not been tested
async def award_weekly(self, ctx, year_actual, week_of_year):
    sql_cte_workouts_scoreboard = award_workouts_scoreboard()

    sql_input = {"year_actual": year_actual, "week_of_year": week_of_year}

    sql_award_weekly = \
        ("""
            select user_id,
            year_actual,
            week_of_year,
            sum(total_workouts),
            round(sum(total_difficulty) / sum(total_workouts), 2) as avg_difficulty
            from workouts_scoreboard
            where year_actual = %(year_actual)s
            and week_of_year = %(week_of_year)s
            and consistency_flag = 1
            group by user_id, year_actual, week_of_year;
        """)

    query, positional_args = db_manager.pyformat_to_psql(sql_cte_workouts_scoreboard + sql_award_weekly, sql_input)

    logger.debug(f'Returning award list for year {year_actual} and week {week_of_year}\n')

    result = await self.bot.db.fetch(query, *positional_args)

    # todo: turn this into an embed
    await self.bot.get_channel(1045906913080115225).send(result)


# todo: has not been tested
async def award_quarterly(self, year_actual, quarter_actual):
    sql_cte_workouts_scoreboard = award_workouts_scoreboard()

    sql_input = {"year_actual": year_actual, "quarter_actual": quarter_actual}

    sql_award_quarterly = \
        ("""
            select user_id, 
            year_actual, 
            quarter_actual, 
            sum(total_workouts) as total_workouts,
            round(sum(total_difficulty) / sum(total_workouts), 2) as avg_difficulty,
            case when min(consistency_flag) = 0 then 0 else 1 end as consistency_flag
            from workouts_scoreboard
            where year_actual = %(year_actual)s
            and quarter_actual = %(quarter_actual)s - 1
            group by user_id, year_actual, quarter_actual;
        """)

    query, positional_args = db_manager.pyformat_to_psql(sql_cte_workouts_scoreboard + sql_award_quarterly, sql_input)

    logger.debug(f'Returning award list for year {year_actual} and quarter {quarter_actual}\n')

    result = await self.bot.db.fetch(query, *positional_args)

    # todo: turn this into an embed
    await self.bot.get_channel(1045906913080115225).send(result)


# todo: has not been tested
async def award_yearly(self, year_actual):
    sql_cte_workouts_scoreboard = award_workouts_scoreboard()

    sql_input = {"year_actual": year_actual}

    sql_award_yearly = \
        ("""
            select user_id, 
            year_actual, 
            sum(total_workouts) as total_workouts,
            round(sum(total_difficulty) / sum(total_workouts), 2) as avg_difficulty,
            case when min(consistency_flag) = 0 then 0 else 1 end as consistency_flag
            from workouts_scoreboard
            where year_actual = %(year_actual)s
            group by user_id, year_actual;
        """)

    query, positional_args = db_manager.pyformat_to_psql(sql_cte_workouts_scoreboard + sql_award_yearly, sql_input)

    logger.debug(f'Returning award list for year {year_actual}\n')

    result = await self.bot.db.fetch(query, *positional_args)

    # todo: turn this into an embed
    await self.bot.get_channel(1045906913080115225).send(result)
