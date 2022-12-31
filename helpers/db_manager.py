import collections
import itertools
from typing import Any, Dict, Tuple, List
import logging


logger = logging.getLogger(__name__)


# https://github.com/MagicStack/asyncpg/issues/9#issuecomment-600659015
def pyformat_to_psql(query: str, named_args: Dict[str, Any]) -> Tuple[str, List[Any]]:
    positional_generator = itertools.count(1)
    positional_map = collections.defaultdict(lambda: '${}'.format(next(positional_generator)))
    formatted_query = query % positional_map
    positional_items = sorted(
        positional_map.items(),
        key=lambda item: int(item[1].replace('$', '')),
    )
    positional_args = [named_args[named_arg] for named_arg, _ in positional_items]
    return formatted_query, positional_args


async def workout_id_matches_user_id(self, workout_id, user_id):
    sql_input = {"workout_id": workout_id, "user_id": user_id}

    sql_workout_id_matches_user_id = \
        ("""select 1
            from workout
            where user_id = %(user_id)s
            and workout_id = %(workout_id)s
            limit 1
        """)

    query, positional_args = pyformat_to_psql(sql_workout_id_matches_user_id, sql_input)

    result = await self.bot.db.fetchrow(query, *positional_args)

    if result is None:
        return False
    else:
        return True


async def fitness_goal_id_matches_user_id(self, fitness_goal_id, user_id):
    sql_input = {"fitness_goal_id": fitness_goal_id, "user_id": user_id}

    sql_fitness_goal_id_matches_user_id = \
        ("""select 1
            from fitness_goal
            where user_id = %(user_id)s
            and fitness_goal_id = %(fitness_goal_id)s
            limit 1
        """)

    query, positional_args = pyformat_to_psql(sql_fitness_goal_id_matches_user_id, sql_input)

    result = await self.bot.db.fetchrow(query, *positional_args)

    if result is None:
        return False
    else:
        return True


async def fitness_goal_exist_user_id(self, user_id):
    sql_input = {'user_id': user_id}

    sql_fitness_goal_exist_user_id = \
        ("""select 1
            from fitness_goal
            where user_id = %(user_id)s
            limit 1
        """)

    query, positional_args = pyformat_to_psql(sql_fitness_goal_exist_user_id, sql_input)

    result = await self.bot.db.fetchrow(query, *positional_args)

    if result is None:
        return False
    else:
        return True


async def fitness_goal_update_end_dates(self):
    sql_fitness_goal_update_end_dates = \
        ("""
            with inferred_end_date as
            (
                select fitness_goal_id,
                lead(start_date, -1, '2999-12-31') over(partition by user_id order by start_date desc) - 1 as end_date
                from fitness_goal
            )
            update fitness_goal
            set end_date = inferred_end_date.end_date
            from inferred_end_date
            where inferred_end_date.fitness_goal_id = fitness_goal.fitness_goal_id;
        """)

    await self.bot.db.execute(sql_fitness_goal_update_end_dates)


async def show_tables(self):
    sql_show_tables = \
        ("""
            select table_name 
            from information_schema.tables
            where table_schema = 'public';
        """)

    result = await self.bot.db.fetch(sql_show_tables)
    list_tables = [item[0] for item in result]

    return list_tables


# todo: not sure if I need to change to prepared statement, also not able to with table name
async def table_is_empty(self, table_name):
    sql_table_is_empty = \
        (f"""
            select *
            from {table_name}
            limit 1;
        """)

    result = await self.bot.db.fetchrow(sql_table_is_empty)

    if result is None:
        result = True
    else:
        result = False

    return result

