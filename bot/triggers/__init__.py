from .commands.help import Help
from .commands import all_commands
from .commands.draft import Draft
from .commands.bets import Bets

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

reaction_triggers = [
    Bets(),
    Draft(),
]
reaction_triggers.sort()
