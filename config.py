import os
import json
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Twitch API Credentials
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# Discord channel ID where notifications will be sent
NOTIFICATION_CHANNEL_ID = int(os.getenv('NOTIFICATION_CHANNEL_ID', '0'))

# File to store streamers data
STREAMERS_FILE = 'streamers.json'

def load_streamers():
    try:
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_streamers(streamers):
    with open(STREAMERS_FILE, 'w') as f:
        json.dump(streamers, f, indent=4) 