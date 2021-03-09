from . import account, category, help, kill, offer, transaction

from .mutual_credit.errors import UserPermissionError

from .utils import find_subcommands, mention_to_id

import discord
from discord.utils import get
import os
import shlex
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True



class MutualCreditClient (discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    async def on_command(self, message):
        args = shlex.split(message.content)

        cmd = args[0][1:]
        args = args[1:]

        user = message.author

        try:
            # non-member commands
            #func = getattr(self, 'handle_' + cmd)
            if cmd == 'account':
                await account.handle(client, message, args)
            elif cmd == 'category':
                await category.handle(client, message, args)
            elif cmd == 'offer':
                await offer.handle(client, message, args)
            elif cmd == 'help':
                await help.handle(client, message, args)
            elif cmd == 'kill':
                await kill.handle(client, message, args)
            elif cmd == 'transaction':
                await transaction.handle(client, message, args)
            else:
                await message.reply('I don\'t know that command')

        except Exception as e:
            await message.reply(str(e))
            raise e


    async def on_message(self, message):
        user = message.author

        if message.author == self.user:
            return

        if not message.content.startswith('!'):
            return

        try:
            await self.on_command(message)
        except UserPermissionError as e:
            await message.reply('You don\'t have permission to do that')
        except Exception as e:
            print(e)
            raise e


    async def on_ready(self):
        print('MutualCreditClient ready')



client = MutualCreditClient(command_prefix='!', intents=intents)