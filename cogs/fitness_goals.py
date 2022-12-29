from discord.ext import commands
from helpers import db_manager
from helpers import clean_data
from datetime import date


class FitnessGoals(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fitness_goals cog ready")

    @commands.command()
    async def join(self, ctx):
        # check if user already exists, if not proceed, otherwise exit out
        user_id = ctx.author.id
        user_exist = await db_manager.fitness_goal_exist_user_id(self, user_id)

        if not user_exist:
            start_date = date.today()
            end_date = date(2999, 12, 31)
            note = "No goals yet"

            sql_input = dict({"user_id": user_id, "start_date": start_date, "end_date": end_date, "note": note})

            sql_insert_fitness_goal = \
                ("""
                    insert into fitness_goal (user_id, start_date, end_date, note)
                    values (%(user_id)s, %(start_date)s, %(end_date)s, %(note)s);
                """)
            query, positional_args = db_manager.pyformat_to_psql(sql_insert_fitness_goal, sql_input)

            await self.bot.db.execute(query, *positional_args)
            print("I created a new fitness_goal entry for you")
        else:
            print("User already exists, sorry!")

    @commands.command()
    async def goal_new(self, ctx, start_date, *, note):
        user_id = ctx.author.id
        end_date = date(2999, 12, 31)

        start_date = clean_data.clean_date(start_date)

        sql_input = {'user_id': user_id, 'start_date': start_date, 'end_date': end_date, 'note': note}

        sql_fitness_goal_new = \
            ("""
                insert into fitness_goal (user_id, start_date, end_date, note)
                values (%(user_id)s, %(start_date)s, %(end_date)s, %(note)s);
            """)

        query, positional_args = db_manager.pyformat_to_psql(sql_fitness_goal_new, sql_input)

        await self.bot.db.execute(query, *positional_args)

        await db_manager.fitness_goal_update_end_dates(self)

        print("I created a new goal for you")

    @commands.command()
    async def goal(self, ctx, fitness_goal_id=None):
        user_id = ctx.author.id
        fitness_goal_id = int(fitness_goal_id)

        if fitness_goal_id is None:
            sql_fetch_goal = \
                ("""
                    select fitness_goal_id,
                        start_date,
                        end_date,
                        note
                    from fitness_goal
                    where user_id = %(user_id)s
                    order by end_date desc
                    limit 1
                """)
            sql_input = {"user_id": user_id}
        else:
            sql_fetch_goal = \
                ("""
                    select
                        fitness_goal_id,
                        start_date,
                        end_date,
                        note
                    from fitness_goal
                    where fitness_goal_id = %(fitness_goal_id)s;
                """)

            sql_input = {"fitness_goal_id": fitness_goal_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_fetch_goal, sql_input)

        row = await self.bot.db.fetchrow(query, *positional_args)
        await ctx.send(row)

    @commands.command()
    async def goal_history(self, ctx):
        user_id = ctx.author.id

        sql_goal_history = \
            ("""
                select * 
                from fitness_goal
                where user_id = %(user_id)s
                order by end_date desc;
            """)

        sql_input = {"user_id": user_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_goal_history, sql_input)

        result = await self.bot.db.fetch(query, *positional_args)

        await ctx.send(result)

    # maybe break this out into goal_update_start_date, goal_update_note, etc
    @commands.command()
    async def goal_update(self, ctx, fitness_goal_id, start_date, *, note):
        user_id = ctx.author.id

        fitness_goal_id = int(fitness_goal_id)

        fitness_goal_id_matches_user_id = await db_manager.fitness_goal_id_matches_user_id(self, fitness_goal_id, user_id)

        start_date = clean_data.clean_date(start_date)

        if fitness_goal_id_matches_user_id:
            sql_update_fitness_goal = \
                ("""
                    update fitness_goal
                    set start_date = %(start_date)s,
                        note = %(note)s
                    where fitness_goal_id = %(fitness_goal_id)s
                """)

            sql_input = {"start_date": start_date, "note": note, "fitness_goal_id": fitness_goal_id}

            query, positional_args = db_manager.pyformat_to_psql(sql_update_fitness_goal, sql_input)

            await self.bot.db.execute(query, *positional_args)
            await db_manager.fitness_goal_update_end_dates(self)
            print("I updated a fitness_goal record")

    @commands.command()
    async def goal_delete(self, ctx, fitness_goal_id):
        user_id = ctx.author.id
        fitness_goal_id = int(fitness_goal_id)

        fitness_goal_id_matches_user_id = await db_manager.fitness_goal_id_matches_user_id(self, fitness_goal_id, user_id)

        if fitness_goal_id_matches_user_id:
            sql_delete_fitness_goal = \
                ("""
                    delete from fitness_goal
                    where fitness_goal_id = %(fitness_goal_id)s;
                """)

            sql_input = {"fitness_goal_id": fitness_goal_id}

            query, positional_args = db_manager.pyformat_to_psql(sql_delete_fitness_goal, sql_input)

            await self.bot.db.execute(query, *positional_args)

            await db_manager.fitness_goal_update_end_dates(self)
            print("I deleted a fitness goal")


async def setup(bot):
    await bot.add_cog(FitnessGoals(bot))
