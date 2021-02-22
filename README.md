# MutualCredit_DiscordBot
A Discord Bot that adds a mutual credit system to your server.

*Note: This project is in very early alpha. It is not yet ready for actual use.*

## Todo
* README
  ** Better info to help devs to get started contributing
* Diagrams
  ** User workflow diagrams to make high-level understanding of how things work easier to understand.
* Data integrity
  ** There is currently little to no data integrity checks for what data is inserted into the database.
* Cleaner bot interface
  ** The current interface requires the user to perform a lot of actions by copying unique IDs for things. It would more user-friendly if this were abstracted away.
  ** The results returned from commands are also not all that user friendly as they're usually just python dictionaries.
* Private bot messaging
  ** At the moment, users can only send commands to the bot from public channels. Some results are sent via direct message to the calling user, but sending commands is not yet possible. Being able to keep all of your mutual credit commands and results from the bot in a single private channel with just yourself and the bot would keep public channels from being overwhelmed and allow for a legible and tidy personal bot history.
* Tests
  ** There are currently no tests. This is... bad.
* Error handling
  ** Saying that errors aren't handled gracefully is laughably understated. Right now they're just printed to the console and the channel in the original context of the command.
* Logging
  ** There are currently no robust logging features. This would be really helpful in debugging and error-recovery.
* Democratic control mechanisms
  ** A voting mechanism for deciding if a certain users is allowed to have a credit account would be cool. Currently, the bot just restricts credit commands to users with the 'member' role. This can be managed by whatever leadership already exists for the server; so maybe it isn't necessary for now.

## What *is* working
* Managing accounts (create, delete)
* Managing your accounts offers (create, delete, list)
* Listing offers from other accounts
* Creating transactions (buy requests) for another users offers
* Cancelling buy requests you created that are still pending
* Approving transactions (approving a buy request) sent to you
* Denying transactions (denying a buy request) sent to you
* Account balances are properly updated (so far -- no edge cases tested yet)

## Try me
The latest version of this project is running on a Discord server for testing and discussion.

Feel free to join and give the system a try:

https://discord.gg/ECKkNrjWrf

## Notes
You will need at least two users (other than the bot) to use this system.

## Deploy
First, set up an application and bot in the Discord developer portal and a guild (server) to use for testing. For info on how to do that you can follow the first part of [this guide](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal).

*TODO: Setting up bot permissions section*
For now, giving your bot `Administrator` permissions will due.

Note: You may need to enable `SERVER MEMBERS INTENT` on the bot page.

Create a `.env` file in the root project folder. It should contain the bot API token for your bot as follows: `DISCORD_TOKEN={YOUR_DISCORD_TOKEN_HERE}`

Before you can run the project you will need to install the Discord API wrapper for python:
```
pip install -U discord.py

# or if you're on windows
python -m pip install -U discord.py
```

Run `python bot.py`.

In the Discord server you connected the app to, add a new user role `member`.

Any user that is going to use the system must have the `member` role.
