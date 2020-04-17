import sys
import discord
from discord import ChannelType
import json
import subprocess
import asyncio
import traceback

from .triggers import msg_triggers, reaction_triggers
from .triggers import utils
from .triggers.commands import invalid_command


class GhostClient(discord.Client):
    def __init__(
        self,
        config_filename="config/config.json",
        roles_filename="config/roles.json",
        messages_filename="config/messages.json",
        log_filename="nocbot.log",
        path=sys.path[0] + "/"
    ):
        super().__init__()
        config_filename = path + config_filename
        roles_filename = path + roles_filename
        messages_filename = path + messages_filename
        self.log_filename = path + log_filename
        with open(log_filename, "w") as fake_news:
            pass
        with open(config_filename, "r") as config_file:
            self.config = json.load(config_file)
        
        with open(roles_filename, "r") as roles_file:
            self.roles = json.load(roles_file)
        
        with open(messages_filename, "r") as messages_file:
            self.messages = json.load(messages_file)
        
        self.command_channels_only = len(self.config["command_channels"]) > 0

        utils.setup_data_dragon(self)

        print("[+] Initialization complete.")
        if self.command_channels_only:
            print("[#] COMMAND CHANNEL ONLY ENABLED: Commands can only be run in specified channels. Edit config.json to add/remove channels.")

    async def on_ready(self):
        if len(sys.argv) > 1:
            args = ["kill", "-9"]
            args.extend(sys.argv[1:])
            subprocess.call(args)

        self.SERVER = self.get_guild(self.config["SERVER_ID"])

        print(f"[+] Connected to {self.SERVER.name} as {self.user}!")
    
    async def on_message(self, msg):

        if msg.author.bot:
            return

        replied = False
        for trigger in msg_triggers:
            try:
                matches, idx = await trigger.matches_call(self, msg)
                if matches:
                    await trigger.execute_message(self, msg, idx)
                    replied = True
                    break
            except Exception as e:
                await utils.log_traceback(self, self)
                replied = True
                break
        
        """
        if not replied:
            if not await invalid_command(self, msg):
                utils.print_error("", f"A valid command was not replied to:\n{msg.content}")
        """
    async def on_raw_reaction_add(self, reaction):
        user = self.SERVER.get_member(reaction.user_id)
        
        if not user: # user is not in the cache
            user = await self.fetch_user(reaction.user_id)

        if user.bot:
            return

        channel = self.get_channel(reaction.channel_id)
        if not channel:  # channel is not in the cache
            channel = await self.fetch_channel(reaction.channel_id)

        msg = await channel.fetch_message(reaction.message_id)

        for trigger in reaction_triggers:
            try:
                result = await trigger.execute_reaction(
                    self, reaction, channel, msg, user
                )
                # if you delete the message reacted to, return False
                if result is False:
                    break
            except Exception as e:
                utils.log_traceback(self, self)
