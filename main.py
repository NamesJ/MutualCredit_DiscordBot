from bot.client import client

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


if __name__ == '__main__':
    try:
        client.run(TOKEN)
    except Exception as e:
        print(str(e))
