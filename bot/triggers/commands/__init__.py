from ..message_trigger import MessageTrigger
from .. import utils
import re
import discord
from riotwatcher import LolWatcher, ApiError
import os

global_watcher = LolWatcher(os.getenv("LEAGUE_TOKEN"))

class Command():
    prefixes = ["!"]
    requires_mod = False
    requires_server = False

    async def matches_call(self, client, msg):
        for name in self.names:
            for prefix in self.prefixes:
                if re.match(f"^{prefix}{name}\\b", msg.content.lower()):
                    return (True, len(name) + len(prefix))
        return (False, 0)

    async def execute_message(self, client, msg, idx):

        in_dm = msg.channel.type is discord.ChannelType.private

        if self.requires_server and in_dm:
            await msg.channel.send(
                client.messages["requires_server"]
            )
            return

        if (
            not in_dm and
            client.command_channels_only and
            msg.channel.id not in client.config["command_channels"] and
            not utils.user_is_mod(client, msg.author) # mods can use commands in any channel
        ):
            author = msg.author
            await msg.delete()
            await author.send(
                client.messages["command_channels_only"]
            )
            return

        if self.requires_mod and not utils.user_is_mod(client, msg.author):
            await msg.channel.send(client.messages["invalid_permissions"])
            return

        await self.execute_command(client, msg, msg.clean_content[idx:].strip())
    
    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other):
        return self.names[0] < other.names[0]

class LeagueAPICommand(Command):
    watcher = global_watcher

from .coinflip import Coinflip
from .clash import Clash
from .draft import Draft
from .move import Move
from .purge import Purge
from .randomize import Randomize
from .reset import Reset

# Commands will auto alphabetize
all_commands = [
    Coinflip(),
    Clash(),
    Draft(),
    Move(),
    Purge(),
    Randomize(),
    Reset(),
]
all_commands.sort()

async def invalid_command(client, msg):
    if msg.author.bot or len(msg.content) < 2 or msg.content[0] != "!":
        return False

    await msg.channel.send(
        client.messages["invalid_command"].format(utils.sanitized(msg.content.strip()))
    )
    return True