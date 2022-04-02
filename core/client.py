from discord import Intents
from discord.ext.commands import Bot
from discord_components import DiscordComponents, Interaction


intents = Intents.default()
intents.members = True
intents.presences = True
client = Bot(command_prefix='-', intents=intents)


# SERVICE
@client.event
async def on_connect():
    print("[BOT] Connected!")


@client.event
async def on_ready():
    # ADD COMPONENTS
    DiscordComponents(client)

    # REPORT
    print(f"[BOT] Ready! Logged in as {client.user}")


# # BUTTONS
# @client.event
# async def on_button_click(interaction: Interaction):
#     if not interaction.responded:
#         try:
#             await button_parser(interaction)
#         except NotFound:
#             pass


# MESSAGES
@client.command(name='повторить')
async def test(message, *arg):
    await message.send(';'.join(arg))
