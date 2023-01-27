from discord.ext import commands
import logging
import discord


logger = logging.getLogger(__name__)


# todo: improve and build out help commands!
class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    # async def send_bot_help(self, mapping):
    #     for cog in mapping:
    #         if cog is not None:
    #             await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in mapping[cog]]}')
    #
    #             # todo: make an embed for help commands
    #             # embed = discord.Embed(title='TITLE_HERE', description='DESCRIPTION_HERE', color=BLUE)
    #             # for cog, cmds in mapping.items():
    #             #     name = cog.qualified_name
    #             #     embed.add_field(name=name, value=f"{len(cmds)} commands")
    #             #     embed.set_thumbnail(url='IMAGE_URL_HERE')
    #
    #             # channel = self.get_destination()
    #             # await channel.send(embed=embed)

    async def send_bot_help(self, mapping):
        """
        This is triggered when !help is invoked.

        This example demonstrates how to list the commands that the member invoking the help command can run.
        """
        filtered = await self.filter_commands(self.context.bot.commands, sort=True) # returns a list of command objects
        names = [command.name for command in filtered] # iterating through the commands objects getting names
        available_commands = "\n".join(names) # joining the list of names by a new line
        embed = discord.Embed(description=available_commands)
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_group_help(self, group):
        await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')

    async def send_command_help(self, command):
        await self.get_destination().send(command.name)
