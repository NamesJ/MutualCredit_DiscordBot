# bot.py
from credit_system import CreditSystem

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

cs = CreditSystem()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def mentionToId(mention):
    userId = mention
    if userId.startswith('<@') and userId.endswith('>'):
        userId = userId[2:-1]
    if userId.startswith('!'):
        userId = userId[1:]
    return int(userId)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='kill', help='Kill bot process')
@commands.has_role('admin')
async def kill_bot(ctx):
    exit()


@bot.command(name='clean_db', help='Reset database')
@commands.has_role('admin')
async def clean_db(ctx):
    cs.cleanDB()


@bot.command(name='mk_account', help='Create a new mutual credit account | !mk_account')
@commands.has_role('member')
async def mk_account(ctx):
    try:
        cs.createAccount(ctx.author.id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send('Mutual credit account created!')


@bot.command(name='balance', help='Show your account balance | !get_account_min_balance')
@commands.has_role('member')
async def balance(ctx):
    balance = None
    try:
        balance = cs.getBalance(ctx.author.id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
        raise
    else:
        await ctx.send(f'Account balance: ${balance}')


# Anything special needed for multiword arguments (space delimited but quoted)?
@bot.command(name='mk_offer', help='Create a new offer to your account | !mk_offer DESC PRICE TITLE')
@commands.has_role('member')
async def mk_offer(ctx, description, price: int, title):
    offerId = None
    try:
        offerId = cs.createOffer(ctx.author.id, description, price, title)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Offer ID: {offerId}')


@bot.command(name='add_cats', help='Add categories to an existing offer | !add_cats OFFER_ID CAT1 CAT2 CAT3...')
@commands.has_role('member')
async def add_cats(ctx, offer_id, *args):
    cnt = 0

    for category in args:
        try:
            cs.addCategoryToOffer(offer_id, category)
        except Exception as e:
            await ctx.send(str(e))
            print(e)
        else:
            cnt += 1

    await ctx.send(f'{cnt}/{len(args)} categories added to offer')


@bot.command(name='ls_cats', help='List categories associated with an existing offer | !ls_cats OFFER_ID')
@commands.has_role('member')
async def ls_cats(ctx, offer_id):
    try:
        categories = cs.getOfferCategories(offer_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        if len(categories) > 0:
            categories = ', '.join(categories)
        await ctx.send(f'Offer {offer_id} categories: {categories}')


@bot.command(name='rm_cats', help='Remove categories from an existing offer | !rm_cats OFFER_ID CAT1 CAT2 CAT3...')
@commands.has_role('member')
async def rm_cats(ctx, offer_id, *args):
    cnt = 0

    for category in args:
        try:
            cs.removeCategoryFromOffer(offer_id, category)
        except Exception as e:
            await ctx.send(str(e))
            print(e)
        else:
            cnt += 1

    await ctx.send(f'{cnt}/{len(args)} categories removed from offer')


@bot.command(name='rm_offer', help='Remove an offer from your account | !rm_offer OFFER_ID')
@commands.has_role('member')
async def rm_offer(ctx, offer_id):
    try:
        seller_id = cs.getOfferSeller(offer_id)
        if ctx.author.id != seller_id:
            raise Exception('User attempted to delete offer from another user\'s account')
        cs.deleteOffer(offer_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send('Offer has been removed!')


# Output needs better formatting
@bot.command(name='ls_offers', help='Get offers for a seller\'s account | !ls_offers SELLER')
@commands.has_role('member')
async def ls_offers(ctx, seller):
    seller_id = mentionToId(seller)
    offers = None
    try:
        offers = cs.getOffers(seller_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'{offers}')


@bot.command(name='buy', help='Send a request to buy an offer from a seller | !buy OFFER_ID')
@commands.has_role('member')
async def mk_buy(ctx, offer_id):
    tx_id = None
    try:
        tx_id = cs.createTransaction(ctx.author.id, offer_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Transaction ID: {tx_id}')
        #seller = discord.utils.get(guild.members, name=sellerName)
        seller_id = cs.getOfferSeller(offer_id)
        seller = ctx.guild.get_member(seller_id)
        tx = cs.getTransaction(tx_id)
        await seller.create_dm()
        await seller.dm_channel.send(
            f'New buy request:\n'
            f'{tx}'
        )


@bot.command(name='approve', help='Approve a buy request from another user | !approve TX_ID')
@commands.has_role('member')
async def approve_tx(ctx, tx_id):
    balance = None
    try:
        cs.approveTransaction(tx_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
        raise
    else:
        await ctx.send(f'Transaction approved!')
        balance = cs.getBalance(ctx.author.id)
        await ctx.send(f'New account balance: ${balance}')


@bot.command(name='cancel', help='Cancel your pending buy request | !cancel TX_ID')
@commands.has_role('member')
async def cancel_tx(ctx, tx_id):
    try:
        cs.cancelTransaction(tx_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Transaction cancelled!')


@bot.command(name='deny', help='Deny a request to buy | !deny TX_ID')
@commands.has_role('member')
async def deny_tx(ctx, tx_id):
    try:
        cs.denyTransaction(tx_id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Transaction denied!')


bot.run(TOKEN)






### For now, assuming all users in guild are members
