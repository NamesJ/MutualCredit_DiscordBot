from . import vouch_system as vs

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX='!'

try: intents
except NameError: intents = discord.Intents.default()
finally: intents.members = True



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


@commands.command(name='bootstrap_vouch', help='Bootstrap yourself as first member of vouch system | !bootstrap_vouch')
@commands.has_role('admin')
async def bootstrap_vouch(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    try:
        vs.bootstrap(ctx.author.id)
    except Exception as e:
        await sendDM(member, str(e))
    else:
        await sendDM(member, f'Bootstrap was successful. You are the first member!')


@commands.command(name='check_membership', help='Shows your current membership status | !check_membership')
async def check_membership(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    if vs.isMember(ctx.author.id):
        await sendDM(member, f'You are currently a member!')
    else:
        await sendDM(member, f'You are not currently a member.')


@commands.command(name='check_vouches', help='Shows how many vouches you have and need | !check_vouches')
async def check_vouches(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    vouchee_id = ctx.author.id
    if vs.isMember(vouchee_id):
        await sendDM(member, f'You are already a member!')
    else:
        actual = vs.getVoucheeValue(vouchee_id)
        required = vs.thresholdApprove()
        await sendDM(member, f'You currently have {actual}/{required} vouches.')


@commands.command(name='vouch', help='Create or change vouch for another user | !vouch @USER [n/no|p/pass|y/yes]')
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

            for role in ctx.guild.roles:
                if role.name != 'member': continue
                await new_member.add_roles(role)
                
            await sendDM(new_member, f'Congratulations, you are now a member')


BOT_COMMANDS = [
    bootstrap_vouch,
    check_membership,
    check_vouches,
    vouch
]


if __name__ == '__main__':
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    for cmd in BOT_COMMANDS:
        bot.add_command(cmd)
    bot.run(TOKEN)
