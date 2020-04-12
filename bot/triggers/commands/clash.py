from . import Command
from .. import utils
import json
import discord
from requests import HTTPError

class Clash(Command):
    names = ["clash"]
    description = "Get the information about the clash team that a player is on."
    usage = "!clash <summoner>"
    requires_server = True

    def generate_team_msg(self, client, team):

        players = {}

        for player in team['players']:
            summoner = None

            try:
                summoner = self.dragon.watcher.summoner.by_id(client.config["region"], player['summonerId'])
            except HTTPError as e:
                utils.log(self, "An HTTP Error has occurred trying to retrieve a team member.")
                return

            player_name = summoner['name']
            

            clash_summoner = None

            try:
                clash_summoner = self.dragon.watcher.clash.by_summoner_id(client.config["region"], player['summonerId'])[0]
            except HTTPError as e:
                utils.log(self, "An HTTP Error has occurred trying to retrieve a team member.")
                return
            
            players[player_name] = {
                "position": clash_summoner['position'],
                "captain": (clash_summoner['role'] == "CAPTAIN")
            }
        
        roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY", "UNSELECTED"]
        desc = ""
        i = 0
        while i < len(roles):
            for player in players.keys():
                if players[player]['position'] == roles[i]:
                    desc += f"{roles[i]} - {player}"
                    if players[player]['captain']:
                        desc += " (CAPTAIN)"
                    desc += "\n"
            i += 1

        embed = discord.Embed(
            title=f"({team['abbreviation']}) {team['name']}",
            description=desc
        )

        content = "<https://na.op.gg/multi/query=" + "%2C".join([player.replace(" ", "") for player in players]) + ">"

        return content, embed

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return

        self.dragon = utils.global_dragon
        
        lookup_summoner = None

        try:
            lookup_summoner = self.dragon.watcher.summoner.by_name(client.config["region"], content)
        except HTTPError as e:
            utils.log(self, "An HTTP Error has occurred trying to get the summoner.")
            return

        if not lookup_summoner:
            utils.log(self, "Can not receive summoner from League API Endpoint")
            return
        
        """
        returns a list of dictionaries
        [
            {
                'summonerId': str,
                'teamId': str,
                'position': str,
                'role': str
            }
        ]
        """

        clash_summoner = None
        
        try:
            clash_summoner = self.dragon.watcher.clash.by_summoner_id(client.config["region"], lookup_summoner['id'])[0]
        except HTTPError as e:
            utils.log(self, "An HTTP Error has occurred trying to get the player.")
            return
        
        if not clash_summoner:
            utils.log(self, "Can not receive player from Clash API Endpoint")
            return
        
        team = None
        
        try:
            team = self.dragon.watcher.clash.by_team_id(client.config["region"], clash_summoner['teamId'])
        except HTTPError as e:
            utils.log(self, "An HTTP Error has occurred trying to get the team.")
            return
        
        if not team:
            utils.log(self, "Can not receive team from Clash API Endpoint")
            return

        content, embed = self.generate_team_msg(client, team)

        await msg.channel.send(
            content=content, embed=embed
        )

        