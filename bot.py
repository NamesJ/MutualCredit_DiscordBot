from mutual_credit import credit_system as cs
from mutual_credit.errors import (
    MaxBalanceError,
    MinBalanceError,
    SelfTransactionError,
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
        self.commands = []

        for name in vars(self):
            if name.startswith('handle_'):
                self.commands.append(name[7:])


    async def run_command(self, message):

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

        total_txs = len(tx_ids)
        response = ''
        for i in range(total_txs):
            tx_id = tx_ids[i]

            if total_txs > 1:
                response += f'{i+1}/{total_txs}:'

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


    async def handle_available_balance(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_balance(self, message): # member-only command
        balance = cs.getBalance(message.author.id)
        await message.reply(f'Your balance is ${balance}')


    async def handle_buy(self, message):
        args = shlex.split(message.content)
        if len(args) < 2:
            await message.reply(f'I think you forgot something -- you didn\'t give me enough arguments.')
            return

        user = message.author
        offer_ids = args[1:]

        total_offers = len(offer_ids)
        response = ''
        for i in range(total_offers):
            offer_id = offer_ids[i]

            if total_offers > 1:
                response += f'{i+1}/{total_offers}:'

            try:
                cs.createTransaction(user.id, offer_id)
                available_balance = cs.getAvailableBalance(user.id)
            except TransactionIDError as e:
                response += f' Skipping offer {offer_id}.'
                response += ' An offer with that ID doesn\'t exist.\n'
            except MinBalanceError as e:
                response += f' Skipping offer {offer_id}.'
                response += ' You\'re balance is too low.\n'
            except SelfTransactionError as e:
                response += f' Skipping offer {offer_id}.'
                response += ' You can\'t buy your own offer.'
            else:
                response += f' Sent buy request for {offer_id}.\n'
                response += f'New available balance: ${available_balance}\n'

        # remove last line break
        response = response[:-1]
        await message.reply(response)


    async def handle_cancel(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_create_account(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_create_offer(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_delete_offer(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_deny(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_help(self, message):
        response = 'Commands:'

        for cmd in self.commands:
            response += f'\n{cmd}'

        await message.reply(response)


    async def handle_kill(self, message): # member-only command
        quit()


    async def handle_list_categories(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_list_offers(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_remove_categories(self, message):
        await message.reply('This command is not yet implemented.')


    async def handle_show_range(self, message):
        await message.reply('This command is not yet implemented.')


    async def on_ready(self):
        print('MutualCreditClient ready')


    async def on_message(self, message):
        if message.content.startswith('!'):
            try:
                await self.run_command(message)
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
