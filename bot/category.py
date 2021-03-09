from .mutual_credit import credit_system as cs
from .mutual_credit.errors import OfferIDError, UserPermissionError

from .utils import role_check

import shlex


async def subcmd_add(client, message, args):
    ''' Create one or more categories for offer of caller '''

    if len(args) < 2:
        raise Exception('Must provide at least one offer ID and one category')

    offer_id = args[0]
    categories = args[1:]

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    try:
        cs.addCategoriesToOffer(user.id, offer_id, categories)
    except OfferIDError as e:
        await message.reply(f'An offer with ID {offer_id} does not exist')
    except UserPermissionError as e:
        await message.reply('You are not allowed to edit someone else\'s offer')
    else:
        categories = cs.getOfferCategories(offer_id)
        categories = ', '.join(categories)
        await message.reply(f'Offer now has the following categories: {categories}')


async def subcmd_remove(client, message, args):
    print(args)
    ''' Remove one or more categories from offer of caller '''

    if len(args) < 2:
        raise Exception('Must provide at least one offer ID and one category')

    offer_id = args[0]
    categories = args[1:]

    print(categories)

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    try:
        cs.removeCategoriesFromOffer(user.id, offer_id, categories)
    except UserPermissionError as e:
        await message.reply('You are not allowed to edit someone else\'s offer')
    else:
        categories = cs.getOfferCategories(offer_id)
        categories = ', '.join(categories)
        await message.reply(f'Offer now has the following categories: {categories}')


async def subcmd_show(client, message, args):
    ''' List all categories for offer of caller '''

    if len(args) != 1:
        raise Exception('Must provide an offer ID')

    offer_id = args[0]

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    try:
        categories = cs.getOfferCategories(offer_id)
        categories = ', '.join(categories)
    except OfferIDError as e:
        await message.reply(f'An offer with ID {offer_id} doesn\'t exist.')
    else:
        await message.reply(f'Offer {offer_id} categories: {categories}')


async def handle(client, message, args):
    if len(args) < 1:
        raise Exception('Must provide a sub-command')

    subcmd = args[0]
    args = args[1:]

    try:
        if subcmd == 'add':
            try:
                await subcmd_add(client, message, args)

            except AccountIDError as e:
                await message.reply('You don\'t have an account.')

        elif subcmd == 'remove':
            try:
                await subcmd_remove(client, message, args)

            except AccountIDError as e:
                await message.reply('You don\'t have an account.')

        elif subcmd == 'show':
            try:
                await subcmd_show(client, message, args)

            except AccountIDError as e:
                await message.reply('You don\'t have an account.')

        else:
            await message.reply('I don\'t know that sub-command!')

    except AccountIDError as e:
        print(e)
        await message.reply('You don\'t have an account.')
