import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Planilha do Google
import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
# A credencial e o id devem mudar para o bot serio
cred = Credentials.from_service_account_file("credencial_teste.json", scopes=scopes)
client = gspread.authorize(cred)
sheet_id = "1vSCJAxKV7DqLsNzeqRjfT_1Vpd6U4U1bHlTjVT4iAgM"
sheet = client.open_by_key(sheet_id)
aba = sheet.worksheet("Presenca")


load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

class BotHype(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_voice_channel = None
        self.presenca_estado = {}  # {user_id: datetime}
        self.historico_presencas = defaultdict(list)  # {user_id: [(entrada, saida), ...]}

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"O {self.user} foi ligado com sucesso")

    async def on_voice_state_update(self, member, before, after):
        if member.bot or not self.current_voice_channel:
            return

        now = datetime.now()
        bot_channel = self.current_voice_channel
        canal_testes_id = bot.get_channel(1364736443628654614)

        if before.channel != after.channel:
            if after.channel == bot_channel and before.channel != bot_channel:
                self.presenca_estado[member.id] = now
                await canal_testes_id.send(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {member.display_name} entrou em {bot_channel.name}")

            elif before.channel == bot_channel and after.channel != bot_channel:
                entrada = self.presenca_estado.pop(member.id, None)
                if entrada:
                    self.historico_presencas[member.id].append((entrada, now))
                    tempo_total = now - entrada
                    linha = [
                        member.display_name,
                        str(bot_channel),
                        entrada.strftime("%Y-%m-%d %H:%M:%S"),
                        now.strftime("%Y-%m-%d %H:%M:%S"),
                        str(tempo_total)[:7]
                        
                    ]
                    aba.append_row(linha)
                    await canal_testes_id.send(
                        f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {member.display_name} saiu de {bot_channel.name} (Tempo em call: {tempo_total})"
                    )

bot = BotHype()

@bot.tree.command(name="comandos", description="Lista os comandos que o BotHype tem disponível")
async def Exibircomandos(interaction: discord.Interaction):
    await interaction.response.send_message("No momento não tenho nenhum comando, mas no futuro serei capaz de registrar em planilhas quem apareceu em chamadas de discord")


@bot.tree.command(name="registrar", description="O bot irá entrar na chamada e irá registrar os membros presentes")
async def registrar(interaction: discord.Interaction):
    now = datetime.now()

    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f'Entrei no canal de voz: {channel.name}')

        for member in channel.members:
            if not member.bot:
                bot.presenca_estado[member.id] = now
                canal_testes_id = bot.get_channel(1364736443628654614)
                await canal_testes_id.send(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {member.display_name} já estava presente em {channel.name}")

        bot.current_voice_channel = channel
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

        bot.current_voice_channel = None
        await voice_client.disconnect()
        await interaction.response.send_message("✅ Desconectado com sucesso!")

    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao sair: {str(e)}", ephemeral=True)

bot.run(discord_token)