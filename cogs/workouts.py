from discord.ext import commands
import discord
from helpers import core_tables
from helpers import db_manager
from helpers import clean_data
from helpers import embeds
import logging
from cogs import basic
import csv
import os


logger = logging.getLogger(__name__)


class Workouts(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

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
            logger.debug(f'Fetching most recent workout for user_id: {user_id}')
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
            logger.debug(f'Fetching workout with workout_id: {workout_id}')

        query, positional_args = db_manager.pyformat_to_psql(sql_fetch_workout, sql_input)

        result = await self.bot.db.fetchrow(query, *positional_args)

        content, embed = embeds.embed_workout(ctx, result["workout_id"], result["date"], result["type_of_workout"], result["difficulty"], result["note"])

        await ctx.send(content=content, embed=embed)

    # todo: allow csv or txt parameter? allow time period parameter?
    @commands.command()
    async def workout_history(self, ctx, file_format='txt'):
        user_id = ctx.author.id

        sql_workout_history = \
            ("""
                select workout_id,
                date,
                type_of_workout,
                difficulty,
                note
                from workout
                where user_id = %(user_id)s
                order by date desc;
            """)

        sql_input = {"user_id": user_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_workout_history, sql_input)

        logger.debug(f'Fetching workout history for user_id: {user_id}')

        result = await self.bot.db.fetch(query, *positional_args)

        tabulated_data = clean_data.tabulate_history(result)

        message = f'Output of your workout history <@{user_id}>'

        filename = 'temp/files/workout_history_' + str(user_id) + '.txt'

        if file_format == 'txt':
            with open(filename, 'w') as f:
                f.write(tabulated_data)

            await ctx.send(message, file=discord.File(filename, filename='workout_history.txt'))

            os.remove(filename)

        elif file_format == 'csv':
            # todo: csv dump, should be possible by making tabulate output to tsv then change to csv
            # todo: one issue was tsv doesn't allow new lines so some notes have newlines which means we need to
            #  replace the new line character before tabulate step with __NEWLINE__ then post tabulate and post
            #  conversion to csv we replace __NEWLINE__ to \n
            pass

    # todo: restrict type_of_workout to valid items and notify user if wrong, same for difficulty
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

        logger.debug(f'Inserting new workout for user_id: {user_id}\n'
                     f'Date: {date}\n'
                     f'Type of Workout: {type_of_workout}\n'
                     f'Difficulty: {difficulty}\n'
                     f'Note: {note}')

        await self.bot.db.execute(query, *positional_args)

        workout_id = await db_manager.newest_workout(self, user_id)

        content, embed = embeds.embed_workout_new(ctx, workout_id, date, type_of_workout, difficulty, note)

        await ctx.send(content=content, embed=embed)

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

            logger.debug(f'Deleting workout with workout_id: {workout_id}')

            await self.bot.db.execute(query, *positional_args)

    # # todo: implement update command, need to consider how emoji voting will play into this, assuming it does and
    # #  which fields you are allowed to update
    # # todo: conssider scrapping this, too complex?
    # @commands.command()
    # async def workout_update(self, ctx, start_date, *, note):
    #     pass

    # todo: allow csv or txt parameter? allow time period parameter?
    # todo: can't preview txt file on mobile and viewing isn't as block so pretty annoying, maybe a workaround is
    #       to have a recent option that gives most recent workout that way we can just dump it out for if you
    #       are at the gym on your phone and need info on the fly
    @commands.command()
    async def workout_search(self, ctx, *, note_search_term):
        user_id = ctx.author.id

        # note: pyformat_to_psql function didn't like something about containing percent signs or escaped quotes
        #  so hacky-ish workaround to build the search term with percent pattern signs
        note_search_term = "%" + str(note_search_term).lower() + "%"

        sql_workout_search = \
            ("""
                select workout_id,
                date,
                type_of_workout,
                difficulty,
                note
                from workout
                where user_id = %(user_id)s
                and lower(note) like %(note_search_term)s
                order by date desc;
            """)

        sql_input = {"user_id": user_id, "note_search_term": note_search_term}

        query, positional_args = db_manager.pyformat_to_psql(sql_workout_search, sql_input)

        logger.debug(f'Fetching workout history for user_id: {user_id}')

        result = await self.bot.db.fetch(query, *positional_args)

        if len(result) == 0:
            message = f'No matches found <@{user_id}>\nSearch pattern: {note_search_term}'
            await ctx.send(message)

        else:
            tabulated_data = clean_data.tabulate_history(result)

            message = f'Output of your workout search <@{user_id}>\nSearch pattern: {note_search_term}'

            filename = 'temp/files/workout_search_' + str(user_id) + '.txt'

            with open(filename, 'w') as f:
                f.write(tabulated_data)

            await ctx.send(message, file=discord.File(filename, filename='workout_search.txt'))

            os.remove(filename)


async def setup(bot):
    await bot.add_cog(Workouts(bot))
