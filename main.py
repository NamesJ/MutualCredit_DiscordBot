from bot.client import client

from dotenv import load_dotenv
import os
import logging

log = logging.getLogger(__name__)

load_dotenv()


logging.basicConfig(level=os.getenv('LOG_LEVEL', logging.INFO))




if __name__ == '__main__':
    try:
        client.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        log.exception(f'Exception in main: {str(e)}')
