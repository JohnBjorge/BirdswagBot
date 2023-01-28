import discord
from discord.ext import commands
import asyncpg
import logging
from helpers import help_command


logger = logging.getLogger(__name__)


class FitnessBot(commands.Bot):

    def __init__(self, **options):
        self.db = None

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="$",
            help_command=help_command.CustomHelpCommand(),  # just remove if I want default help command
            description="This is the Fitness Bot",
            intents=intents,
            **options
        )

    async def create_db_pool(self, database, user, password):
        self.db = await asyncpg.create_pool(database=database, user=user, password=password, host="127.0.0.1")
