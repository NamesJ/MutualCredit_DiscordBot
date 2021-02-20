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


@bot.command(name='create_account', help='Create a new mutual credit account')
@commands.has_role('member')
async def create_account(ctx):
    creditSystem.createAccount(ctx.author.id)
    await ctx.send('Mutual credit account created!')


@bot.command(name='show_balance', help='Show account balance')
@commands.has_role('member')
async def show_balance(ctx):
    balance = None
    try:
        balance = creditSystem.getBalance(ctx.author.id)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Account balance: ${balance}')


# Anything special needed for multiword arguments (space delimited but quoted)?
@bot.command(name='create_offer', help='Create a new offer to your account\nArgs: DESC PRICE TITLE')
@commands.has_role('member')
async def create_offer(ctx, description, price: int, title):
    offerId = None
    try:
        offerId = creditSystem.createOffer(ctx.author.id, description, price, title)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    except Exception as e:
        raise
    else:
        await ctx.send(f'Offer ID: {offerId}')


@bot.command(name='delete_offer', help='Remove an existing offer from your account\nArgs: OFFER_ID')
@commands.has_role('member')
async def remove_offer(ctx, offerId):
    try:
        creditSystem.deleteOffer(ctx.author.id, offerId)
    except Exception as e:
        await ctx.send(str(e))
    else:
        await ctx.send('Offer has been removed!')


# Output needs better formatting
@bot.command(name='get_offers', help='Get offers for a seller\'s account\nArgs: SELLER_NAME')
@commands.has_role('member')
async def get_offers(ctx, seller):
    sellerId = mentionToId(seller)
    offers = None
    try:
        offers = creditSystem.getOffers(sellerId)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'{offers}')


@bot.command(name='request_buy', help='Request a transaction to buy an offer from a seller\nArgs: SELLER_NAME OFFER_ID')
@commands.has_role('member')
async def request_buy(ctx, sellerMention, offerId):
    sellerId = mentionToId(sellerMention)
    txId = None
    try:
        txId = creditSystem.createTransaction(ctx.author.id, sellerId, offerId)
    except Exception as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction created with ID "{txId}"')
        #seller = discord.utils.get(guild.members, name=sellerName)
        seller = ctx.guild.get_member(sellerId)
        tx = creditSystem.getTransaction(txId)
        await seller.create_dm()
        await seller.dm_channel.send(
            f'New buy request:\n'
            f'{tx}'
        )


@bot.command(name='approve_tx', help='Approve a pending buy request from a buyer\nArgs: TX_ID')
@commands.has_role('member')
async def approve_tx(ctx, txId):
    balance = None
    try:
        creditSystem.approveTransaction(txId)
    except InvalidTransactionIdError as e:
        await ctx.send(str(e))
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    except AccountBalanceAboveMaxError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction approved!')
        balance = creditSystem.getAccountBalance(ctx.author.id)
        await ctx.send(f'New account balance: ${balance}')


@bot.command(name='cancel_tx', help='Cancel your pending buy request\nArgs: TX_ID')
@commands.has_role('member')
async def cancel_tx(ctx, txId):
    try:
        creditSystem.cancelTransaction(txId)
    except Exception as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction cancelled!')


@bot.command(name='deny_tx', help='Deny a pending buy request from a buyer\nArgs: TX_ID')
@commands.has_role('member')
async def deny_tx(ctx, txId):
    try:
        creditSystem.denyTransaction(txId)
    except Exception as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction denied!')


bot.run(TOKEN)






### For now, assuming all users in guild are members
