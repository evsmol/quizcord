from discord import Intents, errors
from discord.ext.commands import Bot, Context
from discord_components import DiscordComponents, Interaction

import embeds
from core.config import DEVELOPERS_ID
from core.button_parser import button_parser
from data.quiz_func import add_quiz
from data.admin_func import delete_empty_quizzes

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
async def get_server_quizzes(ctx: Context):
    if ctx.guild:
        await ctx.channel.send(embed=embeds.ServerQuizzes(ctx.guild.id))


@client.command(name='помощь')
async def get_help(ctx: Context):
    if ctx.guild:
        await ctx.channel.send(embed=embeds.Help(),
                               components=embeds.help.keyboard)


@client.command(name='создать')
async def create_quiz(ctx: Context):
    try:
        await ctx.author.send('Создаю новый квиз...')
        await ctx.author.send('*Учтите, что пустой квиз может быть удалён '
                              'при проверке модератором!*')
        if ctx.guild:
            await ctx.message.add_reaction('📨')
            quiz_id = add_quiz(ctx.author.id, ctx.guild.id)
            await ctx.author.send(
                embed=embeds.ChangeQuiz(quiz_id, ctx.guild.name),
                components=embeds.change_quiz.keyboard_no_published)
        elif len(ctx.author.mutual_guilds) == 1:
            quiz_id = add_quiz(ctx.author.id, ctx.author.mutual_guilds[0].id)
            await ctx.author.send(
                embed=embeds.ChangeQuiz(quiz_id,
                                        ctx.author.mutual_guilds[0].name),
                components=embeds.change_quiz.keyboard_published)
        else:
            quiz_id = add_quiz(ctx.author.id)
            servers_names = [server.name
                             for server in ctx.author.mutual_guilds]
            await ctx.author.send(embed=embeds.ChooseServer(servers_names))
    except errors.Forbidden as e:
        await ctx.channel.send('Чтобы создать квиз, откройте доступ к личным '
                               'сообщениям')
        print(f'[ERROR] {e}')


@client.command(name='мои')
async def get_user_quizzes(ctx: Context, ctx2):
    match ctx2:
        case 'квизы':
            if ctx.guild:
                await ctx.channel.send(
                    embed=await embeds.UserQuizzes(ctx.author.id,
                                                   ctx.author.name,
                                                   ctx.guild.id))
            else:
                await ctx.author.send(
                    embed=await embeds.UserQuizzes(ctx.author.id,
                                                   ctx.author.name,
                                                   client=client))


# @client.command(name='квиз')
# async def show_quiz(ctx: Context, param):


# ADMIN COMMANDS
@client.command(name='очистить')
async def del_empty_quizzes(ctx: Context, ctx2):
    if ctx.author.id not in DEVELOPERS_ID:
        msg = 'Эта команда доступна только разработчикам'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        return
    match ctx2:
        case 'квизы':
            delete_empty_quizzes()
            await ctx.message.add_reaction('✅')
