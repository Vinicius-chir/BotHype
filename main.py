import discord
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

class BotHype(discord.Client):
    
    def __init__(self): # self referencia-se a própria classe
        intents = discord.Intents.all()
        super().__init__(
            command_prefix = "$", # Comando de prefixo que o bot "lê" para responder as mensagens
            intents = intents
        )
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self): #Lista de comando
        await self.tree.sync()
    
    async def on_ready(self):
        print(f"O {self.user} foi ligado com sucesso") # Mensagem de quando o bot for ligado

bot = BotHype()

@bot.tree.command(name="comandos", description="Lista os comandos que o BotHype tem disponível")
async def comandos(interaction:discord.Interaction):
    await interaction.response.send_message("No momento não tenho nenhum comando, mas no futuro serei capaz de registrar em planilhas quem apareceu em chamadas de discord")

bot.run(discord_token)