import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from mutual_credit.bot import *
from mutual_credit.bot import BOT_COMMANDS as MC_BOT_COMMANDS
from vouch.bot import *
from vouch.bot import BOT_COMMANDS as V_BOT_COMMANDS

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.members = True



@commands.command(name='kill', help='Kill bot process')
@commands.has_role('admin')
async def kill_bot(ctx):
    exit()


"""
@commands.command(name='clean_db', help='Reset database')
@commands.has_role('admin')
async def clean_db(ctx):
    cs.cleanDB()
"""


BOT_COMMANDS = [
    #clean_db,
    kill_bot
]
BOT_COMMANDS += MC_BOT_COMMANDS
BOT_COMMANDS += V_BOT_COMMANDS


if __name__ == '__main__':
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    for cmd in BOT_COMMANDS:
        bot.add_command(cmd)
    bot.run(TOKEN)
