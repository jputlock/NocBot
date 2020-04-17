from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
from requests import HTTPError

class Bets(Command, ReactionTrigger):
    names = ["bets"]
    description = "Starts a betting session on a player's game."
    usage = "!bets <summoner>"
    requires_server = True

    class State:

        def __init__(self):
            self.embed = None
            self.team_1_betters = []
            self.team_2_betters = []

        def parse_msg(self, client, embed):
            self.embed = embed
            for field in self.embed.fields:
                if field.name == utils.team_names[0] + " Bets":
                    for line in field.value.split("\n"):
                        if line == "Nobody!":
                            break
                        self.team_1_betters.append(
                            utils.user_from_mention(client, utils.find_first_mention(line))
                        )
                if field.name == utils.team_names[1] + " Bets":
                    for line in field.value.split("\n"):
                        if line == "Nobody!":
                            break
                        self.team_2_betters.append(
                            utils.user_from_mention(client, utils.find_first_mention(line))
                        )
                if field.name == "Match ID":
                    self.game_id = int(field.value)

        def get_embed(self):
            for i, field in enumerate(self.embed.fields):
                if field.name == utils.team_names[0] + " Bets":
                    txt = "Nobody!"
                    if len(self.team_1_betters) > 0:
                        txt = "\n".join(
                            f"{user.mention}"
                            for user in self.team_1_betters
                        )
                    self.embed.set_field_at(
                        i,
                        name=utils.team_names[0] + " Bets",
                        value=txt
                    )
                if field.name == utils.team_names[1] + " Bets":

                    txt = "Nobody!"
                    if len(self.team_2_betters) > 0:
                        txt = "\n".join(
                            f"{user.mention}"
                            for user in self.team_2_betters
                        )

                    self.embed.set_field_at(
                        i,
                        name=utils.team_names[1] + " Bets",
                        value=txt
                    )

            return self.embed
        
        def add_vote(self, team, voter):
            if team == 1:
                self.team_1_betters.append(voter)
            elif team == 2:
                self.team_2_betters.append(voter)
        
        def check_user(self, user):
            return (user in self.team_1_betters) or (user in self.team_2_betters)

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return
        
        self.dragon = utils.global_dragon
        
        lookup_summoner = None
        lookup_summoner = self.dragon.watcher.summoner.by_name(client.config["region"], content)

        async with msg.channel.typing():
            if not lookup_summoner:
                utils.log(self, "Can not receive summoner from League API Endpoint", client)
                return
            
            game = None
            try:
                game = self.dragon.watcher.spectator.by_summoner(client.config["region"], lookup_summoner['id'])
            except HTTPError as e:
                utils.log(self, "Player is not in a game.", client)
                await msg.channel.send(
                    "That player is not in a game (or is in a bot game)."
                )
                return
            
            if not game:
                utils.log(self, "Can not receive game from League API Endpoint", client)
                return
            
            team_1, team_2 = [], []

            for player in game['participants']:
                if player['teamId'] == 100:
                    team_1.append(player)
                else:
                    team_2.append(player)

            desc = utils.team_names[0] + "\n" + "\n".join(
                    f"{player['summonerName']}: {self.dragon.champions[player['championId']]['name']} " +
                    f"[{self.dragon.summoners[player['spell1Id']]['name']}/{self.dragon.summoners[player['spell2Id']]['name']}] " +
                    f"({self.dragon.runes[player['perks']['perkStyle']][player['perks']['perkIds'][0]]})"
                    for player in team_1
                )

            desc += "\n" + utils.team_names[1] + "\n" + "\n".join(
                    f"{player['summonerName']}: {self.dragon.champions[player['championId']]['name']} " +
                    f"[{self.dragon.summoners[player['spell1Id']]['name']}/{self.dragon.summoners[player['spell2Id']]['name']}] " +
                    f"({self.dragon.runes[player['perks']['perkStyle']][player['perks']['perkIds'][0]]})"
                    for player in team_2
                )

            embed = discord.Embed(
                title="Betting Round",
                description=desc
            )

            embed.add_field(
                name=utils.team_names[0] + " Bets",
                value="Nobody!"
            )

            embed.add_field(
                name=utils.team_names[1] + " Bets",
                value="Nobody!"
            )

            embed.add_field(
                name="Match ID",
                value=game['gameId']
            )
            
            message = await msg.channel.send(
                content="",
                embed=embed
            )

            for reaction in ["\U0001F535", "\U0001F534", "\U0001F504"]:
                await message.add_reaction(reaction)
    
    def get_game_winner(self, client, game_id):

        game = None
        try:
            game = utils.global_dragon.watcher.match.by_id(client.config["region"], game_id)
        except HTTPError as e:
            utils.log(self, "The game is not over or does not exist!", client)
            return
        
        if not game:
            utils.log(self, "Can not receive game from League API Endpoint", client)
            return
        
        teams = game['teams']
        for team in teams:
            if team['win'] == "Win":
                return int(team['teamId'])
        return 0

    async def execute_reaction(self, client, reaction, channel, msg, user):
        if client.user.id == reaction.user_id:
            return
        
        if len(msg.embeds) == 0 or msg.embeds[0].title != "Betting Round":
            return
        
        state = Bets.State()

        await msg.remove_reaction(reaction.emoji, user)

        state.parse_msg(client, msg.embeds[0])

        if reaction.emoji.name == "\U0001F504": # check game end

            winner = self.get_game_winner(client, state.game_id)

            if winner == 100:
                await msg.edit(
                    content=client.messages['blue_won'],
                    embed=state.get_embed()
                )

            elif winner == 200:
                await msg.edit(
                    content=client.messages['red_won'],
                    embed=state.get_embed()
                )
            
            return

        if state.check_user(user):
            return

        if reaction.emoji.name not in ["\U0001F535", "\U0001F534"]:
            return

        if reaction.emoji.name == "\U0001F535":
            state.add_vote(1, user)
        elif reaction.emoji.name == "\U0001F534":
            state.add_vote(2, user)
        
        # update the message

        await msg.edit(
            content="", embed=state.get_embed()
        )