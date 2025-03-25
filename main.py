import discord
from discord import app_commands
from discord.ext import tasks
import requests
import config
import asyncio
from typing import Optional
import json
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class StreamNotifier(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.tree = app_commands.CommandTree(self)
        self.streamers_status = {}
        self.access_token = None
        self.streamers = self.load_streamers()
        self.get_twitch_token()

    def get_twitch_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": config.TWITCH_CLIENT_ID,
            "client_secret": config.TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, params=params)
        self.access_token = response.json()["access_token"]

    def check_stream_status(self, username):
        headers = {
            "Client-ID": config.TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.twitch.tv/helix/streams?user_login={username}"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data["data"]:
            return True, data["data"][0]
        return False, None

    def get_user_info(self, username):
        headers = {
            "Client-ID": config.TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.twitch.tv/helix/users?login={username}"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data["data"]:
            return data["data"][0]
        return None

    def load_streamers(self):
        try:
            if os.path.exists('streamers.json'):
                with open('streamers.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Erro ao carregar streamers: {e}")
            return {}

    def save_streamers(self, streamers):
        try:
            with open('streamers.json', 'w') as f:
                json.dump(streamers, f, indent=4)
        except Exception as e:
            logging.error(f"Erro ao salvar streamers: {e}")

    @tasks.loop(minutes=1)
    async def check_streams(self):
        try:
            streamers = self.load_streamers()
            if not streamers:
                return

            # Obter token de acesso da Twitch
            token_response = requests.post(
                'https://id.twitch.tv/oauth2/token',
                params={
                    'client_id': config.TWITCH_CLIENT_ID,
                    'client_secret': config.TWITCH_CLIENT_SECRET,
                    'grant_type': 'client_credentials'
                }
            )
            token_data = token_response.json()
            access_token = token_data['access_token']

            # Verificar cada streamer
            for username in streamers.keys():
                try:
                    headers = {
                        'Client-ID': config.TWITCH_CLIENT_ID,
                        'Authorization': f'Bearer {access_token}'
                    }
                    
                    # Buscar informações do usuário
                    user_response = requests.get(
                        f'https://api.twitch.tv/helix/users',
                        headers=headers,
                        params={'login': username}
                    )
                    user_data = user_response.json()
                    
                    if not user_data['data']:
                        logging.warning(f"Usuário {username} não encontrado na Twitch")
                        continue
                        
                    user_id = user_data['data'][0]['id']
                    
                    # Buscar informações da stream
                    stream_response = requests.get(
                        f'https://api.twitch.tv/helix/streams',
                        headers=headers,
                        params={'user_id': user_id}
                    )
                    stream_data = stream_response.json()
                    
                    is_live = bool(stream_data['data'])
                    was_live = self.streamers_status.get(username, False)
                    
                    if is_live and not was_live:
                        try:
                            channel = self.get_channel(config.NOTIFICATION_CHANNEL_ID)
                            if not channel:
                                logging.error(f"Canal {config.NOTIFICATION_CHANNEL_ID} não encontrado")
                                continue
                                
                            stream_info = stream_data['data'][0]
                            embed = discord.Embed(
                                title="Twitch Alerts 🔔",
                                description=f"**{username}** está ao vivo!",
                                color=discord.Color.purple(),
                                url=f"https://twitch.tv/{username}"
                            )
                            
                            embed.add_field(
                                name="Título",
                                value=stream_info['title'],
                                inline=False
                            )
                            
                            embed.add_field(
                                name="Jogando",
                                value=stream_info['game_name'],
                                inline=True
                            )
                            
                            embed.add_field(
                                name="Espectadores",
                                value=str(stream_info['viewer_count']),
                                inline=True
                            )
                            
                            embed.set_thumbnail(url=user_data['data'][0]['profile_image_url'])
                            
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(label="Assistir Live", url=f"https://twitch.tv/{username}", style=discord.ButtonStyle.url))
                            view.add_item(discord.ui.Button(label="VODs", url=f"https://twitch.tv/{username}/videos", style=discord.ButtonStyle.url))
                            
                            await channel.send(embed=embed, view=view)
                            logging.info(f"Notificação enviada para {username}")
                        except discord.Forbidden as e:
                            logging.error(f"Erro de permissão ao enviar mensagem: {e}")
                        except Exception as e:
                            logging.error(f"Erro ao enviar notificação: {e}")
                    
                    self.streamers_status[username] = is_live
                    
                except Exception as e:
                    logging.error(f"Erro ao verificar streamer {username}: {e}")
                    continue
                
        except Exception as e:
            logging.error(f"Erro geral no check_streams: {e}")

    async def setup_hook(self):
        await self.tree.sync()
        self.check_streams.start()

    async def on_ready(self):
        logging.info(f'Bot está online como {self.user}')
        self.check_streams()

client = StreamNotifier()

@client.tree.command(name="add", description="Adiciona um streamer para monitorar")
@app_commands.describe(
    username="Nome do usuário da Twitch",
    description="Descrição personalizada (opcional)"
)
async def add_streamer(interaction: discord.Interaction, username: str, description: Optional[str] = None):
    username = username.lower()
    
    # Verifica se o streamer existe
    user_info = client.get_user_info(username)
    if not user_info:
        await interaction.response.send_message(f"❌ Streamer '{username}' não encontrado na Twitch!", ephemeral=True)
        return
    
    # Adiciona ou atualiza o streamer
    client.streamers[username] = {"description": description}
    client.save_streamers(client.streamers)
    
    await interaction.response.send_message(
        f"✅ Streamer '{username}' adicionado com sucesso!" +
        (f"\nDescrição: {description}" if description else ""),
        ephemeral=True
    )

@client.tree.command(name="remove", description="Remove um streamer da lista de monitoramento")
@app_commands.describe(username="Nome do usuário da Twitch")
async def remove_streamer(interaction: discord.Interaction, username: str):
    username = username.lower()
    if username in client.streamers:
        del client.streamers[username]
        client.save_streamers(client.streamers)
        await interaction.response.send_message(f"✅ Streamer '{username}' removido com sucesso!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Streamer '{username}' não está na lista!", ephemeral=True)

@client.tree.command(name="list", description="Lista todos os streamers monitorados")
async def list_streamers(interaction: discord.Interaction):
    if not client.streamers:
        await interaction.response.send_message("Nenhum streamer está sendo monitorado!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 Streamers Monitorados",
        color=discord.Color.blue()
    )
    
    for username, info in client.streamers.items():
        status = "🔴 Live" if client.streamers_status.get(username, False) else "⭕ Offline"
        description = f"\nDescrição: {info['description']}" if info.get('description') else ""
        embed.add_field(
            name=f"{status} {username}",
            value=description or "Sem descrição",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="ping", description="Responde com Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

client.run(config.DISCORD_TOKEN) 