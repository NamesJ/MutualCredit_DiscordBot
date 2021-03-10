import discord.utils
from discord.utils import get

import logging

log = logging.getLogger(__name__)


async def role_check(client, account_id, role_name):
    log.debug(f'role_check: arguments=({account_id}, {role_name})')

    all_roles = []

    for guild in client.guilds:
        all_roles += guild.roles

    allowed_role = discord.utils.find(lambda r: r.name==role_name, all_roles)

    if not allowed_role:
        log.error(f'role_check: role "{role_name}" is not known by client')

    user = discord.utils.find(lambda m: m.id==account_id, client.get_all_members())

    if not user:
        log.debug(f'role_check: user with ID "{account_id}" not found in client members list')

    if allowed_role in user.roles:
        log.debug(f'role_check: pass')
        return True

    log.debug(f'role_check: fail')

    return False


def find_subcommands(module):
    subcmds = []

    for name in dir(module):
        item = getattr(module, name)

        if str(type(item)) != "<class 'function'>":
            continue

        if not name.startswith('subcmd_'):
            continue

        subcmds.append(name)


def mention_to_id(mention):
    user_id = mention

    if user_id.startswith('<@') and user_id.endswith('>'):
        user_id = user_id[2:-1]
    if user_id.startswith('!'):
        user_id = user_id[1:]

    try:
        return int(user_id)

    except Exception as e:
        print(e)
        return None


async def user_from_id(client, user_id):
    user = get(client.get_all_members(), id=user_id)

    return user
