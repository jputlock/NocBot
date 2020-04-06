from . import Command
from .. import utils

class Purge(Command):
    names = ["purge"]
    description = "MOD+ ONLY: Purges the last x messages from a channel."
    usage = "!purge <number of messages>"
    requires_mod = True
    requires_server = True

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.author.send(
                f"Usage: {self.usage}"
            )
            return

        arr = content.split(" ")
        try:
            num = int(arr[0]) + 1
            await msg.channel.purge(limit=num)
        except:
            utils.log(self, f"Could not parse # for purge command, content = \'{content}\'")