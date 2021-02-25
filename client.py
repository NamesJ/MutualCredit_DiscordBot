from mutual_credit import credit_system as cs
from mutual_credit.errors import (
    AccountIDError,
    MaxBalanceError,
    MinBalanceError,
    OfferIDError,
    SelfTransactionError,
    TransactionIDError,
    TransactionStatusError,
    UserPermissionError
)

import discord
from dotenv import load_dotenv
import os
import shlex



def mentionToId(mention):
    userId = mention
    if userId.startswith('<@') and userId.endswith('>'):
        userId = userId[2:-1]
    if userId.startswith('!'):
        userId = userId[1:]
    return int(userId)



class MutualCreditClient (discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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


    async def handle_balance(self, message): # member-only command
        user = message.author
        balance = cs.getBalance(user.id)
        available = cs.getAvailableBalance(user.id)
        await message.reply(f'\nBalance: ${balance}\nAvailable: ${available}')


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
                cs.cancelTransaction(user.id, tx_id)
                balance = cs.getAvailableBalance(user.id)
            except TransactionIDError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' A transaction with that ID doesn\'t exist.\n'
            except UserPermissionError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' You are not the buyer for this transaction.\n'
            except TransactionStatusError as e:
                response += f' Skipping transaction {tx_id}.'
                response += ' Transaction is not pending.'
            else:
                response += f' Cancelled transaction {tx_id}.\n'
                response += f'New available balance: ${balance}\n'

        # remove last line break
        response = response[:-1]
        await message.reply(response)


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

        for name in dir(self):
            if name.startswith('handle_'):
                response += '\n!' + name[7:]

        await message.reply(response)


    async def handle_kill(self, message): # member-only command
        quit()


    async def handle_list_categories(self, message):
        args = shlex.split(message.content)
        if len(args) != 2:
            await message.reply(f'I think you forgot something -- that\'s not the right number of arguments.')
            return

        user = message.author
        offer_id = args[1]

        try:
            categories = cs.getOfferCategories(offer_id)
            categories = ', '.join(categories)
        except OfferIDError as e:
            await message.reply(f'An offer with ID {offer_id} doesn\'t exist.')
        else:
            await message.reply(f'Offer {offer_id} categories: {categories}')


    async def handle_list_offers(self, message):
        args = shlex.split(message.content)
        if len(args) != 2:
            await message.reply(f'That\'s not the right number of arguments.')

        user = message.author
        mention = args[1]
        seller_id = mentionToId(mention)

        try:
            offers = cs.getOffers(seller_id)
        except AccountIDError as e:
            await message.reply(f'There is no seller with that ID.')
        else:
            response = '\n'

            for offer in offers:
                offer_id, seller_id, description, price, title = offer
                response += f'{title} | ${price}\n{description}\n{offer_id}\n\n'

            response = response[:-2]

            await message.reply(response)


    async def handle_remove_categories(self, message):
        args = shlex.split(message.content)
        if len(args) < 3:
            await message.reply(f'I think you forgot something -- you didn\'t give me enough arguments.')
            return

        user = message.author
        offer_id, categories = args[1], args[2:]

        try:
            cs.removeCategoriesFromOffer(user.id, offer_id, categories)
        except UserPermissionError as e:
            await message.reply('You are not allowed to edit someone else\'s offer')
        else:
            categories = cs.getOfferCategories(offer_id)
            categories = ', '.join(categories)
            await message.reply(f'Offer now has the following categories: {categories}')


    async def handle_show_range(self, message):
        args = shlex.split(message.content)
        if len(args) > 1:
            await message.reply(f'This command takes no arguments.')

        user = message.author

        try:
            min_balance, max_balance = cs.getAccountRange(user.id)
        except AccountIDError as e:
            await message.reply('You don\'t seem to have an account.')
        else:
            await message.reply(f'${min_balance} to ${max_balance}')


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
