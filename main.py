import os
import logging
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram Bot API token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Create an Updater for the bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


# Define the start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot to download Instagram Reels. Just send me the Reel URL.")

# Define the message handler
def handle_message(update, context):
    message = update.message
    # Check if the message contains a URL
    if message.entities and message.entities[0].type == 'url':
        url = message.text
        # Process the URL and download the Reel
        reel_url = extract_reel_url(url)
        if reel_url:
            reel_file = download_reel(reel_url)
            if reel_file:
                # Send the Reel file back to the user
                context.bot.send_video(chat_id=update.effective_chat.id, video=open(reel_file, 'rb'))
                # Clean up the downloaded file
                os.remove(reel_file)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to download the Reel.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Reel URL.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a valid Reel URL.")


def extract_reel_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            video_element = soup.find('video')
            if video_element and video_element.has_attr('src'):
                reel_url = video_element['src']
                return reel_url
    except Exception as e:
        logging.error("Error extracting Reel URL: %s", str(e))
    return None


def download_reel(url):
    reel_file = 'reel.mp4'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(reel_file, 'wb') as f:
                f.write(response.content)
            return reel_file
    except Exception as e:
        logging.error("Error downloading Reel: %s", str(e))
    return None


# Register handlers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.text & (~Filters.command), handle_message)
dispatcher.add_handler(message_handler)

# Start the bot
updater.start_polling()
