import discord
import random
from draft import Draft
from utils import *
import tokens

client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_reaction_add(reaction, user):

    if client.user == user:
        return

    message = reaction.message

    if len(message.embeds) == 1 and message.embeds[0].title == "League Draft":
        draft = Draft()

        await message.remove_reaction(reaction.emoji, user)

        draft.parse_message(client, message)

        # filter out people who shouldn't go or invalid emojis

        possible_emojis = [reaction["emoji"] for reaction in number_emoji[1:len(draft.unpicked) + 1]]

        if reaction.emoji not in possible_emojis:
            return
        if user not in draft.captains:
            print("[WARNING] Somebody who isn't a captain tried to go")
            return
        
        if user != draft.captains[(draft.turn - 1) % 2]:
            print("[WARNING] A captain tried to go out of turn!")
            return

        # update it to swap the player to the correct team

        draft.make_pick(possible_emojis.index(reaction.emoji))

        # update the message

        channel = message.channel
        await message.delete()

        new_msg = await channel.send(
            content=draft.get_content(), embed=draft.get_embed()
        )
        
        for reaction in number_emoji[1:len(draft.unpicked) + 1]:
            await new_msg.add_reaction(reaction["emoji"])


@client.event
async def on_message(message):
    global flag

    if message.author.bot or message.author == client.user:
        return

    if message.content.lower() == "no u":
        await message.channel.send("no u")
        return
    
    if not message.content.startswith(flag):
        return

    bot_commands = client.get_channel(688971836511617044)

    # only allow commands in bot_commands

    if (message.channel is not bot_commands) and (message.channel.type is not discord.ChannelType.private):
        await message.author.send(f"You can only use commands in {bot_commands.mention} or in a DM!")
        return
    
    # get rid of the flag
    message.content = message.content[1:]

    #######################################
    #         CAN BE SENT ANYWHERE        #
    #######################################
    
    if message.content == "help":
        await message.channel.send("Available Commands:\n    !randomize\n    !reset")

    if message.content == "coinflip":
        await message.channel.send(
            "heads" if random.randint(0, 1) == 0 else "tails"
        )
    
    if message.content.startswith("ugg"):
        args = get_args_from_text(message.content)
        if len(args) != 2:
            await message.channel.send(
                "Usage: !ugg <champ name>"
            )
            return
        await message.channel.send(
            f"<https://u.gg/lol/champions/{args[1]}/build>"
        )

    if message.content.startswith("opgg"):
        args = get_args_from_text(message.content)
        if len(args) < 2:
            await message.channel.send(
                "Usage: !opgg <name1> [<name2> <name3> ...]"
            )
            return
        
        content = ""

        if len(args) > 2:
            content += "<https://na.op.gg/multi/query=" + "%2C".join(
                [
                    name for name in args[1:]
                ]
            ) + ">\n"
        content += "\n".join(
            [
                f"<https://na.op.gg/summoner/userName={name}>"
                for name in args[1:]
            ]
        )
        await message.channel.send(
            content
        )

    if message.channel.type is discord.ChannelType.private:
        await message.channel.send("Either this command is server-only or does not exist.")
        return

    if message.content.startswith("clash"):
        args = get_args_from_text(message.content)

    #######################################
    #           ONLY IN A SERVER          #
    #######################################

    if message.content.startswith("purge"):
        # permission check
        if not is_mod(message.author):
            await send_permission_denied(message.channel)
            return

        args = get_args_from_text(message.content)

        num = 100

        if len(args) > 1:
            num = int(args[1])
        
        await bot_commands.purge(limit=num)
        return

    if message.content.startswith("draft"):
        # permission check
        if not is_mod(message.author):
            await send_permission_denied(message.channel)
            return

        draft = Draft()
        result = draft.parse_args(client, message)

        if result == -1:
            await message.channel.send(
                error_msgs["draft"]["usage"]
            )
            return
        elif result == -2:
            await message.channel.send(
                error_msgs["draft"]["no_captain1"]
            )
            return
        elif result == -3:
            await message.channel.send(
                error_msgs["draft"]["no_captain2"]
            )
            return
        elif result == -4:
            await message.channel.send(
                error_msgs["draft"]["bot_captain"]
            )
        elif result == -5:
            await message.channel.send(
                error_msgs["draft"]["same_captain"]
            )
        elif result == -6:
            await message.author.send(
                error_msgs["draft"]["caller_not_connected"]
            )
        elif result == -7:
            await message.channel.send(
                error_msgs["draft"]["incorrect_num_players"]
            )
        elif result == -8:
            await message.channel.send(
                error_msgs["draft"]["captain_not_connected"]
            )
        else:
            # success, result is a tuple (string, discord.Embed)
            sent_msg = await message.channel.send(
                content=draft.get_content(), embed=draft.get_embed()
            )
            
            for reaction in number_emoji[1:len(draft.unpicked) + 1]:
                await sent_msg.add_reaction(reaction["emoji"])

    if message.content == "reset":
        # permission check
        if not is_mod(message.author):
            await send_permission_denied(message.channel)
            return
        
        vibing_1_vc = client.get_channel(688951863869046792)
        team_1_vc   = client.get_channel(688953927504363555)
        team_2_vc   = client.get_channel(688953951865143303)

        all_members = team_1_vc.members + team_2_vc.members

        print("Moving these users:", [member.name for member in all_members])

        for member in all_members:
            try:
                await member.move_to(vibing_1_vc)
            except:
                print(f"[ERROR] Could not move {member.name} to Vibing 1")

    if message.content.startswith("randomize"):
        # permission check
        if not is_mod(message.author):
            await send_permission_denied(message.channel)
            return

        if message.author.voice is None:
            await message.author.send("You need to be connected to a voice channel to use that command!")
            return

        connected_members = message.author.voice.channel.members

        if len(connected_members) != 10:
            print("[ERROR] Cannot randomize without exactly 10")
            await message.channel.send("You need exactly 10 users in your voice channel to use this command.")
            return

        temp = random.sample(connected_members, k=len(connected_members))

        roles_list = ["Top", "Jgl", "Mid", "Bot", "Sup"]

        team_1, team_2 = temp[:5], temp[5:]

        await message.channel.send(
            "**Team 1**:\n" +
            "".join(role + ": " + member.name + "\n" for role, member in zip(roles_list, team_1)) +
            "\n**Team 2**:\n" +
            "".join(role + ": " + member.name + "\n" for role, member in zip(roles_list, team_2))
        )

        team_1_vc = client.get_channel(688953927504363555)
        team_2_vc = client.get_channel(688953951865143303)

        for member in team_1:
            try:
                await member.move_to(team_1_vc)
            except:
                print(f"[ERROR] Could not move {member.name} to Team 1")
        
        for member in team_2:
            try:
                await member.move_to(team_2_vc)
            except:
                print(f"[ERROR] Could not move {member.name} to Team 2")

client.run(tokens.discord_token)
