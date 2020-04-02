from dotenv import load_dotenv

load_dotenv()

from bot.ghost import GhostClient
import os

client = GhostClient()

client.run(os.getenv("DISCORD_TOKEN"))