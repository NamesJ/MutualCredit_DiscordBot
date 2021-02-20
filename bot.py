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

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='create_account', help='Create a new mutual credit account')
@commands.has_role('member')
async def create_account(ctx):
    accountInfo = creditSystem.createAccount(ctx.author.name)
    await ctx.send('Mutual credit account created!')
    await ctx.send(f'{accountInfo}')


@bot.command(name='show_balance', help='Show account balance')
@commands.has_role('member')
async def show_balance(ctx):
    balance = None
    try:
        balance = creditSystem.getAccountBalance(ctx.author.name)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Account balance: ${balance}')


# Anything special needed for multiword arguments (space delimited but quoted)?
@bot.command(name='create_offer', help='Create a new offer to your account\nArgs: DESC PRICE TITLE')
@commands.has_role('member')
async def create_offer(ctx, description, price: int, title):
    offerData = None
    try:
        offerData = creditSystem.createAccountOffer(ctx.author.name, description, price, title)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    except Exception as e:
        raise
    else:
        await ctx.send(f'Offer ID: {offerData}')


@bot.command(name='get_account_offers', help='Get offers for a seller\'s account\nArgs: SELLER_NAME')
@commands.has_role('member')
async def get_account_offers(ctx, sellerName):
    offersData = None
    try:
        offersData = creditSystem.getAccountOffersData(sellerName)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'{sellerName}\'s offers:')
        await ctx.send(f'{offersData}')


@bot.command(name='get_offer_info', help='Get info about a seller\'s offer by ID\nArgs: SELLER_NAME OFFER_ID')
@commands.has_role('member')
async def get_offer_info(ctx, sellerName, offerId):
    offerData = None
    try:
        offerData = creditSystem.getAccountOfferData(sellerName, offerId)
    except InvalidAccountIdError as e:
        await ctx.send(str(e))
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'{offerData}')



@bot.command(name='remove_offer', help='Remove an existing offer from your account\nArgs: OFFER_ID')
@commands.has_role('member')
async def remove_offer(ctx, offerId):
    try:
        creditSystem.removeAccountOffer(ctx.author.name, offerId)
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send('Offer has been removed!')


@bot.command(name='request_buy', help='Request a transaction to buy an offer from a seller\nArgs: SELLER_NAME OFFER_ID')
@commands.has_role('member')
async def request_buy(ctx, sellerName, offerId):
    txData = None
    try:
        txData = creditSystem.requestTransaction(ctx.author.name, sellerName, offerId)
    except BuyerIsSellerError as e:
        await ctx.send(str(e))
    except InvalidOfferIdError as e:
        await ctx.send(str(e))
    except AccountBalanceBelowMinError as e:
        await ctx.send(str(e))
    except Exception as e:
        raise
    else:
        await ctx.send(f'Transaction created: {txData}')
        # send message to seller to notify them
        guild = ctx.guild
        seller = discord.utils.get(guild.members, name=sellerName)
        offerData = creditSystem.getAccountOfferData(sellerName, offerId)
        #del txData['offerId'] # not necessary, adding offerData instead
        txData['offer'] = offerData
        await seller.create_dm()
        await seller.dm_channel.send(
            f'New buy request:\n'
            f'{txData}'
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
        balance = creditSystem.getAccountBalance(ctx.author.name)
        await ctx.send(f'New account balance: ${balance}')


@bot.command(name='cancel_tx', help='Cancel your pending buy request\nArgs: TX_ID')
@commands.has_role('member')
async def cancel_tx(ctx, txId):
    try:
        creditSystem.cancelTransaction(txId)
    except InvalidTransactionIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction "{txId}" cancelled.')


@bot.command(name='deny_tx', help='Deny a pending buy request from a buyer\nArgs: TX_ID')
@commands.has_role('member')
async def deny_tx(ctx, txId):
    try:
        creditSystem.denyTransaction(txId)
    except InvalidTransactionIdError as e:
        await ctx.send(str(e))
    else:
        await ctx.send(f'Transaction "{txId}" denied.')


bot.run(TOKEN)






### For now, assuming all users in guild are members
