from . import vouch_system as vs

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


try: TOKEN
except:
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

try: COMMAND_PREFIX
except: COMMAND_PREFIX='!'

try: intents
except NameError: intents = discord.Intents.default()
finally: intents.members = True

try: bot
except: bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)



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


@bot.command(name='vouch', help='Create or change vouch for another user | !vouch @USER [n/no|p/pass|y/yes]')
@commands.has_role('member')
async def vouch(ctx, mention, value):
    member = ctx.guild.get_member(ctx.author.id)
    vouchee_id = mentionToId(mention)
    voucher_id = ctx.author.id
    membership_before = vs.isMember(vouchee_id)

    try:
        if value.lower() in ['n', 'no']:
            vs.vouchNegative(voucher_id, vouchee_id)
        elif value.lower() in ['p', 'pass']:
            vs.vouchNeutral(voucher_id, vouchee_id)
        elif value.lower() in ['y', 'yes']:
            vs.vouchPositive(voucher_id, vouchee_id)
        else:
            raise Exception(f'Invalid value called for !vouch: {ctx.message}')
    except Exception as e:
            await sendDM(member, str(e))
    else:
        membership_after = vs.isMember(vouchee_id)
        if membership_after and not membership_before: # new member
            new_member = ctx.guild.get_member(vouchee_id)
            await sendDM(f'Congratulations, you are now a member')


@bot.command(name='check_vouches', help='Shows how many vouches you have and need | !check_vouches')
async def vouch(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    vouchee_id = ctx.author.id
    actual = vs.getVoucheeValue()
    required = vs.thresholdApprove()
    await sendDM(member, f'You currently have {actual}/{required} vouches.')


@bot.command(name='check_membership', help='Shows your current membership status | !check_membership')
async def check_membership(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    if vs.isMember():
        await sendDM(member, f'You are currently a member!')
    else:
        await sendDM(member, f'You are not currently a member.')


if __name__ == '__main__':
    bot.run(TOKEN)
