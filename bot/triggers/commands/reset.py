from . import Command
from .. import utils

class Reset(Command):
    names = ["reset"]
    description = "Reset players from their team channels to the designated lobby channel."
    usage = "!reset"
    requires_mod = True
    requires_server = True

    async def execute_command(self, client, msg, content):
        lobby_vc = client.get_channel(client.config["LOBBY_ID"])
        team_1_vc   = client.get_channel(client.config["TEAM_1_ID"])
        team_2_vc   = client.get_channel(client.config["TEAM_2_ID"])

        all_members = team_1_vc.members + team_2_vc.members

        print("[RESET] Moving these users to the lobby:", [member.name for member in all_members])

        for member in all_members:
            try:
                await member.move_to(lobby_vc)
            except:
                utils.print_error(f"Could not move {member.name} to the lobby channel.")