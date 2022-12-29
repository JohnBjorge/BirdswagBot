from discord.ext import commands
from helpers import core_tables
from helpers import db_manager
from helpers import clean_data


class Workouts(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Workouts cog ready")

    @commands.command()
    async def workout(self, ctx, workout_id=None):
        user_id = ctx.author.id

        if workout_id is None:
            sql_fetch_workout = \
                ("""
                    select workout_id,
                        user_id,
                        date,
                        type_of_workout,
                        difficulty,
                        note
                    from workout
                    where user_id = %(user_id)s
                    order by date desc
                    limit 1
                """)
            sql_input = {"user_id": user_id}
        else:
            sql_fetch_workout = \
                ("""
                    select workout_id,
                        user_id,
                        date,
                        type_of_workout,
                        difficulty,
                        note
                    from workout
                    where workout_id = %(workout_id)s;
                """)

            workout_id = int(workout_id)
            sql_input = {"workout_id": workout_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_fetch_workout, sql_input)

        row = await self.bot.db.fetchrow(query, *positional_args)
        await ctx.send(row)

    @commands.command()
    async def workout_history(self, ctx):
        user_id = ctx.author.id

        # todo: change * to specific columns
        sql_workout_history = \
            ("""
                        select * 
                        from workout
                        where user_id = %(user_id)s
                        order by date desc;
                    """)

        sql_input = {"user_id": user_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_workout_history, sql_input)

        result = await self.bot.db.fetch(query, *positional_args)

        await ctx.send(result)

    @commands.command()
    async def workout_new(self, ctx, date, type_of_workout, difficulty, *, note):
        user_id = ctx.author.id

        date = clean_data.clean_date(date)

        difficulty = int(difficulty)

        sql_input = {'user_id': user_id, 'date': date, 'type_of_workout': type_of_workout, 'difficulty': difficulty, "note": note}

        sql_workout_new = \
            ("""
                insert into workout (user_id, date, type_of_workout, difficulty, note)
                values (%(user_id)s, %(date)s, %(type_of_workout)s, %(difficulty)s, %(note)s);
            """)

        query, positional_args = db_manager.pyformat_to_psql(sql_workout_new, sql_input)

        await self.bot.db.execute(query, *positional_args)

        print("I created a new workout for you")

    @commands.command()
    async def workout_delete(self, ctx, workout_id):
        user_id = ctx.author.id
        workout_id = int(workout_id)

        workout_id_matches_user_id = await db_manager.workout_id_matches_user_id(self, workout_id, user_id)

        if workout_id_matches_user_id:
            sql_delete_workout = \
                ("""
                    delete from workout
                    where workout_id = %(workout_id)s;
                """)

            sql_input = {"workout_id": workout_id}

            query, positional_args = db_manager.pyformat_to_psql(sql_delete_workout, sql_input)

            await self.bot.db.execute(query, *positional_args)

            print("I deleted a workout")

    # todo: implement update command, need to consider how emoji voting will play into this, assuming it does and
    #  which fields you are allowed to update
    @commands.command()
    async def workout_update(self, ctx, start_date, *, note):
        pass


async def setup(bot):
    await bot.add_cog(Workouts(bot))
