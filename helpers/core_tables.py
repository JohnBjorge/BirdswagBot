from helpers import db_manager
import logging


logger = logging.getLogger(__name__)


async def create_core_tables(self):
    sql_create_table_workout = \
        ("""
            create table if not exists workout (
                workout_id serial not null,
                user_id bigint not null,
                date date not null,
                type_of_workout text not null,
                difficulty int not null,
                note text not null,
                created_on timestamptz default current_timestamp not null,
                updated_on timestamptz default current_timestamp not null,
                constraint valid_type_of_workout check (type_of_workout in ('Endurance', 'Strength', 'Balance', 'Flexibility')),
                constraint valid_difficulty check (difficulty in (1, 2, 3, 4)),
                constraint pkey_workout_id primary key (workout_id)
            );
        """)

    # add constraint so that you can't have multiple same start_dates for a given user
    # essentially a composite primary key of user, start_date
    sql_create_table_fitness_goal = \
        ("""
            create table if not exists fitness_goal (
                    fitness_goal_id serial not null,
                    user_id bigint not null,
                    start_date date not null,
                    end_date date not null,
                    note text not null,
                    created_on timestamptz default current_timestamp not null,
                    updated_on timestamptz default current_timestamp not null,
                    constraint pkey_fitness_goal_id primary key (fitness_goal_id)
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

    await self.bot.db.execute(sql_create_table_workout)
    await self.bot.db.execute(sql_create_table_fitness_goal)
    await self.bot.db.execute(sql_create_table_date_dimension)


async def populate_table_date_dimension(self):
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

    date_dimension_empty = await db_manager.table_is_empty(self, "date_dimension")
    if date_dimension_empty:
        await self.bot.db.execute(sql_populate_date_dimension)


async def create_updated_on_trigger(self):
    sql_create_update_updated_on_column_function = \
        ("""
            create or replace function update_updated_on_column() 
            returns trigger as $$
            begin
                new.updated_on = now();
                return new; 
            end;
            $$ language 'plpgsql';
        """)

    sql_create_workout_updated_on_trigger = \
        ("""
            create or replace trigger update_workout_updated_on_column before update on workout for each row execute procedure update_updated_on_column();
        """)

    sql_create_fitness_goal_updated_on_trigger = \
        ("""
            create or replace trigger update_fitness_goal_updated_on_column before update on fitness_goal for each row execute procedure update_updated_on_column();
        """)

    await self.bot.db.execute(sql_create_update_updated_on_column_function)
    await self.bot.db.execute(sql_create_workout_updated_on_trigger)
    await self.bot.db.execute(sql_create_fitness_goal_updated_on_trigger)



