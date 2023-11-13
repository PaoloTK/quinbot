# Quinbot

## Credits

Quinbot is based off https://github.com/hacf-fr/Discord-AffiliateBot. Credits go to them for getting the initial affiliate functionality into it <3

## Dev env setup
1. `cp .env.sample .env`
2. Add the missing values to .env. If you don't know them: Sad.

## Running the bot

### Inside docker
1. `docker-compose up -d`

### In foreground / bash
1. `cd src`
2. `source ../.env && ../pybot/bin/python3 DiscordBot.py`