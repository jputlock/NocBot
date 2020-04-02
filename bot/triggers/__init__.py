from .commands.help import Help
from .commands import all_commands
from .commands.draft import Draft

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

reaction_triggers = [
    Draft(),
]
