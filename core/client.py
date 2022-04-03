from discord import Intents
from discord.ext.commands import Bot, CommandInvokeError
from discord_components import DiscordComponents, Interaction

import embeds
from core.button_parser import button_parser
from data.quiz_func import add_quiz

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


# BUTTONS
@client.event
async def on_button_click(interaction: Interaction):
    if not interaction.responded:
        await button_parser(interaction)


# MESSAGES
@client.command(name='квизы')
async def get_server_quizzes(message):
    if message.guild:
        await message.send(embed=embeds.ServerQuizzes(message.guild.id))


@client.command(name='помощь')
async def get_help(message):
    if message.guild:
        await message.send(embed=embeds.Help(),
                           components=embeds.help.keyboard)


@client.command(name='создать')
async def create_quiz(message):
    try:
        await message.author.send('Создаю новый квиз...')
        if message.guild:
            quiz_id = add_quiz(message.author.id, message.guild.id)
            await message.author.send(
                embed=embeds.ChangeQuiz(quiz_id, message.guild.name),
                components=embeds.change_quiz.keyboard)
        else:
            quiz_id = add_quiz(message.author.id)
    except Exception as e:
        await message.send('Чтобы создать квиз, откройте доступ к личным '
                           'сообщениям')
        print(f'[ERROR] {e}')
