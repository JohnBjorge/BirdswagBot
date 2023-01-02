from discord.ext import commands
import discord
from helpers import core_tables
from helpers import db_manager
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class Basic(commands.Cog):
    db_tables = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # todo: this appears to get run multiple times and not sure when or why, documentation seems to indicate it won't
    #  necessarily get run once. Where should I instantiate these tables that only need to happen once? Right now it's
    #  fine here since I say "create or replace" or "create if not exists".
    @commands.Cog.listener()
    async def on_ready(self):
        await core_tables.create_core_tables(self)
        await core_tables.populate_table_date_dimension(self)
        await core_tables.create_updated_on_trigger(self)

        db_tables = await db_manager.show_tables(self)
        # add check for three tables otherwise throw error?

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def embed_sample(self, ctx):
        content = \
            """You can~~not~~ do `this`.```py\nAnd this.\nprint('Hi')```\n*italics* or _italics_     __*underline italics*__\n**bold**     __**underline bold**__\n***bold italics***  __***underline bold italics***__\n__underline__     ~~Strikethrough~~"""""

        embed = discord.Embed(title="Hello ~~people~~ world :wave:",
                              url='https://discord.com',
                              description=""""You can use [links](https://discord.com) or emojis :smile: 😎\n```\nAnd also code blocks\n```""",
                              color=0x1036cb,
                              timestamp=datetime.today())
        embed.set_author(name="author", url='https://discord.com',
                         icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
        embed.set_image(url='https://glitchii.github.io/embedbuilder/assets/media/banner.png')

        embed.add_field(name="Field 1, *lorem* **ipsum**, ~~dolor~~", value="Field value", inline=True)
        embed.add_field(name="Field 2",
                        value="You can use custom emojis <:Kekwlaugh:722088222766923847>",
                        inline=False)
        embed.add_field(name="Inline field", value="Fields can be inline", inline=True)

        embed.add_field(name="Inline field", value="*Lorem ipsum*", inline=True)

        embed.add_field(name="Inline field", value="value", inline=True)
        embed.add_field(name="Another field", value="> Nope, didn't forget about this", inline=False)

        embed.set_footer(text="footer text", icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
        await ctx.send(content=content, embed=embed)


# todo: combine embed_workout and embed_workout_new, only difference right now is the title
def embed_workout(ctx, workout_id, date, type_of_workout, difficulty, note):
    content = \
        """"""

    embed = discord.Embed(title="Workout :saluting_face:",
                          url='',
                          description="Unique id: " + str(workout_id),
                          color=0x1036cb,
                          timestamp=datetime.today())
    embed.set_author(name=ctx.author, url="",
                     icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_image(url='')

    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Type of Workout",
                    value=type_of_workout,
                    inline=True)
    embed.add_field(name="Difficulty", value=str(difficulty) + " out of 4", inline=True)

    embed.add_field(name="Note", value="> " + note, inline=False)

    return content, embed


def embed_workout_new(ctx, workout_id, date, type_of_workout, difficulty, note):
    content = \
        """"""

    embed = discord.Embed(title="Workout Completed :saluting_face:",
                          url='',
                          description="Unique id: " + str(workout_id),
                          color=0x1036cb,
                          timestamp=datetime.today())
    embed.set_author(name=ctx.author, url="",
                     icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_image(url='')

    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Type of Workout",
                    value=type_of_workout,
                    inline=True)
    embed.add_field(name="Difficulty", value=str(difficulty) + " out of 4", inline=True)

    embed.add_field(name="Note", value="> " + note, inline=False)

    return content, embed


# todo: combine embed_join and embed_goal, only difference is title at the moment
def embed_join(ctx, fitness_goal_id, user_id, start_date, end_date, note):
    content = \
        """"""

    embed = discord.Embed(title="Fitness Goal Created :saluting_face:",
                          url='',
                          description="Unique id: " + str(fitness_goal_id),
                          color=0x1036cb,
                          timestamp=datetime.today())
    embed.set_author(name=ctx.author, url="",
                     icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_image(url='')

    embed.add_field(name="Start Date", value=start_date, inline=True)
    embed.add_field(name="End Date",
                    value=end_date,
                    inline=True)
    embed.add_field(name="Note", value="> " + note, inline=False)

    return content, embed


def embed_goal(ctx, fitness_goal_id, start_date, end_date, note):
    content = \
        """"""

    embed = discord.Embed(title="Fitness Goal :saluting_face:",
                          url='',
                          description="Unique id: " + str(fitness_goal_id),
                          color=0x1036cb,
                          timestamp=datetime.today())
    embed.set_author(name=ctx.author, url="",
                     icon_url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.set_image(url='')

    embed.add_field(name="Start Date", value=start_date, inline=True)
    embed.add_field(name="End Date",
                    value=end_date,
                    inline=True)
    embed.add_field(name="Note", value="> " + note, inline=False)

    return content, embed


async def setup(bot):
    await bot.add_cog(Basic(bot))
