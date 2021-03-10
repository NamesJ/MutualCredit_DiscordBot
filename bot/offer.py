from .mutual_credit import credit_system as cs
from .mutual_credit.errors import (
    AccountIDError,
    OfferIDError,
    MaxBalanceError,
    MinBalanceError,
    TransactionIDError,
    UserPermissionError
)

from .utils import user_from_id, mention_to_id, role_check

import shlex
import logging

log = logging.getLogger(__name__)



async def subcmd_add(client, message, args):
    ''' Create a new offer for calling account '''

    if len(args) < 3:
        raise Exception('Invalid number of arguments.')

    user = message.author
    title, price, description = args[:3]

    offer_id = cs.createOffer(user.id, description, price, title)

    if len(args) > 3: # user supplies optional tags
        cs.addCategoriesToOffer(user.id, offer_id, args[3:])

    await message.reply(f'Created offer with ID {offer_id}.')


async def subcmd_remove(client, message, args):
    ''' Delete one or more offers for caller '''

    if len(args) < 1:
        raise Exception(f'You must provide at least one offer ID.')

    user = message.author
    offer_ids = args

    response = ''
    for i in range(len(offer_ids)):
        offer_id = offer_ids[i]

        if len(offer_ids) > 1:
            response += f'{i+1}/{len(offer_ids)}:'

        try:
            cs.deleteOffer(user.id, offer_id)
        except TransactionIDError as e:
            response += f' Skipping offer {offer_id}.'
            response += ' A transaction with that ID doesn\'t exist.\n'
        except MaxBalanceError as e:
            response += f' Skipping offer {offer_id}.'
            response += ' You\'re balance is too high.\n'
        except MinBalanceError as e:
            response += f' Skipping offer {offer_id}.'
            response += ' Buyer\'s balance is too low.\n'
        except UserPermissionError as e:
            response += f' Skipping offer {offer_id}.'
            response += ' You are not the seller for this transaction.\n'
        else:
            response += f' Deleted offer {offer_id}.\n'

    # remove last line break
    response = response[:-1]
    await message.reply(response)


async def subcmd_show(client, message, args):
    ''' List all offers for account '''

    user = message.author
    seller_name = None
    seller_id = None

    if len(args) == 0:
        seller_id = user.id
        seller_name = user.name
    elif len(args) == 1:
        seller_id = mention_to_id(args[0])
        if not seller_id:
            raise Exception('Invalid user mention provided')
        seller = await user_from_id(client, seller_id)
        seller_name = seller.name
    else:
        raise Exception('Invalid number of arguments')

    try:
        offers = cs.getOffers(seller_id)
    except AccountIDError as e:
        await message.reply(f'No seller with ID {seller_id} exists.')
    else:
        if not offers:
            await message.reply(f'Account has no offers.')
            return

        response = f'{seller_name}\'s Offers:\n\n'

        offer_strfmt = '{title} | ${price}\n{desc}\nCategories: {cats}\nID: {off_id}\n\n'

        for offer in offers:
            categories = cs.getOfferCategories(offer[0])
            if len(categories):
                categories = ', '.join(categories)
            else:
                categories = '---'


            response += offer_strfmt.format(
                off_id = offer[0],
                sell_id = offer[1],
                desc = offer[2],
                price = offer[3],
                title = offer[4],
                cats = categories
            )

        #strip last line breaks
        response = response[:-2]
        await message.reply(response)


async def handle(client, message, args):
    if len(args) < 1:  # TODO: Add an CommandArgumentsError
        raise Exception('Invalid number of arguments')

    subcmd = args[0]
    args = args[1:]

    user = message.author
    is_admin = await role_check(client, user.id, 'admin')
    is_member = await role_check(client, user.id, 'member')

    try:
        # non-member sub-commands up here

        # member-only sub-commands down here

        if not is_member:
            raise Exception('You are not a member.')

        if subcmd == 'add':
            try:
                await subcmd_add(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'remove':
            try:
                await subcmd_remove(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'show':
            try:
                await subcmd_show(client, message, args)

            except AccountIDError as e:
                raise e

        else:
            await message.reply('I don\'t know that sub-command!')

    except AccountIDError as e:
        print(e)
        await message.reply('You need an account to do that')
