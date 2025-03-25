# Discord Twitch Stream Notifier

Um bot do Discord que notifica quando streamers específicos começam uma transmissão ao vivo na Twitch.

## Funcionalidades

- 🔔 Notifica quando streamers específicos começam uma live
- 📊 Mostra informações da stream (título, jogo, espectadores)
- 🔗 Botões para assistir a live e ver VODs
- 📝 Suporte a descrições personalizadas para cada streamer
- ⚡ Verificação automática a cada minuto
- 📋 Comandos para gerenciar streamers monitorados
- 🔄 Sistema de logging para debug

## Comandos

- `/ping` - Verifica se o bot está online
- `/add <username> [description]` - Adiciona um streamer para monitorar
- `/remove <username>` - Remove um streamer da lista
- `/list` - Lista todos os streamers monitorados com seus status

## Configuração

1. Clone este repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
   DISCORD_TOKEN=seu_token_do_discord
   TWITCH_CLIENT_ID=seu_client_id_da_twitch
   TWITCH_CLIENT_SECRET=seu_client_secret_da_twitch
   NOTIFICATION_CHANNEL_ID=id_do_canal_discord
   ```

4. Configure as permissões do bot no canal:
   - Ver Canais
   - Enviar Mensagens
   - Incorporar Links (Embed Links)
   - Usar Links Externos
   - Ler Histórico de Mensagens

## Como Obter as Credenciais

### Discord Token
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá para a seção "Bot"
4. Clique em "Reset Token" para obter o token
5. Ative as opções "MESSAGE CONTENT INTENT" e "SERVER MEMBERS INTENT"

### Twitch Credentials
1. Acesse o [Twitch Developer Console](https://dev.twitch.tv/console)
2. Registre uma nova aplicação
3. Copie o Client ID
4. Gere um novo Client Secret

### Channel ID
1. Ative o "Modo Desenvolvedor" nas configurações do Discord
2. Clique com o botão direito no canal desejado
3. Selecione "Copiar ID"

## Executando o Bot

### Windows (Início Automático)
1. Execute o arquivo `start_bot.bat`
2. Execute o arquivo `create_startup_shortcut.vbs` para configurar início automático
3. O bot iniciará automaticamente quando o Windows iniciar

### Manual
```bash
python main.py
```

## Logs e Debug

O bot gera logs detalhados no arquivo `bot.log`. Use este arquivo para:
- Verificar erros
- Monitorar o funcionamento do bot
- Debug de problemas

## Contribuindo

Sinta-se à vontade para contribuir com o projeto! Abra uma issue ou envie um pull request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 