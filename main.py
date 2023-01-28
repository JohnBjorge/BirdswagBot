import os
import logging
import discord
from dotenv import load_dotenv
from bot import FitnessBot
import asyncio
import argparse


# possibly useful security doc for discord bots
# https://gist.github.com/apple502j/d1330461e7e8ad6532cb62a670d06a5a


async def load_extensions(bot):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")


def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local", help="option to run on local machine", action="store_true")
    parser.add_argument("-d", "--debug", help="option to run on debug mode for detailed logging", action="store_true")
    args = parser.parse_args()
    return args


def setup_logging(debug_flag):
    logger = logging.getLogger()  # root logger

    handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')

    if debug_flag:
        discord.utils.setup_logging(handler=handler, level=logging.DEBUG, root=True)
        discord.utils.setup_logging(level=logging.DEBUG, root=True)
    else:
        discord.utils.setup_logging(handler=handler, level=logging.INFO, root=True)
        discord.utils.setup_logging(level=logging.INFO, root=True)

    return logger


async def main():
    args = parse_command()
    local_flag = args.local
    debug_flag = args.debug

    logger = setup_logging(debug_flag)

    bot = FitnessBot()

    load_dotenv()

    discord_token = os.getenv('DISCORD_TOKEN')
    database = os.getenv('DATABASE')
    db_user = os.getenv('DB_USER_GC')
    db_password = os.getenv('DB_PASSWORD_GC')

    if local_flag:
        discord_token = os.getenv('DISCORD_TOKEN_LOCAL')
        db_user = os.getenv('DB_USER_LOCAL')
        db_password = os.getenv('DB_PASSWORD_LOCAL')

    async with bot:
        await load_extensions(bot)
        await bot.create_db_pool(database, db_user, db_password)
        logger.info("Connection to database established, starting up bot!")
        await bot.start(discord_token)

if __name__ == "__main__":
    asyncio.run(main())
