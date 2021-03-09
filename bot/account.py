from .mutual_credit import credit_system as cs
from .mutual_credit.errors import AccountIDError

from .utils import role_check

import shlex


async def subcmd_allowance(client, message, args):
    ''' Show range for account of caller '''

    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    try:
        min_balance, max_balance = cs.getAccountRange(user.id)
    except AccountIDError as e:
        await message.reply('You don\'t seem to have an account.')
    else:
        await message.reply(f'${min_balance} to ${max_balance}')


async def subcmd_balance(client, message, args): # member-only command
    ''' Get account balance for caller '''

    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    # membership check for members-only functions
    if not role_check(client, user.id, 'member'):
        message.reply('You are not a member.')

    account_balance = cs.getAccountBalance(user.id)
    available_balance = cs.getAvailableBalance(user.id)
    pending_credits = cs.getTotalPendingCredits(user.id)

    response = ''
    response += f'\nAccount balance: ${account_balance}'
    response += f'\nAvailable balance: ${available_balance}'
    response += f'\nPending credits: ${pending_credits}'
    await message.reply(response)


async def subcmd_create(client, message, args):
    ''' Create account if one does not exist for caller '''

    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    if role_check(client, user.id, 'member'):
        raise Exception('You are not a member.')

    try:
        cs.createAccount(user.id)
    except AccountIDError as e:
        await message.reply('You already have an account.')
    else:
        await message.reply('Account created!')


async def handle(client, message, args):
    if len(args) < 1: # TODO: Add an CommandArgumentsError
        raise Exception('Must provide a sub-command')

    subcmd = args[0]
    args = args[1:]

    try:
        if subcmd == 'allowance':
            try:
                await subcmd_allowance(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'balance':
            try:
                await subcmd_balance(client, message, args)

            except AccountIDError as e:
                raise e

        elif subcmd == 'create':
            try:
                await subcmd_create(client, message, args)

            except AccountIDError as e:
                raise e

        else: # TODO: Add SubCommandError
            await message.reply('I don\'t know that sub-command!')

    except AccountIDError as e:
        print(e)
        await message.reply('You need an account to do that.')
