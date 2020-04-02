from . import Command
from .. import utils

from discord import VoiceChannel

class Move(Command):
    names = ["move"]
    description = "Move all players from your channel to another"
    usage = "!move <channel_name>"
    requires_mod = True
    requires_server = True

    async def execute_command(self, client, msg, content):

        target_channel_name = content.split(" ")[0]

        # grab the current vc

        if msg.author.voice is None:
            await msg.channel.send(
                client.messages["caller_not_connected"]
            )
            return

        # grab current vc members

        members = msg.author.voice.channel.members

        # grab other vc from names

        target_vc = None

        for channel in self.SERVER.channels:
            if channel.name.lower() == target_channel_name.lower() and type(channel) is VoiceChannel:
                target_vc = channel
                break

        if not target_vc:
            utils.print_error(self, f"Voice channel \'{target_channel_name}\' not found.")
            await msg.channel.send(
                client.messages["voice_channel_not_found"]
            )
            return

        # move to the other vc

        all_members = target_vc.members

        for member in all_members:
            try:
                await member.move_to(target_vc)
            except:
                utils.print_error(self, f"Could not move {member.name} to {target_vc.name}")