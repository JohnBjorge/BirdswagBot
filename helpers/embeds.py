import discord
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


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

    embed.add_field(name="Note", value=">>> " + note, inline=False)

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

    embed.add_field(name="Note", value=">>> " + note, inline=False)

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
    embed.add_field(name="Note", value=">>> " + note, inline=False)

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
    embed.add_field(name="Note", value=">>> " + note, inline=False)

    return content, embed
