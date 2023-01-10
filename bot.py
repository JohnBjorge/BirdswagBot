import discord
from discord.ext import commands
import asyncpg
import logging
from helpers import help_command
import aiocron

logger = logging.getLogger(__name__)


class BirdswagBot(commands.Bot):

    def __init__(self, **options):
        self.db = None

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="$",
            help_command=help_command.CustomHelpCommand(),  # just remove if I want default help command
            description="This is the Birdswag Bot",
            intents=intents,
            **options
        )

    async def create_db_pool(self, database, user, password):
        self.db = await asyncpg.create_pool(database=database, user=user, password=password, host="127.0.0.1")

    async def setup_hook(self):
        cron = CronJobs(self)

    async def close(self):
        await super().close()


# you can also import this from else where.
class CronJobs():
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # print Hello world 20secs.
        @aiocron.crontab("* * * * * */20")
        async def hello_world():
            await bot.get_channel(1045906913080115225).send("Hello World!")
