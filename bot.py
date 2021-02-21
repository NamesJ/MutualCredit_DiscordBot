# bot.py
import os

from credit_system import *

import discord
from discord.ext import commands
from dotenv import load_dotenv

creditSystem = CreditSystem()

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


@bot.command(name='mk_account', help='Create a new mutual credit account | !mk_account')
@commands.has_role('member')
async def mk_account(ctx):
    try:
        creditSystem.createAccount(ctx.author.id)
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
        balance = creditSystem.getBalance(ctx.author.id)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Account balance: ${balance}')


# Anything special needed for multiword arguments (space delimited but quoted)?
@bot.command(name='mk_offer', help='Create a new offer to your account | !mk_offer DESC PRICE TITLE')
@commands.has_role('member')
async def mk_offer(ctx, description, price: int, title):
    offerId = None
    try:
        offerId = creditSystem.createOffer(ctx.author.id, description, price, title)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Offer ID: {offerId}')


@bot.command(name='rm_offer', help='Remove an offer from your account | !rm_offer OFFER_ID')
@commands.has_role('member')
async def rm_offer(ctx, offerId):
    try:
        creditSystem.deleteOffer(ctx.author.id, offerId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send('Offer has been removed!')


# Output needs better formatting
@bot.command(name='ls_offers', help='Get offers for a seller\'s account | !ls_offers SELLER')
@commands.has_role('member')
async def ls_offers(ctx, seller):
    sellerId = mentionToId(seller)
    offers = None
    try:
        offers = creditSystem.getOffers(sellerId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'{offers}')


@bot.command(name='buy', help='Send a request to buy an offer from a seller | !buy OFFER_ID')
@commands.has_role('member')
async def mk_buy(ctx, offerId):
    txId = None
    try:
        txId = creditSystem.createTransaction(ctx.author.id, offerId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Transaction ID: {txId}')
        #seller = discord.utils.get(guild.members, name=sellerName)
        sellerId = creditSystem.getSellerIdByOfferId(offerId)
        seller = ctx.guild.get_member(sellerId)
        tx = creditSystem.getTransaction(txId)
        await seller.create_dm()
        await seller.dm_channel.send(
            f'New buy request:\n'
            f'{tx}'
        )


@bot.command(name='approve', help='Approve a buy request from another user | !approve TX_ID')
@commands.has_role('member')
async def approve_tx(ctx, txId):
    balance = None
    try:
        creditSystem.approveTransaction(txId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
    else:
        await ctx.send(f'Transaction approved!')
        balance = creditSystem.getAccountBalance(ctx.author.id)
        await ctx.send(f'New account balance: ${balance}')


@bot.command(name='cancel', help='Cancel your pending buy request | !cancel TX_ID')
@commands.has_role('member')
async def cancel_tx(ctx, txId):
    try:
        creditSystem.cancelTransaction(txId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
        raise
    else:
        await ctx.send(f'Transaction cancelled!')


@bot.command(name='deny', help='Deny a request to buy | !deny TX_ID')
@commands.has_role('member')
async def deny_tx(ctx, txId):
    try:
        creditSystem.denyTransaction(txId)
    except Exception as e:
        await ctx.send(str(e))
        print(e)
        raise
    else:
        await ctx.send(f'Transaction denied!')


bot.run(TOKEN)






### For now, assuming all users in guild are members
