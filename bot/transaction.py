from .mutual_credit import credit_system as cs
from .mutual_credit.errors import (
    AccountIDError,
    MaxBalanceError,
    MinBalanceError,
    SelfTransactionError,
    TransactionIDError,
    TransactionStatusError,
    UserPermissionError
)

from .utils import role_check, user_from_id

import shlex


async def subcmd_approve(client, message, args):
    ''' Approve one or more transactions for caller '''

    if len(args) < 1:
        raise Exception('You must provide at least one transaction ID.')

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    tx_ids = args

    total_txs = len(tx_ids)
    response = ''
    for i in range(total_txs):
        tx_id = tx_ids[i]

        if total_txs > 1:
            response += f'{i+1}/{total_txs}:'

        try:
            cs.approveTransaction(user.id, tx_id)
            balance = cs.getAccountBalance(user.id)
            buyer_id = cs.getTransactionBuyer(tx_id)
        except TransactionIDError as e:
            response += f' Skipping transaction {tx_id}. {str(e)}\n'
        except TransactionStatusError as e:
            response += f' Skipping transaction {tx_id}. {str(e)}\n'
        except MaxBalanceError as e:
            response += f' Skipping transaction {tx_id}. {str(e)}\n'
        except MinBalanceError as e:
            response += f' Skipping transaction {tx_id}. {str(e)}\n'
        except UserPermissionError as e:
            response += f' Skipping transaction {tx_id}. {str(e)}\n'
        else:
            response += f' Approved transaction {tx_id}.\n'
            response += f'New balance: ${balance}\n'

            buyer = user_from_id(client, buyer_id)
            if buyer:
                await buyer.create_dm()
                content = f'{user.name} approved your buy request with'
                content += f' ID {tx_id}'
                await buyer.dm_channel.send(content)

    # remove last line break
    response = response[:-1]
    await message.reply(response)


async def subcmd_cancel(client, message, args):
    ''' Cancel one or many transactions created by caller '''

    if len(args) < 1:
        raise Exception('You must provide at least one trannsaction ID.')

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    tx_ids = args

    total_txs = len(tx_ids)
    response = ''
    for i in range(total_txs):
        tx_id = tx_ids[i]

        if total_txs > 1:
            response += f'{i+1}/{total_txs}:'

        try:
            cs.cancelTransaction(user.id, tx_id)
            balance = cs.getAvailableBalance(user.id)
            seller_id = cs.getTransactionSeller(tx_id)
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

            seller = user_from_id(client, seller_id)
            if seller:
                await seller.create_dm()
                content = f'{seller.name} cancelled their transaction request with'
                content += f' ID {tx_id}'
                await seller.dm_channel.send(content)

    # remove last line break
    response = response[:-1]
    await message.reply(response)


async def subcmd_deny(client, message, args):
    ''' Deny one or more transactions for caller '''

    if len(args) < 1:
        raise Exception('You must provide at least one trannsaction ID.')

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    tx_ids = args

    total_txs = len(tx_ids)
    response = ''
    for i in range(total_txs):
        tx_id = tx_ids[i]

        if total_txs > 1:
            response += f'{i+1}/{total_txs}:'

        try:
            cs.denyTransaction(user.id, tx_id)
            available_balance = cs.getAvailableBalance(user.id)
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
            response += f' Denied transaction {tx_id}.\n'
            #response += f'New available balance: ${available_balance}\n'

    # remove last line break
    response = response[:-1]
    await message.reply(response)


async def subcmd_request(client, message, args):
    ''' Create one or more transactions for caller '''

    if len(args) < 1:
        raise Exception('You must provide one or more offer IDs.')

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    offer_ids = args

    total_offers = len(offer_ids)
    response = ''
    for i in range(total_offers):
        offer_id = offer_ids[i]

        if total_offers > 1:
            response += f'{i+1}/{total_offers}:'

        try:
            tx_id = cs.createTransaction(user.id, offer_id)
            available_balance = cs.getAvailableBalance(user.id)
            seller_id = cs.getOfferSeller(offer_id)
            offer_title = cs.getOfferTitle(offer_id)
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
            response += f' Created buy request with ID {tx_id}.\n'
            response += f'New available balance: ${available_balance}\n'
            # notify seller
            seller = user_from_id(client, seller_id)
            if seller:
                await seller.create_dm()
                content = f'New buy request with ID {tx_id}'
                content += f' from {user.name} for {offer_title}.'
                await seller.dm_channel.send(content)

            else:
                print('Seller not found, which is weird.')

    # remove last line break
    response = response[:-1]
    await message.reply(response)


async def handle(client, message, args):
    if len(args) < 1:  # TODO: Add an CommandArgumentsError
        raise Exception('Invalid number of arguments')

    subcmd = args[0]
    args = args[1:]

    try:
        if subcmd == 'approve':
            try:
                await subcmd_approve(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'cancel':
            try:
                await subcmd_cancel(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'deny':
            try:
                await subcmd_deny(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'request':
            try:
                await subcmd_request(client, message, args)

            except AccountIDError as e:
                raise e

        else:
            await message.reply('I don\'t know that sub-command!')

    except AccountIDError as e:
        print(e)
        await message.reply('You don\'t have an account.')
