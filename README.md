# MutualCredit_DiscordBot
A Discord Bot that adds a mutual credit system to your server.

**THIS PROJECT SHOULD BE CONSIDERED ABANDONED. IT IS/WILL-BE DEPRECATED BY THE FOLLOWING PROJECTS:**

Back-end: [mutual-credit-server](https://github.com/NamesJ/mutual-credit-server)

Front-end: [mutual-credit-ui](https://github.com/NamesJ/mutual-credit-ui)

Bot Interface: [mutual-credit-bot](https://github.com/NamesJ/mutual-credit-bot)

## Features
* Managing account (create, delete, show balance)
* Managing your accounts offers (create, delete, show)
* Showing account offers of your and other user's accounts
* Creating transactions (buy requests) for offers
* Cancelling your pending buy requests
* Approving transactions (approving a buy request) sent to you from other users
* Denying transactions (denying a buy request) sent to you from other users
* Enforced maximum credit/debit limits for accounts
* DM (Private Messaging) for sending commands and receiving responses

## Try me
The latest version of this project is running on a Discord server for testing and discussion.

Feel free to join and give it a try:

https://discord.gg/ECKkNrjWrf

## Notes
*Python 3.7 or greater required*


You will need at least two users (other than the bot) to properly use this system, as transactions occur between two existing accounts.

## Deploy


First, set up an application and bot in the Discord developer portal and a guild (server) to use for testing. For info on how to do that you can follow the first part of [this guide](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal).

*TODO: Setting up bot permissions section*
For now, giving your bot `Administrator` permissions will due.

Note: You may need to enable `SERVER MEMBERS INTENT` on the bot page.


### Setup virtual environment and install dependencies
**Pipenv is used for managing both of these and is recommended**
```
# In project root directory...

## Spawns a shell within the virtualenv
pipenv shell

## Installs all packages specified in Pipfile.lock
pipenv sync
```

### Configure client Discord API key

Create a `.env` file in the root project folder.
It should contain the bot API token for your bot as follows: `DISCORD_TOKEN=<BOT_CLIENT_TOKEN>`, replacing `<BOT_CLIENT_TOKEN>` with the one found on the bot page of your application in the Discord developer portal.

Run `python client.py`.


### Configure the Discord server

In the Discord server you connected the app to, add a new user role `member`.

Any user that is going to use the system must have the `member` role.
