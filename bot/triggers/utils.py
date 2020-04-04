import time
import asyncio
import discord
import re
import traceback

from utils.datadragon import DataDragon

emoji_numbers = [
    "\u0030\u20E3", #  0
    "\u0031\u20E3",
    "\u0032\u20E3",
    "\u0033\u20E3",
    "\u0034\u20E3",
    "\u0035\u20E3",
    "\u0036\u20E3",
    "\u0037\u20E3",
    "\u0038\u20E3",
    "\u0039\u20E3",
    "\U0001F51F",   # 10
]

symbols = {
    "blue_team": ":blue_circle:",
    "red_team": ":red_circle:"
}

team_names = [
    f"{symbols['blue_team']} Team 1",
    f"{symbols['red_team']} Team 2"
]

draft_order = [
    1, 2, 2, 1, 2, 1, 1, 2
]

no_matching_results_emote = "🚫"

global_dragon = None

async def generate_react_menu(
    sendable, user_id, opening_message, max_length, option_list, cancel_message
):
    max_length = min(max_length, len(emoji_numbers))

    msg_to_send = f"<@{user_id}>"
    msg_to_send += opening_message
    for i in range(min(max_length, len(option_list))):
        msg_to_send += f"\n\n{emoji_numbers[i]} {option_list[i]}"
    msg_to_send += f"\n\n{no_matching_results_emote} {cancel_message}"
    sent_msg = await sendable.send(msg_to_send)
    for i in range(min(max_length, len(option_list))):
        await sent_msg.add_reaction(emoji_numbers[i])
    await sent_msg.add_reaction(no_matching_results_emote)

def setup_data_dragon(client):
    global global_dragon
    global_dragon = DataDragon(client)

def user_is_mod(client, user) -> bool:
    return any(id in [role.id for role in user.roles] for id in client.config["mod_role_ids"])


def has_flag(flag, content):
    """Determines if a command's content contains a flag.

    Arguments:
    flag -- the flag for which to search
    content -- the content of the command
    """
    return "-" + flag in content.split()


def get_flag(flag, content, default=None):
    """Finds the value associated with a flag in a command's content.

    Arguments:
    flag -- the flag for which to return a value
    content -- the content of the command

    Keyword arguments:
    default -- the value to return in case the flag is not present in the content, or the flag has no associated value (last argument)
    """
    if not has_flag(flag, content):
        return default

    args = content.split()
    i = args.index("-" + flag)

    # get argument following flag
    if i + 1 == len(args):
        return default
    return args[i + 1]


def find_first_mention(text):
    return re.search("<@!?(\d+)>", text).group(0)

def user_from_mention(client, mention):
    match = re.match("<@!?(\d+)>", mention)
    if match is None:
        return None
    else:
        return client.get_user(int(match.group(1)))


def sanitized(msg):
    return msg.replace("`", "'")


def get_correct_attr(obj, attr, client):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    else:
        return None

def print_error(trigger, text):
    if type(trigger) == str:
        print(f"[!] {text}")
    else:
        print(f"[{type(trigger).__name__.upper()}] {text}")

# prints a traceback and sends it to discord
# to get a traceback sent to steam put this line in any except: call
# await utils.sendTraceback(client, "")
async def sendTraceback(client, content=""):
    # print the traceback to the terminal
    print(content)
    print(traceback.format_exc())

    # if there is a traceback server and channel, send the traceback in discord as well
    """
    try:
        msg_to_send = f"```bash\n{traceback.format_exc()}\n```"
        if content:
            msg_to_send = f"`{content}`\n" + msg_to_send
        await client.TRACEBACK_CHANNEL.send(msg_to_send)
    except:
        print(
            "\nNote: traceback was not sent to Discord, if you want this double check your config.json"
        )
    """