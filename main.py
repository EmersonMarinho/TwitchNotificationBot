import discord
from discord import app_commands
from discord.ext import tasks
import requests
import config
import asyncio
from typing import Optional

class StreamNotifier(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.tree = app_commands.CommandTree(self)
        self.streamers_status = {}
        self.access_token = None
        self.streamers = config.load_streamers()
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

    @tasks.loop(minutes=1)
    async def check_streams(self):
        for username, info in self.streamers.items():
            is_live, stream_data = self.check_stream_status(username)
            was_live = self.streamers_status.get(username, False)
            
            if is_live and not was_live:
                channel = self.get_channel(config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    user_info = self.get_user_info(username)
                    
                    embed = discord.Embed(
                        title=f"Twitch Alerts 🔔",
                        description="Live On",
                        color=0x6441a5
                    )
                    
                    # Adiciona o campo principal com o título da stream
                    stream_title = f"[LIVE] {username}\n{stream_data['title']}"
                    if info.get('description'):
                        stream_title += f"\n{info['description']}"
                    
                    embed.add_field(
                        name="",
                        value=stream_title,
                        inline=False
                    )
                    
                    # Adiciona a thumbnail do jogo
                    if user_info and user_info.get('profile_image_url'):
                        embed.set_thumbnail(url=user_info['profile_image_url'])
                    
                    # Adiciona os botões
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label=f"Twitch.tv/{username}",
                        url=f"https://twitch.tv/{username}"
                    ))
                    view.add_item(discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label="Watch VOD",
                        url=f"https://twitch.tv/{username}/videos"
                    ))
                    
                    await channel.send(embed=embed, view=view)
            
            self.streamers_status[username] = is_live

    async def setup_hook(self):
        await self.tree.sync()
        self.check_streams.start()

    async def on_ready(self):
        print(f'Bot está online como {self.user}')

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
    config.save_streamers(client.streamers)
    
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
        config.save_streamers(client.streamers)
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