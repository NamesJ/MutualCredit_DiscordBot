from .utils import role_check

import shlex


async def handle(client, message, args): # admin-only command
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author

    if not role_check(client, user.id, 'admin'):
        await message.reply('You do not have permission to do that.')
        raise Exception(f'Non-admin user {user} tried to kill bot.')

    quit()
