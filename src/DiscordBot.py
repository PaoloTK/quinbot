# QuinBot.py
import discord
import gettext
import json
import logging
import os
import re
import sys

from aliexpress_api import AliexpressApi, models
from discord import app_commands
from dotenv import load_dotenv
from slash_commands import register_commands

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load environment variables and initialize settings
load_dotenv()

ALI_APP_KEY = os.getenv('ALI_APP_KEY')
ALI_APP_SECRET = os.getenv('ALI_APP_SECRET')
AMAZON_TAG = os.getenv('AMAZON_TAG')
COMMUNITY = os.getenv('COMMUNITY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
LED_SETUP_TALK_CHANNEL_ID = int(os.getenv('LED_SETUP_TALK_CHANNEL_ID'))

ALIEXPRESS_REGEX = "(http[s]?://[a-zA-Z0-9.-]+aliexpress\.(com|us)(?:.+?dl_target_url=(.+)|[^ \n?]+?(?:\.html)|[^ \n?]+))"
AMAZON_REGEX = "(http[s]?://[a-zA-Z0-9.-]*(?:amazon|amzn)\.[a-zA-Z]+(?:.+?(?:ref=[^?]+)|.+(?= )|[^?]+))"

# Load objects from JSON
def load_json(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as file:
        objects = json.load(file)
    return objects

aliexpress = AliexpressApi(ALI_APP_KEY, ALI_APP_SECRET, models.Language.EN, models.Currency.EUR, "discord")
logging.info(aliexpress)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
bot_name = "Bot" # Replaced at runtime
tree = app_commands.CommandTree(client)

def get_username_for_message(message):
    username = message.author.display_name or message.author.name
    return username
    
def get_amazon_affiliate_link(url):
    template = messages.get('AmazonAffiliateLink', "")
    return template.format(url=url, AMAZON_TAG=AMAZON_TAG)

async def handle_new_setup_talk_thread(message):
    thread = message.channel
    channel = message.channel.parent

    if hasattr(message, "position") and message.position == 0 and hasattr(message, "attachments") and len(message.attachments) == 0:
        template = messages.get("NoAttachment","")
        username = get_username_for_message(message)
        channel_name = channel.name

        logging.info('User {} has been informed about best practices in {} channel'.format(username, message.channel.name))
        await thread.send(content=template.format(username=username, channel_name=channel_name, bot_name=bot_name), delete_after=300)

@client.event
async def on_ready():
    bot_name=client.user.name
    logging.info('{} has connected to Discord!'.format(bot_name))
    # Sync bot commands to server
    if GUILD_ID:
        commands = load_json('commands.json')
        await register_commands(tree, commands, GUILD_ID)
        await tree.sync(guild=discord.Object(GUILD_ID))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # HANDLING LED SETUP TALK
    if LED_SETUP_TALK_CHANNEL_ID: 
        if hasattr(message, "channel") and isinstance(message.channel, discord.Thread) and hasattr(message.channel, "parent") and isinstance(message.channel.parent, discord.ForumChannel) and message.channel.parent.id == LED_SETUP_TALK_CHANNEL_ID:
            
            await handle_new_setup_talk_thread(message)

    affiliate_links = []

    if ALI_APP_KEY and ALI_APP_SECRET:
        for match in re.findall(ALIEXPRESS_REGEX, message.content):
            ali_affiliate_links = aliexpress.get_affiliate_links(match[0])
            affiliate_link = ''
            if len(ali_affiliate_links) > 0 and hasattr(ali_affiliate_links[0], 'promotion_link'):
                affiliate_link = ali_affiliate_links[0].promotion_link
            else:
                template = messages.get("BlockedAffiliate","")
                affiliate_link = template.format(url=format(ali_affiliate_links[0].source_value) if hasattr(ali_affiliate_links[0], 'source_value') else '!')
            affiliate_links.append(affiliate_link)
        
    if AMAZON_TAG:
        for match in re.findall(AMAZON_REGEX, message.content):
            affiliate_links.append(get_amazon_affiliate_link(match))

    if affiliate_links:
        username = get_username_for_message(message)

        template = messages.get("Affiliate","")
        community = COMMUNITY if COMMUNITY else "this community"
        response = template.format(community=community, username=username)
        for affiliate_link in affiliate_links:
            response += "\n" + affiliate_link

        logging.info('Replaced {} link(s) in {} channel from {} message'.format(len(affiliate_links), message.channel.name, username))

        await message.channel.send(response)

if __name__ == "__main__":
    messages = load_json('messages.json')

    if not ALI_APP_KEY or not ALI_APP_SECRET:
        logging.warning("Aliexpress environment variables haven't been configured, Aliexpress affiliate won't work")
    if not AMAZON_TAG:
        logging.warning("Amazon environment variable hasn't been configured, Amazon affiliate won't work")
    if not LED_SETUP_TALK_CHANNEL_ID:
        logging.warning("Led Setup Talk environment variable hasn't been configured, the bot won't advise users on best practices")
    if not GUILD_ID:
        logging.warning("Guild ID environment variable hasn't been configured, commands won't be synced")

    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
    else:
        logging.critical("DISCORD_TOKEN environment variable hasn't been configured, exiting")
        sys.exit(1)
    
