from . import Command
from .. import utils

from random import sample

class Randomize(Command):
    names = ["randomize"]
    description = "Assign random teams and random roles to the 10 players in your voice channel. Sorts you into two calls."
    usage = "!randomize"
    requires_mod = True
    requires_server = True

    async def execute_command(self, client, msg, content):
        if msg.author.voice is None:
            await msg.author.send(
                client.messages["caller_not_connected"]
            )
            return
        
        connected_members = msg.author.voice.channel.members

        if len(connected_members) != 10:
            utils.log(self, "Need exactly 10 to randomize")
            await msg.channel.send(
                client.messages["need_ten_players"]
            )
            return
        
        temp = sample(connected_members, k=len(connected_members))

        roles_list = ["Top", "Jgl", "Mid", "Bot", "Sup"]

        team_1, team_2 = temp[:5], temp[5:]

        await msg.channel.send(
            "**Team 1**:\n" +
            "".join(role + ": " + member.name + "\n" for role, member in zip(roles_list, team_1)) +
            "\n**Team 2**:\n" +
            "".join(role + ": " + member.name + "\n" for role, member in zip(roles_list, team_2))
        )

        team_1_vc = client.get_channel(client.config["TEAM_1_ID"])
        team_2_vc = client.get_channel(client.config["TEAM_2_ID"])

        for member in team_1:
            try:
                await member.move_to(team_1_vc)
            except:
                utils.log(self, f"Could not move {member.name} to Team 1")
        
        for member in team_2:
            try:
                await member.move_to(team_2_vc)
            except:
                utils.log(self, f"Could not move {member.name} to Team 2")