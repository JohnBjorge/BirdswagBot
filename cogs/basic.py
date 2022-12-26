from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("I'm ready")

        sql_create_table_workout = \
            ("""
                create table if not exists workout (
                    workout_id serial not null primary key,
                    user_discord_id int not null,
                    date date not null,
                    type_of_workout text not null,
                    difficulty int not null,
                    note text not null,
                    constraint valid_type_of_workout check (type_of_workout in ('cardio', 'strength', 'balance', 'flexibility')),
                    constraint valid_difficulty check (difficulty in (1, 2, 3, 4))
                );
            """)

        sql_create_table_user_discord = \
            ("""
                create table if not exists user_discord (
                    user_discord_id int not null,
                    start_date date not null,
                    end_date date not null,
                    goal text not null
                );
            """)

        sql_create_table_date_dimension = \
            ("""
                create table if not exists date_dimension (
                    date_dimension_id int not null,
                    date_actual date not null,
                    epoch bigint not null,
                    day_suffix varchar(4) not null,
                    day_name varchar(9) not null,
                    day_of_week int not null,
                    day_of_month int not null,
                    day_of_quarter int not null,
                    day_of_year int not null,
                    week_of_month int not null,
                    week_of_year int not null,
                    week_of_year_iso varchar(10) not null,
                    month_actual int not null,
                    month_name varchar(9) not null,
                    month_name_abbreviated varchar(3) not null,
                    quarter_actual int not null,
                    quarter_name varchar(9) not null,
                    year_actual int not null,
                    first_day_of_week date not null,
                    last_day_of_week date not null,
                    first_day_of_month date not null,
                    last_day_of_month date not null,
                    first_day_of_quarter date not null,
                    last_day_of_quarter date not null,
                    first_day_of_year date not null,
                    last_day_of_year date not null,
                    mmyyyy varchar(6) not null,
                    mmddyyyy varchar(10) not null,
                    weekend varchar(7) not null,
                    holiday_usa varchar(10) not null,
                    constraint pkey_date_dimension primary key (date_dimension_id)
                );
            """)

        sql_populate_date_dimension = \
            ("""
                insert into date_dimension
                select to_char(datum, 'yyyymmdd')::int as date_dimension_id,
                       datum as date_actual,
                       extract(epoch from datum) as epoch,
                       to_char(datum, 'fmDDth') as day_suffix,
                       to_char(datum, 'TMDay') as day_name,
                       extract(isodow from datum) as day_of_week,
                       extract(day from datum) as day_of_month,
                       datum - date_trunc('quarter', datum)::date + 1 as day_of_quarter,
                       extract(doy from datum) as day_of_year,
                       to_char(datum, 'W')::int as week_of_month,
                       extract(week from datum) as week_of_year,
                       extract(isoyear from datum) || to_char(datum, '"-W"IW-') || extract(isodow from datum) as week_of_year_iso,
                       extract(month from datum) as month_actual,
                       to_char(datum, 'TMMonth') as month_name,
                       to_char(datum, 'Mon') as month_name_abbreviated,
                       extract(quarter from datum) as quarter_actual,
                       case
                           when extract(quarter from datum) = 1 then 'First'
                           when extract(quarter from datum) = 2 then 'Second'
                           when extract(quarter from datum) = 3 then 'Third'
                           when extract(quarter from datum) = 4 then 'Fourth'
                           end as quarter_name,
                       extract(year from datum) as year_actual,
                       datum + (1 - extract(isodow from datum))::int as first_day_of_week,
                       datum + (7 - extract(isodow from datum))::int as last_day_of_week,
                       datum + (1 - extract(day from datum))::int as first_day_of_month,
                       (date_trunc('month', datum) + interval '1 month - 1 day')::date as last_day_of_month,
                       date_trunc('quarter', datum)::date as first_day_of_quarter,
                       (date_trunc('quarter', datum) + interval '3 month - 1 day')::date as last_day_of_quarter,
                       to_date(extract(year from datum) || '-01-01', 'YYYY-MM-DD') as first_day_of_year,
                       to_date(extract(year from datum) || '-12-31', 'YYYY-MM-DD') as last_day_of_year,
                       to_char(datum, 'mmyyyy') as mmyyyy,
                       to_char(datum, 'mmddyyyy') as mmddyyyy,
                       case
                           when extract(isodow from datum) in (6, 7) then 'Weekend'
                           else 'Weekday'
                           end as weekend,
                       -- Fixed holidays for USA
                       case 
                           when to_char(datum, 'MMDD') in ('0101', '0704', '1225', '1226')
                               then 'Holiday' else 'No holiday' 
                           end as holiday_usa
                from (select '1970-01-01'::date + sequence.day as datum
                      from generate_series(0, 29219) as sequence (day)
                      group by sequence.day) dq
                order by 1;
            """)

        print("creating tables")
        await self.bot.db.execute(sql_create_table_workout)
        await self.bot.db.execute(sql_create_table_user_discord)
        await self.bot.db.execute(sql_create_table_date_dimension)
        print("done creating tables")
        await self.bot.db.execute(sql_populate_date_dimension)
        print("done populating date dimension table")

    @commands.command(aliases=["r"])
    async def read(self, ctx):
        sql = ("SELECT id, name, dob "
               "FROM users "
               "WHERE name='Bob';")

        row = await self.bot.db.fetchrow(sql)
        await ctx.send(row)

#   https://stackoverflow.com/questions/5243596/python-sql-query-string-formatting
    @commands.command(aliases=["w"])
    async def write(self, ctx):
        sql = ("INSERT INTO users (id, name, dob) "
               "VALUES (2, 'John', '1993-08-27');")

        await self.bot.db.execute(sql)
        await ctx.send("I added row to db")


async def setup(bot):
    await bot.add_cog(Basic(bot))
