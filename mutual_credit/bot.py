# bot.py
from .credit_system import CreditSystem

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX='!'
intents = discord.Intents.default()
intents.members = True

cs = CreditSystem()


def mentionToId(mention):
    userId = mention
    if userId.startswith('<@') and userId.endswith('>'):
        userId = userId[2:-1]
    if userId.startswith('!'):
        userId = userId[1:]
    return int(userId)


async def sendDM(user, message):
    await user.create_dm()
    await user.dm_channel.send(message)


@commands.command(name='mk_account', help='Create a new mutual credit account | !mk_account')
@commands.has_role('member')
async def mk_account(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    try:
        cs.createAccount(ctx.author.id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(member, 'Mutual credit account created!')


@commands.command(name='balance', help='Show your account balance | !get_account_min_balance')
@commands.has_role('member')
async def balance(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    balance = None
    try:
        balance = cs.getBalance(ctx.author.id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
        raise
    else:
        await sendDM(member, f'Account balance: ${balance}')


# Anything special needed for multiword arguments (space delimited but quoted)?
@commands.command(name='mk_offer', help='Create a new offer to your account | !mk_offer DESC PRICE TITLE')
@commands.has_role('member')
async def mk_offer(ctx, description, price: int, title):
    member = ctx.guild.get_member(ctx.author.id)
    offerId = None
    try:
        offerId = cs.createOffer(ctx.author.id, description, price, title)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(member, f'Offer created with ID {offerId}')


@commands.command(name='add_cats', help='Add categories to an existing offer | !add_cats OFFER_ID CAT1 CAT2 CAT3...')
@commands.has_role('member')
async def add_cats(ctx, offer_id, *args):
    member = ctx.guild.get_member(ctx.author.id)
    cnt = 0

    for category in args:
        try:
            cs.addCategoryToOffer(offer_id, category)
        except Exception as e:
            await sendDM(member, str(e))
            print(e)
        else:
            cnt += 1

    await sendDM(member, f'{cnt}/{len(args)} categories added to offer with ID {offer_id}')


@commands.command(name='ls_cats', help='List categories associated with an existing offer | !ls_cats OFFER_ID')
@commands.has_role('member')
async def ls_cats(ctx, offer_id):
    member = ctx.guild.get_member(ctx.author.id)
    try:
        categories = cs.getOfferCategories(offer_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        if len(categories) > 0:
            categories = ', '.join(categories)
        await sendDM(member, f'Offer {offer_id} categories: {categories}')


@commands.command(name='rm_cats', help='Remove categories from an existing offer | !rm_cats OFFER_ID CAT1 CAT2 CAT3...')
@commands.has_role('member')
async def rm_cats(ctx, offer_id, *args):
    member = ctx.guild.get_member(ctx.author.id)
    cnt = 0

    for category in args:
        try:
            cs.removeCategoryFromOffer(offer_id, category)
        except Exception as e:
            await sendDM(member, str(e))
            print(e)
        else:
            cnt += 1

    await sendDM(member, f'{cnt}/{len(args)} categories removed from offer with ID {offer_id}')


@commands.command(name='rm_offer', help='Remove an offer from your account | !rm_offer OFFER_ID')
@commands.has_role('member')
async def rm_offer(ctx, offer_id):
    member = ctx.guild.get_member(ctx.author.id)
    try:
        seller_id = cs.getOfferSeller(offer_id)
        if ctx.author.id != seller_id:
            await sendDM(member, 'You can\'t delete an offer from another member\'s account!')
        cs.deleteOffer(offer_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await sendDM(member, 'Offer has been removed!')


# Output needs better formatting
@commands.command(name='ls_offers', help='Get offers for a seller\'s account | !ls_offers SELLER')
@commands.has_role('member')
async def ls_offers(ctx, seller):
    member = ctx.guild.get_member(ctx.author.id)
    seller_id = mentionToId(seller)
    offers = None
    try:
        offers = cs.getOffers(seller_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(member, f'{offers}')


@commands.command(name='ls_range', help='Get min/max balance range for your account | !ls_range')
@commands.has_role('member')
async def ls_range(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    try:
        min_balance, max_balance = cs.getAccountRange(ctx.author.id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(member, f'The range for your account is ${min_balance} to ${max_balance}')



@commands.command(name='buy', help='Send a request to buy an offer from a seller | !buy OFFER_ID')
@commands.has_role('member')
async def mk_buy(ctx, offer_id):
    member = ctx.guild.get_member(ctx.author.id)
    tx_id = None
    try:
        tx_id = cs.createTransaction(ctx.author.id, offer_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        seller_id = cs.getOfferSeller(offer_id)
        seller = ctx.guild.get_member(seller_id)
        await sendDM(member, f'You requested to buy {offer_id} from {seller.name}. Transaction ID: {tx_id}')
        await sendDM(seller, f'New buy request from {ctx.author.name} for offer {offer_id}. Transaction ID: {tx_id}')


@commands.command(name='approve', help='Approve a buy request from another user | !approve TX_ID')
@commands.has_role('member')
async def approve_tx(ctx, tx_id):
    member = ctx.guild.get_member(ctx.author.id)
    buyer_id = cs.getTransactionBuyer(tx_id)
    buyer = ctx.guild.get_member(buyer_id)
    balance = None
    try:
        cs.approveTransaction(tx_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(buyer, f'{ctx.author.name} approved your buy request with ID {tx_id}')
        await sendDM(member, f'Transaction {tx_id} approved!')
        balance = cs.getBalance(ctx.author.id)
        await sendDM(member, f'New account balance: ${balance}')


@commands.command(name='cancel', help='Cancel your pending buy request | !cancel TX_ID')
@commands.has_role('member')
async def cancel_tx(ctx, tx_id):
    member = ctx.guild.get_member(ctx.author.id)
    seller_id = cs.getTransactionSeller(tx_id)
    seller = ctx.guild.get_member(seller_id)
    try:
        cs.cancelTransaction(tx_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(seller, f'{ctx.author.name} cancelled their buy request with ID {tx_id}')
        await sendDM(member, f'Transaction {tx_id} cancelled!')


@commands.command(name='deny', help='Deny a request to buy | !deny TX_ID')
@commands.has_role('member')
async def deny_tx(ctx, tx_id):
    member = ctx.guild.get_member(ctx.author.id)
    buyer_id = cs.getTransactionBuyer(tx_id)
    buyer = ctx.guild.get_member(buyer_id)
    try:
        cs.denyTransaction(tx_id)
    except Exception as e:
        await sendDM(member, str(e))
        print(e)
    else:
        await sendDM(buyer, f'{ctx.author.name} denied your buy request with ID {tx_id}')
        await sendDM(member, f'Transaction {tx_id} denied!')

BOT_COMMANDS = [
    add_cats,
    approve_tx,
    balance,
    cancel_tx,
    #clean_db,
    deny_tx,
    #kill_bot,
    ls_cats,
    ls_offers,
    ls_range,
    mk_account,
    mk_buy,
    mk_offer,
    rm_cats,
    rm_offer
]


if __name__ == '__main__':
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    for cmd in BOT_COMMANDS:
        bot.add_command(cmd)
    bot.run(TOKEN)






### For now, assuming all users in guild are members
