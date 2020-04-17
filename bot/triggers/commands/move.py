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
        
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return

        # grab the current vc

        if msg.author.voice is None:
            await msg.channel.send(
                client.messages["caller_not_connected"]
            )
            return

        # grab current vc members

        current_channel_members = msg.author.voice.channel.members

        # grab other vc from names

        target_vc = None

        for channel in client.SERVER.channels:
            if channel.name.lower() == content.lower() and type(channel) is VoiceChannel:
                target_vc = channel
                # utils.log(self, f"Found channel named \'{content}\' with ID {channel.id}")
                break

        if not target_vc:
            utils.log(self, f"Voice channel \'{content}\' not found.", client)
            await msg.channel.send(
                client.messages["voice_channel_not_found"]
            )
            return

        # move to the other vc

        for member in current_channel_members:
            try:
                await member.move_to(target_vc)
            except:
                utils.log(self, f"Could not move {member.name} to {target_vc.name}", client)