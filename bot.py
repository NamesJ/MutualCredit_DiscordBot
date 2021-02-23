from mutual_credit.bot import *


import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


try: TOKEN
except NameError: TOKEN = os.getenv('DISCORD_TOKEN')

try: COMMAND_PREFIX
except NameError: COMMAND_PREFIX = '!'

try: intents
except NameError: intents = discord.Intents.default()
intents.members = True

try: bot
except NameError: commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)



if __name__ == '__main__':
    bot.run(TOKEN)
