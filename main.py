import os
import logging
import discord
from dotenv import load_dotenv
from bot import BirdswagBot
import asyncio
import asyncpg
import argparse


async def load_extensions(bot):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")


def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local", help="option to run on local machine", action="store_true")
    args = parser.parse_args()
    return args


async def main():
    args = parse_command()
    local_flag = args.local

    handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')

    discord.utils.setup_logging(handler=handler, level=logging.DEBUG, root=False)
    discord.utils.setup_logging(level=logging.DEBUG, root=False)

    bot = BirdswagBot()

    load_dotenv()
    discord_token = os.getenv('DISCORD_TOKEN')
    database = os.getenv('DATABASE')
    db_user = os.getenv('DB_USER_GC')
    db_password = os.getenv('DB_PASSWORD_GC')

    if local_flag:
        db_user = os.getenv('DB_USER_LOCAL')
        db_password = os.getenv('DB_PASSWORD_LOCAL')

    async with bot:
        await load_extensions(bot)

#        https: // stackoverflow.com / questions / 71625788 / accesing - loop - attribute - in -non -async-contexts
        await bot.create_db_pool(database, db_user, db_password)

        await bot.start(discord_token)

if __name__ == "__main__":
    asyncio.run(main())

