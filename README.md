# Discord Stream Notifier Bot

Este bot do Discord notifica quando um streamer específico da Twitch começa uma transmissão ao vivo.

## Configuração Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
DISCORD_TOKEN=seu_token_do_discord
TWITCH_CLIENT_ID=seu_client_id_da_twitch
TWITCH_CLIENT_SECRET=seu_client_secret_da_twitch
NOTIFICATION_CHANNEL_ID=id_do_canal_de_notificacoes
```

## Deploy

### Railway (Recomendado)
1. Crie uma conta no [Railway](https://railway.app/)
2. Conecte com seu GitHub
3. Crie um novo projeto
4. Selecione "Deploy from GitHub repo"
5. Configure as variáveis de ambiente:
   - DISCORD_TOKEN
   - TWITCH_CLIENT_ID
   - TWITCH_CLIENT_SECRET
   - NOTIFICATION_CHANNEL_ID
6. O deploy será automático

### Heroku
1. Crie uma conta no [Heroku](https://heroku.com)
2. Instale o [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Login no Heroku:
```bash
heroku login
```
4. Crie um novo app:
```bash
heroku create seu-app-name
```
5. Configure as variáveis de ambiente:
```bash
heroku config:set DISCORD_TOKEN=seu_token
heroku config:set TWITCH_CLIENT_ID=seu_client_id
heroku config:set TWITCH_CLIENT_SECRET=seu_client_secret
heroku config:set NOTIFICATION_CHANNEL_ID=seu_channel_id
```
6. Deploy:
```bash
git push heroku main
```

## Comandos

- `/ping` - Verifica se o bot está online
- `/add username "descrição"` - Adiciona um streamer
- `/remove username` - Remove um streamer
- `/list` - Lista todos os streamers monitorados 