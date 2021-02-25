from mutual_credit import credit_system as cs
from mutual_credit.errors import (
    MaxBalanceError,
    MinBalanceError,
    TransactionIDError,
    TransactionStatusError,
    UserPermissionError
)

import discord
from dotenv import load_dotenv
import os
import shlex



class MutualCreditClient (discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def handle_command(self, message):

        args = shlex.split(message.content)
        cmd = args[0][1:]
        try:
            func = getattr(self, 'handle_' + cmd)
            if not cs.isMember(message.author.id): # membership check
                raise UserPermissionError('You must be a member to do that')
        except AttributeError as e:
            await message.reply(f'I don\'t know the command {cmd}')
        else:
            await func(message)


    async def handle_add_cats(self, message):
        args = shlex.split(message.content)
        if len(args) < 3:
            await message.reply(f'I think you forgot something -- you didn\'t give me enough arguments.')
            return

        user = message.author
        offer_id, categories = args[1], args[2:]

        try:
            cs.addCategoriesToOffer(user.id, offer_id, categories)
        except UserPermissionError as e:
            await message.reply('You are not allowed to edit someone else\'s offer')
        else:
            categories = cs.getOfferCategories(offer_id)
            categories = ', '.join(categories)
            await message.reply(f'Offer now has the following categories: {categories}')


    async def handle_approve(self, message):
        args = shlex.split(message.content)
        if len(args) < 2:
            await message.reply(f'I think you forgot something -- you didn\'t give me enough arguments.')
            return

        user = message.author
        tx_ids = args[1:]

        total = len(tx_ids)
        response = ''
        for i in range(len(tx_ids)):
            tx_id = tx_ids[i]

            response += f'{i+1}/{total}:'

            try:
                cs.approveTransaction(user.id, tx_id)
                balance = cs.getBalance(user.id)
            except TransactionIDError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' A transaction with that ID doesn\'t exist.\n'
            except MaxBalanceError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' You\'re balance is too high.\n'
            except MinBalanceError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' Buyer\'s balance is too low.\n'
            except UserPermissionError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' You are not the seller for this transaction.\n'
            else:
                response += f' Approved transaction {tx_id}.\n'
                response += f'New balance: ${balance}\n'

        # remove last line break
        response = response[:-1]
        await message.reply(response)






    async def handle_balance(self, message): # member-only command
        balance = cs.getBalance(message.author.id)
        await message.reply(f'Your balance is ${balance}')


    async def handle_kill(self, message): # member-only command
        quit()


    async def handle_hello(self, message):
        await message.reply('Hi!', mention_author=True)


    async def on_ready(self):
        print('MutualCreditClient ready')


    async def on_message(self, message):
        if message.content.startswith('!'):
            try:
                await self.handle_command(message)
            except UserPermissionError as e:
                await message.reply('You don\'t have permission to do that')
            except Exception as e:
                print(str(e))




if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.members = True
    client = MutualCreditClient(command_prefix='!', intents=intents)
    try:
        client.run(TOKEN)
    except Exception as e:
        print(str(e))
