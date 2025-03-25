import os
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
NOTIFICATION_CHANNEL_ID = int(os.getenv('NOTIFICATION_CHANNEL_ID', 0))

# Configurações da Twitch
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# Verifica se as variáveis de ambiente foram carregadas corretamente
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não encontrado no arquivo .env")
if not TWITCH_CLIENT_ID:
    raise ValueError("TWITCH_CLIENT_ID não encontrado no arquivo .env")
if not TWITCH_CLIENT_SECRET:
    raise ValueError("TWITCH_CLIENT_SECRET não encontrado no arquivo .env")
if not NOTIFICATION_CHANNEL_ID:
    raise ValueError("NOTIFICATION_CHANNEL_ID não encontrado no arquivo .env")

print(f"Configurações carregadas:")
print(f"Channel ID: {NOTIFICATION_CHANNEL_ID}")
print(f"Twitch Client ID: {TWITCH_CLIENT_ID}")
print(f"Discord Token: {'Presente' if DISCORD_TOKEN else 'Ausente'}")
print(f"Twitch Client Secret: {'Presente' if TWITCH_CLIENT_SECRET else 'Ausente'}")

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