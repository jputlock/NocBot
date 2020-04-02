from . import LeagueAPICommand
from .. import utils
import json

class Clash(LeagueAPICommand):
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

        
        lookup_summoner = self.watcher.summoner.by_name(client.config["region"], player)

        if not lookup_summoner:
            utils.print_error(self, "Can not receive summoner from League API Endpoint")
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
        team = self.watcher.clash.by_summoner_id(client.config["region"], lookup_summoner['id'])
        
        if not team:
            utils.print_error(self, "Can not receive team from Clash API Endpoint")
            return

        players = []

        for player in team:
            summoner = self.watcher.summoner.by_id(client.config["region"], player['summonerId'])

            players.append(summoner.name.replace(" ", ""))
            # self.generate_player_embed(summoner)
        
        await msg.channel.send(
            "https://na.op.gg/multi/query=" + "%2C".join(players)
        )

        