from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
import random
import re

class Draft(Command, ReactionTrigger):
    names = ["draft"]
    description = "Start a 5v5 draft with two selected captains. Able to randomize which captain picks first and turn on a snake draft."
    usage = "!draft <@captain1> <@captain2> [random] [snake]"
    requires_mod = True
    requires_server = True

    class DraftState:
        def __init__(self, players=None, captains=None, snake=False):
            self.unpicked = players
            self.captains = captains
            self.snake = snake

            self.team_1 = []
            self.team_2 = []
            self.turn = 0

        def parse_msg(self, client, message):

            content = message.content

            self.turn = int(re.match("Pick (\d+)", content).group(1))

            embed = message.embeds[0]

            self.captains = [None] * 2

            self.unpicked = [
                utils.user_from_mention(client, utils.find_first_mention(line))
                for line in embed.description.split("\n")[1:]
            ]

            for field in embed.fields:
                if field.name == utils.team_names[0]:
                    self.captains[0] = utils.user_from_mention(client, utils.find_first_mention(field.value))
                    self.team_1 = [utils.user_from_mention(client, utils.find_first_mention(line)) for line in field.value.split("\n")[1:]]
                if field.name == utils.team_names[1]:
                    self.captains[1] = utils.user_from_mention(client, utils.find_first_mention(field.value))
                    self.team_2 = [utils.user_from_mention(client, utils.find_first_mention(line)) for line in field.value.split("\n")[1:]]

        def make_pick(self, index):
            player = self.unpicked.pop(index)
            if self.snake:
                if utils.draft_order[self.turn] == 1:
                    self.team_1.append(player)
                else:
                    self.team_2.append(player)
            else:
                if (self.turn - 1) % 2 == 0:
                    self.team_1.append(player)
                else:
                    self.team_2.append(player)

        def get_content(self):
            self.turn += 1
            # write a message and wait for reaccs
            if len(self.unpicked) > 0:
                if self.snake:
                    return f"Pick {self.turn}:\n{utils.draft_order[self.turn - 1].mention}, it's your turn to pick!"
                else:
                    return f"Pick {self.turn}:\n{self.captains[(self.turn - 1) % 2].mention}, it's your turn to pick!"
            return "Finalized teams:"

        def get_embed(self):
            captain_1, captain_2 = self.captains

            desc = ""

            if len(self.unpicked) > 0:
                desc = f"Unpicked Players:\n" + "\n".join(
                    [
                        utils.emoji_numbers[i] + f" {player.mention}"
                        for i, player in enumerate(self.unpicked, 1)
                    ]
                )

            embed = discord.Embed(
                title="League Draft",
                description=desc
            )

            embed.add_field(
                name=utils.team_names[0],
                value=f"\n{captain_1.mention}\n" + "\n".join(
                    player.mention for player in self.team_1
                )
            )
            embed.add_field(
                name=utils.team_names[1],
                value=f"\n{captain_2.mention}\n" + "\n".join(
                    player.mention for player in self.team_2
                )
            )

            return embed

    async def execute_command(self, client, msg, content):
        if not content:
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return
        
        args = msg.content.split(" ")

        if len(args) < 3:
            utils.log(self, "Tried to draft without at least 3 arguments")
            await msg.channel.send(
                f"Usage: {self.usage}"
            )
            return
        
        captain_1 = utils.user_from_mention(client, args[1])
        if captain_1 is None:
            await msg.channel.send(
                client.messages["draft_no_captain1"]
            )
            return
        
        captain_2 = utils.user_from_mention(client, args[2])
        if captain_2 is None:
            await msg.channel.send(
                client.messages["draft_no_captain2"]
            )
            return
        
        if captain_1.bot or captain_2.bot:
            await msg.channel.send(
                client.messages["draft_bot_captain"]
            )
            return

        if captain_1 == captain_2:
            await msg.channel.send(
                client.messages["draft_same_captain"]
            )
            return
        
        captains = [captain_1, captain_2]
        snake = False

        if "random" in content:
            random.shuffle(captains)

        if "snake" in content:
            snake = True

        voice_channel = msg.author.voice.channel
        players = set(voice_channel.members)
        
        if msg.author.voice is None:
            await msg.channel.send(
                client.messages["caller_not_connected"]
            )
            return

        if len(players) != 10:
            await msg.channel.send(
                client.messages["need_ten_players"]
            )
            return

        for captain in captains:
            if captain not in players:
                utils.log(self, f"{captain.name} is not in the voice channel!")
                await msg.channel.send(
                    client.messages["draft_captain_not_connected"]
                )
                return
        
        team_1_vc = client.get_channel(client.config["TEAM_1_ID"])
        team_2_vc = client.get_channel(client.config["TEAM_2_ID"])

        if len(team_1_vc.members) + len(team_2_vc.members) > 0:
            await msg.channel.send(
                client.messages["team_calls_not_empty"]
            )

        # remove captains from unpicked player pool
        for captain in captains:
            players.remove(captain)

        state = Draft.DraftState(
            players,
            captains,
            snake
        )
        
        message = await msg.channel.send(
            content=state.get_content(), embed=state.get_embed()
        )

        for reaction in utils.emoji_numbers[1:len(state.unpicked) + 1]:
                await message.add_reaction(reaction)
    
    async def execute_reaction(self, client, reaction, channel, msg, user):
        if client.user.id == reaction.user_id:
            return

        if len(msg.embeds) == 0 or msg.embeds[0].title != "League Draft":
            return
        
        state = Draft.DraftState()

        await msg.remove_reaction(reaction.emoji, user)

        state.parse_msg(client, msg)

        # filter out people who shouldn't go or invalid emojis

        possible_emojis = utils.emoji_numbers[1:len(state.unpicked) + 1]

        if reaction.emoji.name not in possible_emojis:
            return

        if user not in state.captains:
            utils.log(self, "Somebody who isn't a captain tried to go")
            return
        
        if user != state.captains[(state.turn - 1) % 2]:
            utils.log(self, "A captain tried to go out of turn!")
            return

        # update it to swap the player to the correct team

        state.make_pick(possible_emojis.index(reaction.emoji.name))

        # update the message

        await msg.delete()

        new_msg = await channel.send(
            content=state.get_content(), embed=state.get_embed()
        )
        
        for reaction in utils.emoji_numbers[1:len(state.unpicked) + 1]:
            await new_msg.add_reaction(reaction)
