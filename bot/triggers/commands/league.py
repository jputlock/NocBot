from . import Command
from .. import utils
import json
import discord
from requests import HTTPError

class League(Command):
    names = ["league"]
    description = "Get the stats of the current league game of a summoner."
    usage = "!league <summoner>"

    def get_embed(self, target, client, game):

        embed = discord.Embed

        team_1, team_2 = [], []

        for player in game['participants']:

            summoner = self.dragon.watcher.league.by_summoner(client.config['region'], player['summonerId'])

            rank = ""
            for league_entry in summoner:
                if league_entry['queueType'] == "RANKED_SOLO_5x5":
                    rank = league_entry['tier'].title() + " " + league_entry['rank']
                    break

            player['rank'] = rank

            if player['teamId'] == 100:
                team_1.append(player)
            else:
                team_2.append(player)

        desc = utils.team_names[0] + "\n" + "\n".join(
                f"{player['summonerName']} ({player['rank']}): {self.dragon.champions[player['championId']]['name']} " +
                f"[{self.dragon.summoners[player['spell1Id']]['name']}/{self.dragon.summoners[player['spell2Id']]['name']}] " +
                f"({self.dragon.runes[player['perks']['perkStyle']][player['perks']['perkIds'][0]]})"
                for player in team_1
            )

        desc += "\n" + utils.team_names[1] + "\n" + "\n".join(
                f"{player['summonerName']} ({player['rank']}): {self.dragon.champions[player['championId']]['name']} " +
                f"[{self.dragon.summoners[player['spell1Id']]['name']}/{self.dragon.summoners[player['spell2Id']]['name']}] " +
                f"({self.dragon.runes[player['perks']['perkStyle']][player['perks']['perkIds'][0]]})"
                for player in team_2
            )

        embed = discord.Embed(
            title=f"{target}'s Current Game:",
            description=desc
        )
        return embed

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return
        
        self.dragon = utils.global_dragon
        
        lookup_summoner = None
        lookup_summoner = self.dragon.watcher.summoner.by_name(client.config["region"], content)

        if not lookup_summoner:
            utils.print_error(self, "Can not receive summoner from League API Endpoint")
            return
        
        try:
            game = self.dragon.watcher.spectator.by_summoner(client.config["region"], lookup_summoner['id'])
        except HTTPError as e:
            utils.print_error(self, "Player is not in a game.")
            return
        
        if not game:
            utils.print_error(self, "Can not receive game from League API Endpoint")
            return
        
        players = [player['summonerName'] for player in game['participants']]

        await msg.channel.send(
            content="",
            embed=self.get_embed(content, client, game)
        )