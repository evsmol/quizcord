from discord import Message, Intents, errors
from discord.ext.commands import Bot, Context, errors
from discord_components import DiscordComponents, Interaction

import embeds
from core.config import DEVELOPERS_ID, BOT_ID
from core.button_parser import button_parser
from core.state_machine import QuizcordStateMachine, STATE_MACHINE
from data.quiz_func import add_quiz, update_quiz, get_server_quizzes, \
    get_user_quizzes
from data.question_func import update_question
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
        await button_parser(interaction, client)


# MESSAGES
@client.command(name='помощь')
async def get_help(ctx: Context):
    if ctx.guild:
        await ctx.channel.send(embed=embeds.Help(guild=True))
    else:
        await ctx.author.send(embed=embeds.Help(guild=False))


@client.command(name='квизы')
async def get_quizzes_for_server(ctx: Context, user_id=None):
    if ctx.guild:
        if not user_id:
            await ctx.channel.send(
                embed=embeds.ServerQuizzes(ctx.guild.id)
            )
        else:
            user_id = user_id.replace('<@!', '', 1)
            user_id = user_id.replace('<@', '', 1)
            user_id = user_id.replace('>', '', 1)
            try:
                user = client.get_user(int(user_id))
                if not user:
                    raise ValueError
            except ValueError:
                await ctx.channel.send('Введён некорректный id автора')
                return

            if user.id == int(BOT_ID):
                await ctx.channel.send(f'<@{BOT_ID}> пока не научился '
                                       f'создавать свои квизы')
            else:
                await get_quizzes_by_user(ctx, 'квизы', author=user)


@client.command(name='создать')
async def create_quiz(ctx: Context):
    if ctx.author.id in STATE_MACHINE:
        await ctx.send('Нельзя использовать команду в этом состоянии')
        return

    try:
        await ctx.author.send('Создаю новый квиз...')
        await ctx.author.send('*Учтите, что пустой квиз может быть удалён '
                              'при проверке модератором!*')
        if ctx.guild:
            await ctx.message.add_reaction('📨')
            quiz_id = add_quiz(ctx.author.id, ctx.guild.id)

            view_quiz = embeds.ViewQuiz(quiz_id, ctx.guild.name, ctx.author.id)
            await ctx.author.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )

        elif len(ctx.author.mutual_guilds) == 1:
            quiz_id = add_quiz(ctx.author.id, ctx.author.mutual_guilds[0].id)

            view_quiz = embeds.ViewQuiz(
                quiz_id,
                ctx.author.mutual_guilds[0].name,
                ctx.author.id
            )
            await ctx.author.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )

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
async def get_quizzes_by_user(ctx: Context, ctx2, author=None):
    if not author:
        author_id = ctx.author.id
        author_name = ctx.author.name
    else:
        author_id = author.id
        author_name = author.name

    match ctx2:
        case 'квизы':
            if ctx.guild:
                await ctx.channel.send(
                    embed=await embeds.embed_user_quizzes(author_id,
                                                          author_name,
                                                          ctx.guild.id))
            else:
                await ctx.author.send(
                    embed=await embeds.embed_user_quizzes(author_id,
                                                          author_name,
                                                          client=client))


@client.command(name='квиз')
async def get_quiz(ctx: Context, *quiz_id):
    if not quiz_id:
        msg = 'Отсутствует номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
    elif not quiz_id[0].isdigit() or len(quiz_id) > 1:
        msg = 'Введён некорректный номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
    elif ctx.guild:
        quiz_id = int(quiz_id[0])
        server_quizzes = get_server_quizzes(ctx.guild.id)
        quizzes_id = [quiz.id for quiz in server_quizzes]
        if quiz_id in quizzes_id:

            view_quiz = embeds.ViewQuiz(
                quiz_id,
                ctx.guild.name,
                ctx.author.id,
                is_server=True
            )
            await ctx.channel.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )
        else:
            await ctx.channel.send('Нет доступа к квизу')
    else:
        quiz_id = int(quiz_id[0])
        quizzes_list = get_user_quizzes(ctx.author.id)
        quizzes_id = [quiz.id for quiz in quizzes_list]
        quizzes_server_id = [quiz.server_id for quiz in quizzes_list]
        if quiz_id in quizzes_id:
            server = client.get_guild(
                quizzes_server_id[quizzes_id.index(quiz_id)])

            view_quiz = embeds.ViewQuiz(quiz_id, server.name, ctx.author.id)
            await ctx.author.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )
        else:
            await ctx.author.send('Нет доступа к квизу')


@client.command(name='рейтинг')
async def get_quiz(ctx: Context, *quiz_id):
    if not quiz_id:
        msg = 'Отсутствует номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
    elif not quiz_id[0].isdigit() or len(quiz_id) > 1:
        msg = 'Введён некорректный номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
    elif ctx.guild:
        quiz_id = int(quiz_id[0])
        server_quizzes = get_server_quizzes(ctx.guild.id)
        quizzes_id = [quiz.id for quiz in server_quizzes]
        if quiz_id in quizzes_id:
            await ctx.channel.send(
                embed=embeds.QuizRating(quiz_id),
            )
        else:
            await ctx.channel.send('Нет доступа к квизу')


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

                        quiz_id = add_quiz(message.author.id, server.id)
                        STATE_MACHINE[message.author.id].quiz_id = quiz_id
                        await message.author.send(
                            f'Вы выбрали сервер **{server.name}**'
                        )

                        view_quiz = embeds.ViewQuiz(
                            quiz_id,
                            server.name,
                            message.author.id
                        )
                        await message.author.send(
                            embed=view_quiz,
                            components=view_quiz.keyboard
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

                    update_quiz(quiz_id, title=message.content)

                    embed, keyboard = await embeds.embed_change_quiz(
                        int(quiz_id),
                        client
                    )
                    await message.author.send(
                        embed=embed,
                        components=keyboard
                    )
            case 'quiz_set_description':
                if len(message.content) > 2000:
                    await message.author.send(
                        'Описание не должно превышать 2000 символов. '
                        'Пожалуйста, введите его повторно')
                else:
                    STATE_MACHINE[message.author.id].quiz_description_changed()
                    quiz_id = STATE_MACHINE[message.author.id].quiz_id

                    if message.content == '.':
                        update_quiz(quiz_id, description='')
                    else:
                        update_quiz(quiz_id, description=message.content)

                    embed, keyboard = await embeds.embed_change_quiz(
                        int(quiz_id),
                        client
                    )
                    await message.author.send(
                        embed=embed,
                        components=keyboard
                    )
            case 'question_set_text':
                if len(message.content) > 200:
                    await message.author.send(
                        'Текст вопроса не должен превышать 200 символов. '
                        'Пожалуйста, введите его повторно')
                else:
                    STATE_MACHINE[message.author.id].question_text_changed()
                    question_id = STATE_MACHINE[message.author.id].question_id
                    number = STATE_MACHINE[message.author.id].question_number
                    quantity = \
                        STATE_MACHINE[message.author.id].question_quantity

                    update_question(question_id, text=message.content)

                    embed = embeds.ChangeQuestion(question_id, number,
                                                  quantity)

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
            case 'question_set_explanation':
                if len(message.content) > 2000:
                    await message.author.send(
                        'Пояснение не должно превышать 2000 символов. '
                        'Пожалуйста, введите его повторно')
                else:
                    STATE_MACHINE[
                        message.author.id].question_explanation_changed()
                    question_id = STATE_MACHINE[message.author.id].question_id
                    number = STATE_MACHINE[message.author.id].question_number
                    quantity = \
                        STATE_MACHINE[message.author.id].question_quantity

                    if message.content == '.':
                        update_question(
                            question_id,
                            explanation=''
                        )
                    else:
                        update_question(
                            question_id,
                            explanation=message.content
                        )

                    embed = embeds.ChangeQuestion(question_id, number,
                                                  quantity)

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
            case 'question_set_media':
                question_id = STATE_MACHINE[message.author.id].question_id
                number = STATE_MACHINE[message.author.id].question_number
                quantity = \
                    STATE_MACHINE[message.author.id].question_quantity

                try:
                    if message.content == '.':
                        update_question(
                            question_id,
                            media=''
                        )
                    else:
                        update_question(
                            question_id,
                            media=message.attachments[0].proxy_url
                        )

                    STATE_MACHINE[message.author.id].question_media_changed()

                    embed = embeds.ChangeQuestion(question_id, number,
                                                  quantity)

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
                except IndexError:
                    await message.author.send(
                        'Некорректный ввод. '
                        'Пожалуйста, отправьте файл повторно'
                    )
            case 'question_set_answers':
                answers = message.content.split('\n')
                if len(answers) > 5:
                    await message.author.send(
                        'Вариантов ответов не может быть больше 5. '
                        'Пожалуйста, введите их повторно')
                    return

                right_answer_count = 0
                right_answer = None
                for i, answer in enumerate(answers):
                    if answer.startswith('+'):
                        right_answer = i
                        right_answer_count += 1
                        answers[i] = answer.lstrip('+')

                if right_answer_count == 0:
                    await message.author.send(
                        'Верный вариант ответа не указан. '
                        'Пожалуйста, повторите ввод')
                    return
                if right_answer_count > 1:
                    await message.author.send(
                        'Указано несколько верных вариантов. '
                        'Пожалуйста, повторите ввод')
                    return

                question_id = STATE_MACHINE[message.author.id].question_id
                number = STATE_MACHINE[message.author.id].question_number
                quantity = STATE_MACHINE[message.author.id].question_quantity

                update_question(question_id,
                                answers=answers,
                                right_answer=right_answer)

                STATE_MACHINE[message.author.id].question_answers_changed()

                embed = embeds.ChangeQuestion(question_id, number, quantity)

                msg_media = await message.author.send('ᅠ')
                STATE_MACHINE[message.author.id].msg_media = msg_media
                if embed.media:
                    await msg_media.edit(embed.media)

                await message.author.send(
                    embed=embed,
                    components=embed.keyboard
                )


# ADMIN COMMANDS
@client.command(name='очистить')
async def del_empty_quizzes(ctx: Context, ctx2=None):
    if not ctx2:
        msg = 'Уточните, очистку каких компонентов необходимо выполнить'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        return
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
