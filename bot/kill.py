from .utils import role_check

import shlex
import logging

log = logging.getLogger(__name__)


async def handle(client, message, args): # admin-only command
    if len(args) > 0:
        raise Exception(f'This command takes no arguments.')

    user = message.author
    is_admin = await role_check(client, user.id, 'admin')
    is_member = await role_check(client, user.id, 'member')

    if not is_admin:
        raise Exception('You do not have permission to do that.')
        log.warning(f'Non-admin user {user} tried to kill bot.')

    quit()
