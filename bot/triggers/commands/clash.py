from . import Command
from .. import utils
import json
from requests import HTTPError

class Clash(Command):
    names = ["clash"]
    description = "Get the information about the clash team that a player is on."
    usage = "!clash <summoner>"
    requires_server = True

    def generate_player_embed(self, summoner):
        pass

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return
        
        player = content.split(" ")[0]

        self.dragon = utils.global_dragon
        
        lookup_summoner = None

        try:
            lookup_summoner = self.dragon.watcher.summoner.by_name(client.config["region"], player)
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

        team = None
        
        try:
            team = self.dragon.watcher.clash.by_summoner_id(client.config["region"], lookup_summoner['id'])
        except HTTPError as e:
            utils.log(self, "An HTTP Error has occurred trying to get the team.")
            return
        
        if not team:
            utils.log(self, "Can not receive team from Clash API Endpoint")
            return

        players = []

        for player in team:
            summoner = None

            try:
                summoner = self.dragon.watcher.summoner.by_id(client.config["region"], player['summonerId'])
            except HTTPError as e:
                utils.log(self, "An HTTP Error has occurred trying to retrieve a team member.")
                return

            players.append(summoner.name.replace(" ", ""))
            # self.generate_player_embed(summoner)
        
        await msg.channel.send(
            "<https://na.op.gg/multi/query=" + "%2C".join(players) + ">"
        )

        