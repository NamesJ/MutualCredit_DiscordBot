# MutualCredit_DiscordBot
A Discord Bot that adds a mutual credit system to your server

## Todo
* Persistence / database
  ** Currently, there is no persistence whatsoever. If the program crashes or gets reset, all of the data is gone.
* Cleaner bot interface
  ** The current interface performs a lot of actions by referencing an unwieldly unique ID for referring to a specific offer or transaction. It would be much better if this were abstracted away.
  ** The results returned from commands are also not all that user friendly as they're usually just python dictionaries.
* Democratic control mechanisms
  ** A voting mechanism for deciding if a certain users is allowed to have a credit account would be cool. Currently, the bot just restricts credit commands to users with the 'member' role. This can be managed by whatever leadership already exists for the server; so maybe it isn't necessary for now.
* Private bot messaging
  ** At the moment, users can only send commands to the bot from public channels. Some results are sent via direct message to the calling user, but sending commands is not yet possible. Being able to keep all of your mutual credit commands and results from the bot in a single private channel with just yourself and the bot would keep public channels from being overwhelmed and allow for a legible and tidy personal bot history.

## Deploy
First, set up an application and bot in the Discord developer portal and a guild (server) to use for testing. For info on how to do that you can follow the first part of [this guide](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal).

Create a `.env` file in the root project folder. It should contain the API token for your bot as follows:
`DISCORD_TOKEN={YOUR_DISCORD_TOKEN_HERE}`

Then run `python bot.py`.
