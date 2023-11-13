# bot.py
import gettext
import os
import re
# from pprint import pprint
import urllib.parse

import discord
from aliexpress_api import AliexpressApi, models
from dotenv import load_dotenv

load_dotenv()

try:
    traduction = gettext.translation('discord_affiliatebot', localedir='locale')
    traduction.install()
except FileNotFoundError:
    traduction = gettext.translation('discord_affiliatebot', localedir='locale', languages=["en"])
    traduction.install()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ALI_APP_KEY = os.getenv('ALI_APP_KEY')
ALI_APP_SECRET = os.getenv('ALI_APP_SECRET')
AMAZON_TAG = os.getenv('AMAZON_TAG')
COMMUNITY = os.getenv('COMMUNITY')
LED_SETUP_TALK_CHANNEL_ID = int(os.getenv('LED_SETUP_TALK_CHANNEL_ID'))

# ALIEXPRESS_REGEX = "(http[s]?://[a-zA-Z0-9.-]+aliexpress\.com(?:.+?dl_target_url=(.+)|[^\s\n?]+?(?:.html)|[^\s\n?]+))"
ALIEXPRESS_REGEX = "(http[s]?://[a-zA-Z0-9.-]+aliexpress\.(com|us)(?:.+?dl_target_url=(.+)|[^ \n?]+?(?:\.html)|[^ \n?]+))"
AMAZON_REGEX = "(http[s]?://[a-zA-Z0-9.-]*(?:amazon|amzn)\.[a-zA-Z]+(?:.+?(?:ref=[^?]+)|.+(?= )|[^?]+))"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
aliexpress = AliexpressApi(ALI_APP_KEY, ALI_APP_SECRET, models.Language.EN, models.Currency.EUR, "discord")

def getUserNameForMessage(message):
    userName = message.author.name
    if hasattr(message.author, "display_name") and message.author.display_name is not None:
        userName = message.author.display_name
    if hasattr(message.author, "nick") and message.author.nick is not None:
        userName = message.author.nick

    return userName
    

async def handleNewSetupTalkThread(message):
    thread = message.channel
    channel = message.channel.parent

    if hasattr(message, "position") and message.position == 0 and hasattr(message, "attachments") and len(message.attachments) == 0:
        userName = getUserNameForMessage(message)

        await thread.send(content='''Dear {:s},

thanks for your post in #{:s}!

I've detected that you didn't attach an image to your post: Please remember that if you would like to get support for a project, an install or just a general wiring question, it's **extremely** helpful to get a rough drawing of your planned setup!

Also a kind reminder: Please see the post guidelines! You can find them at the top of the channel by clicking on the icon that looks like a :orange_book: with a :ballot_box_with_check:!

Thanks for helping us to help you! :)

Sincerely,
{:s}!'''.format(userName, message.channel.parent.name, client.user.name), delete_after=300)

@client.event
async def on_ready():
    print('{} has connected to Discord!'.format(client.user.name))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # HANDLING LED SETUP TALK
    if LED_SETUP_TALK_CHANNEL_ID is not None and hasattr(message, "channel") and isinstance(message.channel, discord.Thread) and hasattr(message.channel, "parent") and isinstance(message.channel.parent, discord.ForumChannel) and message.channel.parent.id == LED_SETUP_TALK_CHANNEL_ID:
        await handleNewSetupTalkThread(message)

    if message.content == '!affiliate check':
        await message.channel.send('{} affiliate bot is running !'.format(COMMUNITY))
        return

    affiliate_links = []

    if ALI_APP_KEY:
        for match in re.findall(ALIEXPRESS_REGEX, message.content):
            ali_affiliate_links = aliexpress.get_affiliate_links(match[0])
            affiliate_link = ''
            if len(ali_affiliate_links) > 0 and hasattr(ali_affiliate_links[0], 'promotion_link'):
                affiliate_link = ali_affiliate_links[0].promotion_link
            else:
                affiliate_link = 'This seller does not allow direct affiliate links, sorry{:s}'.format(': {:s}'.format(ali_affiliate_links[0].source_value) if hasattr(ali_affiliate_links[0], 'source_value') else '!')
            affiliate_links.append(affiliate_link)
    if AMAZON_TAG:
        for match in re.findall(AMAZON_REGEX, message.content):
            affiliate_links.append(get_amazon_affiliate_link(match))

    if affiliate_links:
        userName = getUserNameForMessage(message)

        response = traduction.ngettext('Support {} by using this affiliate link posted by {}:',
                                       'Support {} by using these affiliate links posted by {}:',
                                       len(affiliate_links)).format(COMMUNITY, userName)
        for affiliate_link in affiliate_links:
            response += "\n" + affiliate_link

        if isinstance(message.channel, discord.DMChannel):
            print(traduction.ngettext('Replaced {} link in DM',
                                      'Replaced {} links in DM',
                                      len(affiliate_links))
                  .format(len(affiliate_links)))
        else:
            print(traduction.ngettext('Replaced {} link in {} channel from {} message on {} server',
                                      'Replaced {} links in {} channel from {} message on {} server',
                                      len(affiliate_links))
                  .format(len(affiliate_links), message.channel.name, userName, message.guild.name))

        await message.channel.send(response)

        if message.content.startswith('!affiliate '):
            await message.delete()


def get_amazon_affiliate_link(url):
    return url + f'?tag={AMAZON_TAG}'


if DISCORD_TOKEN:
  client.run(DISCORD_TOKEN)
else:
  print("Fatal: No DISCORD_TOKEN")
