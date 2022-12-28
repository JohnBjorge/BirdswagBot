from discord.ext import commands
from helpers import core_tables
from helpers import db_manager
import datetime
import typing


class Basic(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await core_tables.create_core_tables(self)
        await core_tables.populate_table_date_dimension(self)

        db_tables = await db_manager.show_tables(self)
        # add check for three tables otherwise throw error?

        print("I'm ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def join(self, ctx):
        # check if user already exists, if not proceed, otherwise exit out

        user_id = ctx.author.id
        start_date = str(date.today())
        end_date = "2999-12-31"
        note = "No goals"

        sql_input = dict({"user_id": user_id, "start_date": start_date, "end_date": end_date, "note": note})

        sql_insert_fitness_goal = \
            ("""
                insert into fitness_goal (user_id, start_date, end_date, note)
                values (:user_id, :start_date, :end_date, :note);
            """)

        await self.bot.db.execute(sql_insert_fitness_goal, sql_input)

    @commands.command()
    async def goal_new(self, ctx, start_date, *, note):
        # add infer end date functionality
        user_id = int(ctx.author.id)
        end_date = datetime.date(2999, 12, 31)
        start_date = datetime.date(1800, 1, 1)

        sql_input = {'user_id': user_id, 'start_date': start_date, 'end_date': end_date, 'note': note}

        print(sql_input)

        sql_fitness_goal_new = \
            ("""
                insert into fitness_goal (user_id, start_date, end_date, note)
                values (%(user_id)s, %(start_date)s, %(end_date)s, %(note)s);
            """)

        print(sql_fitness_goal_new)

        new_query, positional_args = db_manager.pyformat2psql(sql_fitness_goal_new, sql_input)

        # await self.bot.db.execute(sql_fitness_goal_new, user_id, start_date, end_date, note)
        await self.bot.db.execute(new_query, *positional_args)

    @commands.command()
    async def goal(self, ctx, fitness_goal_id = None):
        user_id = ctx.author.id
        sql_fetch_goal = None

        if fitness_goal_id is None:
            sql_fetch_goal = \
                (f"""
                    select fitness_goal_id,
                        start_date,
                        end_date,
                        note
                    from fitness_goal
                    where user_id = {user_id}
                    order by end_date desc
                    limit 1
                """)
        else:
            sql_fetch_goal = \
                (f"""
                    select
                        fitness_goal_id,
                        start_date,
                        end_date,
                        note
                    from fitness_goal
                    where fitness_goal_id = {fitness_goal_id};
                """)

        row = await self.bot.db.fetchrow(sql_fetch_goal)
        await ctx.send(row)

    @commands.command()
    async def goal_history(self, ctx):
        user_id = ctx.author.id

        sql_goal_history = \
            (f"""
                select * 
                from fitness_goal
                where user_id = {user_id}
                order by end_date desc;
            """)

        result = await self.bot.db.fetch(sql_goal_history)

        await ctx.send(result)

    @commands.command()
    async def goal_update(self, ctx, fitness_goal_id, start_date, *, note):
        # don't let users update records that aren't theirs
        # maybe break this out into goal_update_start_date, goal_update_note, etc
        # add helper function to handle updating end_dates for inferring
        sql_update_fitness_goal = \
            (f"""
                update fitness_goal
                set start_date = '{start_date}',
                    note = '{note}'
                where fitness_goal_id = {fitness_goal_id}
            """)

        await self.bot.db.execute(sql_update_fitness_goal)
        await ctx.send("I updated the record")

    @commands.command()
    async def goal_delete(self, ctx, fitness_goal_id):
        # first arg is goal id, delete goal, update inferred end dates

        fitness_goal_id = fitness_goal_id

        sql_delete_fitness_goal = \
            (f"""
                delete from fitness_goal
                where fitness_goal_id = {fitness_goal_id};
            """)

        await self.bot.db.execute(sql_delete_fitness_goal)


async def setup(bot):
    await bot.add_cog(Basic(bot))
