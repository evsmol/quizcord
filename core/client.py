from discord import Message, Intents, errors
from discord.ext.commands import Bot, Context, errors
from discord_components import DiscordComponents, Interaction

import embeds
from core.config import DEVELOPERS_ID
from core.button_parser import button_parser
from core.state_machine import QuizcordStateMachine, STATE_MACHINE
from data.quiz_func import add_quiz, update_quiz
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
        await ctx.channel.send(embed=embeds.Help(guild=True))
    else:
        await ctx.author.send(embed=embeds.Help(guild=False))


@client.command(name='создать')
async def create_quiz(ctx: Context):
    if ctx.author.id in STATE_MACHINE:
        await ctx.send('Нельзя использовать команду в этом состоянии')
        return

    try:
        await ctx.author.send('Создаю новый квиз...')
        await ctx.author.send('*Учтите, что пустой квиз может быть удалён '
                              'при проверке модератором!ඞ*')
        if ctx.guild:
            await ctx.message.add_reaction('📨')
            quiz_id = add_quiz(ctx.author.id, ctx.guild.id)
            await ctx.author.send(
                embed=embeds.ViewQuiz(quiz_id, ctx.guild.name, ctx.author.id),
                components=embeds.ViewQuiz(quiz_id, ctx.guild.name,
                                           ctx.author.id).keyboard)

        elif len(ctx.author.mutual_guilds) == 1:
            quiz_id = add_quiz(ctx.author.id, ctx.author.mutual_guilds[0].id)
            await ctx.author.send(
                embed=embeds.ViewQuiz(quiz_id,
                                      ctx.author.mutual_guilds[0].name,
                                      ctx.author.id),
                components=embeds.ViewQuiz(quiz_id,
                                           ctx.author.mutual_guilds[0].name,
                                           ctx.author.id).keyboard)

        else:
            STATE_MACHINE[ctx.author.id] = QuizcordStateMachine(
                initial='quiz_set_server')
            STATE_MACHINE[ctx.author.id].servers = ctx.author.mutual_guilds
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


@client.command(name='отмена')
async def cancel(ctx: Context):
    if ctx.author.id in STATE_MACHINE:
        del STATE_MACHINE[ctx.author.id]
        await ctx.send('Текущая команда отменена')
    else:
        await ctx.send('Нет команды для отмены...')


@client.event
async def on_message(message: Message):
    if message.content.startswith(client.command_prefix):
        await client.process_commands(message)

    elif message.author.id in STATE_MACHINE and not message.guild:
        user = STATE_MACHINE[message.author.id]
        match user.state:
            case 'quiz_set_server':
                if user.servers != message.author.mutual_guilds:
                    STATE_MACHINE[message.author.id].servers = \
                        message.author.mutual_guilds
                    await message.author.send(
                        'Список Ваших серверов был изменён. '
                        'Пожалуйста, выберите сервер повторно')

                    servers_names = [server.name
                                     for server
                                     in message.author.mutual_guilds]
                    await message.author.send(
                        embed=embeds.ChooseServer(servers_names))

                elif message.content.isdigit():
                    if 0 < int(message.content) <= len(user.servers):
                        server = user.servers[int(message.content) - 1]

                        update_quiz(user.quiz_id, server_id=server.id)
                        await message.author.send(
                            f'Вы выбрали сервер **{server.name}**'
                        )
                        await message.author.send(
                            embed=embeds.ViewQuiz(user.quiz_id, server.name,
                                                  message.author.id),
                            components=embeds.ViewQuiz(
                                user.quiz_id,
                                server.name,
                                message.author.id
                            ).keyboard
                        )
                        del STATE_MACHINE[message.author.id]
                    else:
                        await message.author.send(
                            'Нет сервера с таким номером. '
                            'Пожалуйста, выберите сервер повторно'
                        )
                else:
                    await message.author.send(
                        'Некорректный ввод. '
                        'Пожалуйста, выберите сервер повторно'
                    )
            case 'quiz_set_title':
                if len(message.content) > 200:
                    await message.author.send(
                        'Название не должно превышать 200 символов. '
                        'Пожалуйста, введите его повторно')
                else:
                    STATE_MACHINE[message.author.id].quiz_title_changed()
                    quiz_id = STATE_MACHINE[message.author.id].quiz_id
                    server_name = STATE_MACHINE[message.author.id].server_name

                    update_quiz(quiz_id, title=message.content)

                    await message.author.send(
                        embed=embeds.ChangeQuiz(int(quiz_id), server_name),
                        components=embeds.ChangeQuiz(int(quiz_id),
                                                     server_name).keyboard)
            case 'quiz_set_description':
                if len(message.content) > 2000:
                    await message.author.send(
                        'Описание не должно превышать 2000 символов. '
                        'Пожалуйста, введите его повторно')
                else:
                    STATE_MACHINE[message.author.id].quiz_description_changed()
                    quiz_id = STATE_MACHINE[message.author.id].quiz_id
                    server_name = STATE_MACHINE[message.author.id].server_name

                    if message.content == '.':
                        update_quiz(quiz_id, description='')
                    else:
                        update_quiz(quiz_id, description=message.content)

                    await message.author.send(
                        embed=embeds.ChangeQuiz(int(quiz_id), server_name),
                        components=embeds.ChangeQuiz(int(quiz_id),
                                                     server_name).keyboard)


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
