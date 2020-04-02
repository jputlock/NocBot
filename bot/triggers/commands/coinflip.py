from . import Command
from .. import utils

from random import randint

class Coinflip(Command):
    names = ["coinflip", "cointoss"]
    description = "Flips a coin. Returns HEADS or TAILS."
    usage = "!coinflip"

    async def execute_command(self, client, msg, content):
        await msg.channel.send(
            "HEADS" if randint(0, 1) == 0 else "TAILS"
        )
    