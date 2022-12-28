import collections
import itertools
from typing import Any, Dict, Tuple, List


def pyformat2psql(query: str, named_args: Dict[str, Any]) -> Tuple[str, List[Any]]:
    positional_generator = itertools.count(1)
    positional_map = collections.defaultdict(lambda: '${}'.format(next(positional_generator)))
    formatted_query = query % positional_map
    positional_items = sorted(
        positional_map.items(),
        key=lambda item: int(item[1].replace('$', '')),
    )
    positional_args = [named_args[named_arg] for named_arg, _ in positional_items]
    return formatted_query, positional_args


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

