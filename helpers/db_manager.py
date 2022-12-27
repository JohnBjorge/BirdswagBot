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
