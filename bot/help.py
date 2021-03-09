from .utils import role_check

import shlex


async def subcmd_long(client, message, args):
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    response = '''
!help output

**Create an account (member-only)**
*You must run this command first to use any of the commands below*
`!account create`

**Check your allowance (max debit/credit) (member-only)**
`!account allowance`

**Check your balance (member-only)**
*Returns account balance, available balance (balance - pending transfer requests sent from you) and pending sales (pending transfer requests sent to you) for your offers)*
`!account balance`

**Add one or more categories to an offer (member-only)**
`!category add OFFER_ID CATEGORY [CATEGORY ...]`

**Remote one or more categories from an offer (member-only)**
`!category remove OFFER_ID CATEGORY [CATEGORY ...]`
'''

    if role_check(client, user.id, 'admin'):
        response +='''
**Show this help message**
`!help`

**Kill the bot (admin-only)**
`!kill`
'''

    response += '''
**Create a new offer (optionally with one or more categories)**
`!offer add TITLE PRICE DESCRIPTION [CATEGORY CATEGORY ...]`

**Remove one or more of your offers (member-only)**
`!offer remove OFFER_ID [OFFER_ID OFFER_ID]`

**Show offers from an account (member-only)**
*`@USER` indicates that your should use a `mention` ('@' someone)*
`!offer show @USER`

**Approve a transfer request from someone (member-only)**
*The buyer(s) will be notified that you have denied their request(s)*
*If successful, the offer price(s) will be added to your balance*
`!transaction approve TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Cancel one or more of your pending transfer requests (member-only)**
*The seller(s) will be notified that your request(s) have been cancelled*
`!transaction cancel TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Deny a transfer request from someone (member-only)**
*The buyer(s) will be notified that you have denied their request(s)*
`!transaction deny TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Create a transfer request for one or more offers (member-only)**
*The seller(s) will be notified of your request(s)*
`!transaction request OFFER_ID [OFFER_ID OFFER_ID ...]`'''

    await message.reply(response)


async def subcmd_short(client, message, args):
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    response = '''
!help output

`!account allowance`
`!account balance`
`!account create`
`!category add OFFER_ID CATEGORY [CATEGORY ...]`
`!category remove OFFER_ID CATEGORY [CATEGORY ...]`'''

    if role_check(client, user.id, 'admin'):
        response +='''
`!help`
`!kill`'''

    response += '''
`!offer add TITLE PRICE DESCRIPTION [CATEGORY CATEGORY ...]`
`!offer remove OFFER_ID [OFFER_ID OFFER_ID]`
`!offer show @USER`
`!transaction cancel TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`
`!transaction deny TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`
`!transaction request OFFER_ID [OFFER_ID OFFER_ID ...]`'''

    await message.reply(response)


async def handle(client, message, args):
    subcmd = None

    if len(args) > 0:
        subcmd = args[0]
        args = args[1:]

    user = message.author

    if not role_check(client, user.id, 'member'):
        await message.reply('No commands exist for non-members.')
        return

    if subcmd and subcmd == 'long':
        await subcmd_long(client, message, args)
        return

    else:
        await subcmd_short(client, message, args)
