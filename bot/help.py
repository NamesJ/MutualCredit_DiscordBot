from .utils import role_check

import os
import shlex
import logging

log = logging.getLogger(__name__)

# this way instead of `os.getenv(...)` to make sure that it's set
COMMAND_PREFIX = os.environ['COMMAND_PREFIX']


async def subcmd_long(client, message, args, is_admin=False):
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    response = f'''
{COMMAND_PREFIX}help output

**Create an account (member-only)**
*You must run this command first to use any of the commands below*
`{COMMAND_PREFIX}account create`

**Check your allowance (max debit/credit) (member-only)**
`{COMMAND_PREFIX}account allowance`

**Check your balance (member-only)**
*Returns account balance, available balance (balance - pending transfer requests sent from you) and pending sales (pending transfer requests sent to you) for your offers)*
`{COMMAND_PREFIX}account balance`

**Add one or more categories to an offer (member-only)**
`{COMMAND_PREFIX}tag add OFFER_ID TAG [TAG ...]`

**Remote one or more categories from an offer (member-only)**
`{COMMAND_PREFIX}tag remove OFFER_ID TAG [TAG ...]`
'''

    if is_admin:
        response += f'''
**Show the help message (add `full` for more output)**
`{COMMAND_PREFIX}help [full]`

**Kill the bot (admin-only)**
`{COMMAND_PREFIX}kill`
'''

    response += f'''
**Create a new offer (optionally with one or more categories)**
`{COMMAND_PREFIX}offer add TITLE PRICE DESCRIPTION [TAG TAG ...]`

**Remove one or more of your offers (member-only)**
`{COMMAND_PREFIX}offer remove OFFER_ID [OFFER_ID OFFER_ID]`

**Show offers from an account (member-only)**
*`@USER` indicates that your should use a `mention` ('@' someone)*
`{COMMAND_PREFIX}offer show @USER`

**Approve a transfer request from someone (member-only)**
*The buyer(s) will be notified that you have denied their request(s)*
*If successful, the offer price(s) will be added to your balance*
`{COMMAND_PREFIX}transaction approve TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Cancel one or more of your pending transfer requests (member-only)**
*The seller(s) will be notified that your request(s) have been cancelled*
`{COMMAND_PREFIX}transaction cancel TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Deny a transfer request from someone (member-only)**
*The buyer(s) will be notified that you have denied their request(s)*
`{COMMAND_PREFIX}transaction deny TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Create a transfer request for one or more offers (member-only)**
*The seller(s) will be notified of your request(s)*
`{COMMAND_PREFIX}transaction request OFFER_ID [OFFER_ID OFFER_ID ...]`'''

    await message.reply(response)


async def subcmd_short(client, message, args, is_admin=False):
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    response = f'''
{COMMAND_PREFIX}help output

`{COMMAND_PREFIX}account allowance`
`{COMMAND_PREFIX}account balance`
`{COMMAND_PREFIX}account create`
`{COMMAND_PREFIX}tag add OFFER_ID TAG [TAG ...]`
`{COMMAND_PREFIX}tag remove OFFER_ID TAG [TAG ...]`'''

    if is_admin:
        response += f'''
`{COMMAND_PREFIX}help [full]`
`{COMMAND_PREFIX}kill`'''

    response += f'''
`{COMMAND_PREFIX}offer add TITLE PRICE DESCRIPTION [TAG TAG ...]`
`{COMMAND_PREFIX}offer remove OFFER_ID [OFFER_ID OFFER_ID]`
`{COMMAND_PREFIX}offer show @USER`
`{COMMAND_PREFIX}transaction cancel TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`
`{COMMAND_PREFIX}transaction deny TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`
`{COMMAND_PREFIX}transaction request OFFER_ID [OFFER_ID OFFER_ID ...]`'''

    await message.reply(response)


async def handle(client, message, args):
    log.info(f'handle: arguments=({message, args})')
    subcmd = None

    if len(args) > 0:
        subcmd = args[0]
        args = args[1:]

    user = message.author
    is_admin = await role_check(client, user.id, 'admin')
    is_member = await role_check(client, user.id, 'member')

    if not is_member:
        raise Exception('You are not a member.')


    if subcmd and subcmd == 'full':
        await subcmd_long(client, message, args, is_admin=is_admin)
        return

    else:
        await subcmd_short(client, message, args, is_admin=is_admin)
