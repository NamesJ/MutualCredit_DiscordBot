from discord.utils import get



def role_check(client, account_id, role_name):
    user = get(client.get_all_members(), id=account_id)

    for guild in client.guilds:
        role = get(guild.roles, name=role_name)
        if role is None:
            continue

        if role in user.roles:
            return True

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


def user_from_id(client, user_id):
    user = get(client.get_all_members(), id=user_id)

    return user
