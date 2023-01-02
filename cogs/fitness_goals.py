from discord.ext import commands
from helpers import db_manager
from helpers import clean_data
from datetime import date
import logging
from cogs import basic


logger = logging.getLogger(__name__)


class FitnessGoals(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def join(self, ctx):
        # check if user already exists, if not proceed, otherwise exit out
        user_id = ctx.author.id
        user_exist = await db_manager.fitness_goal_exist_user_id(self, user_id)

        if not user_exist:
            start_date = date.today()
            end_date = date(2999, 12, 31)
            note = "No goals yet"

            sql_input = {"user_id": user_id, "start_date": start_date, "end_date": end_date, "note": note}

            sql_insert_fitness_goal = \
                ("""
                    insert into fitness_goal (user_id, start_date, end_date, note)
                    values (%(user_id)s, %(start_date)s, %(end_date)s, %(note)s);
                """)
            query, positional_args = db_manager.pyformat_to_psql(sql_insert_fitness_goal, sql_input)

            logger.debug(f'Inserting new fitness goal for user_id: {user_id}\n'
                         f'Start Date: {start_date}\n'
                         f'End Date: {end_date}\n'
                         f'Note: {note}')

            await self.bot.db.execute(query, *positional_args)

            fitness_goal_id = await db_manager.newest_fitness_goal(self, user_id)

            content, embed = basic.embed_join(ctx, fitness_goal_id, user_id, start_date, end_date, note)

            await ctx.send(content=content, embed=embed)
        else:
            await ctx.send("You have already joined. Try running $goal to see your current fitness goal.")
            logger.debug(f'User has already joined, user_id: {user_id}\n')

    @commands.command()
    async def goal(self, ctx, fitness_goal_id=None):
        user_id = ctx.author.id

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
            logger.debug(f'Fetching fitness goal for user_id: {user_id}')
        else:
            sql_fetch_goal = \
                ("""
                    select fitness_goal_id,
                        start_date,
                        end_date,
                        note
                    from fitness_goal
                    where fitness_goal_id = %(fitness_goal_id)s;
                """)

            fitness_goal_id = int(fitness_goal_id)
            sql_input = {"fitness_goal_id": fitness_goal_id}
            logger.debug(f'Fetching fitness goal for fitness_goal_id: {fitness_goal_id}')

        query, positional_args = db_manager.pyformat_to_psql(sql_fetch_goal, sql_input)

        result = await self.bot.db.fetchrow(query, *positional_args)

        content, embed = basic.embed_goal(ctx, result["fitness_goal_id"], result["start_date"], result["end_date"], result["note"])

        await ctx.send(content=content, embed=embed)

    @commands.command()
    async def goal_history(self, ctx):
        user_id = ctx.author.id

        # todo: change * to specific columns
        sql_goal_history = \
            ("""
                select * 
                from fitness_goal
                where user_id = %(user_id)s
                order by end_date desc;
            """)

        sql_input = {"user_id": user_id}

        query, positional_args = db_manager.pyformat_to_psql(sql_goal_history, sql_input)

        logger.debug(f'Fetching fitness_goal history for user_id: {user_id}')

        result = await self.bot.db.fetch(query, *positional_args)

        await ctx.send(result)

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

        logger.debug(f'Inserting new fitness goal for user_id: {user_id}\n'
                     f'Start Date: {start_date}\n'
                     f'End Date (placeholder, to be updated): {end_date}\n'
                     f'Note: {note}\n')

        await self.bot.db.execute(query, *positional_args)

        await db_manager.fitness_goal_update_end_dates(self)

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

            logger.debug(f'Deleting fitness goal with fitness_goal_id: {fitness_goal_id}')

            await self.bot.db.execute(query, *positional_args)

            await db_manager.fitness_goal_update_end_dates(self)

    # todo: maybe break this out into goal_update_start_date, goal_update_note, etc
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


async def setup(bot):
    await bot.add_cog(FitnessGoals(bot))
