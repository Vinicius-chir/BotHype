import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

class BotHype(discord.Client):
    
    def __init__(self): # self referencia-se a própria classe
        intents = discord.Intents.all()
        super().__init__(
            command_prefix = "h!", # Comando de prefixo que o bot "lê" para responder as mensagens
            intents = intents
        )
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self): #Lista de comando
        await self.tree.sync()
    
    async def on_ready(self):
        print(f"O {self.user} foi ligado com sucesso") # Mensagem de quando o bot for ligado

bot = BotHype()

@bot.tree.command(name="comandos", description="Lista os comandos que o BotHype tem disponível")
async def Exibircomandos(interaction:discord.Interaction):
    await interaction.response.send_message("No momento não tenho nenhum comando, mas no futuro serei capaz de registrar em planilhas quem apareceu em chamadas de discord")

@bot.tree.command(name="registrar", description="O bot irá entrar na chamada e irá registrar os membros presentes em uma planilha")
async def registrar(interaction: discord.Interaction):
    if interaction.user.voice:  
        channel = interaction.user.voice.channel
        await channel.connect() # Espera conectar na call
        await interaction.response.send_message(f'Entrei no canal de voz: {channel.name}')
    else:
        await interaction.response.send_message('❌ Você não está em um canal de voz!')

@bot.tree.command(name="sair", description="Desconecta o bot do canal de voz")
async def sair(interaction: discord.Interaction):
    try:
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            return await interaction.response.send_message("❌ Não estou em nenhum canal de voz!", ephemeral=True)
            
        if interaction.user.voice and interaction.user.voice.channel != voice_client.channel:
            return await interaction.response.send_message(
                "❌ Você precisa estar no mesmo canal que eu para me desconectar!",
                ephemeral=True
            )
        
        await voice_client.disconnect()
        await interaction.response.send_message("✅ Desconectado com sucesso!")
    
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao sair: {str(e)}", ephemeral=True)


bot.run(discord_token)