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
    embed = embeds.Help()
    if ctx.guild:
        await ctx.channel.send(embed=embed, components=embed.keyboard)
        print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> открывает '
              f'справочник')
    else:
        await ctx.author.send(embed=embed, components=embed.keyboard)
        print(f'[PERSONAL] {ctx.author.name} <{ctx.author.id}> открывает '
              f'справочник')


@client.command(name='квизы')
async def get_quizzes_for_server(ctx: Context, user_id=None):
    if ctx.guild:
        if not user_id:
            await ctx.channel.send(
                embed=embeds.ServerQuizzes(ctx.guild.id)
            )
            print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> получает '
                  f'список серверных квизов')
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
                print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> '
                      f'попытался получить список квизов от пользователя с '
                      f'некорректным id ({user_id})')
                return

            if user.id == int(BOT_ID):
                await ctx.channel.send(
                    f'<@{BOT_ID}> пока не научился создавать свои квизы'
                )
                print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> '
                      f'попытался получить список квизов от quizcord')
            else:
                await get_quizzes_by_user(ctx, 'квизы', author=user)
                print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> получает '
                      f'список квизов от {user.nick} <{user.id}>')


@client.command(name='создать')
async def create_quiz(ctx: Context):
    if ctx.author.id in STATE_MACHINE:
        await ctx.send('Нельзя использовать команду в этом состоянии')
        print(f'[WARNING] {ctx.author.name} <{ctx.author.id}> '
              f'попытался создать квиз, находясь в состоянии')
        return

    try:
        await ctx.author.send('Создаю новый квиз...')
        await ctx.author.send(
            '*Учтите, что пустой квиз может быть удалён при проверке '
            'модератором!*'
        )

        if ctx.guild:
            await ctx.message.add_reaction('📨')

            quiz_id = add_quiz(ctx.author.id, ctx.guild.id)

            view_quiz = embeds.ViewQuiz(quiz_id, ctx.guild.name, ctx.author.id)
            await ctx.author.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )
            print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> '
                  f'создаёт квиз с сервера')

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
            print(f'[PERSONAL] {ctx.author.name} <{ctx.author.id}> '
                  f'создаёт квиз, имея один общий сервер')

        else:
            STATE_MACHINE[ctx.author.id] = QuizcordStateMachine(
                initial='quiz_set_server'
            )

            STATE_MACHINE[ctx.author.id].servers = ctx.author.mutual_guilds

            servers_names = [
                server.name for server in ctx.author.mutual_guilds
            ]

            await ctx.author.send(embed=embeds.ChooseServer(servers_names))
            print(f'[PERSONAL] {ctx.author.name} <{ctx.author.id}> '
                  f'выбирает сервер для квиза')

    except errors.Forbidden:
        await ctx.channel.send(
            'Чтобы создать квиз, откройте доступ к личным сообщениям'
        )
        print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> '
              f'попытался создать квиз с закрытыми личными сообщениями')


@client.command(name='мои')
async def get_quizzes_by_user(ctx: Context, ctx2, author=None):
    if not author:
        author_id = ctx.author.id
        author_name = ctx.author.name
    else:
        author_id = author.id
        author_name = author.name

    if ctx2 == 'квизы':
        if ctx.guild:
            await ctx.channel.send(
                embed=await embeds.embed_user_quizzes(
                    author_id,
                    author_name,
                    ctx.guild.id
                )
            )
            print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> '
                  f'получает список своих квизов')
        else:
            await ctx.author.send(
                embed=await embeds.embed_user_quizzes(
                    author_id,
                    author_name,
                    client=client
                )
            )
            print(f'[PERSONAL] {ctx.author.name} <{ctx.author.id}> '
                  f'получает список своих квизов')


@client.command(name='квиз')
async def get_quiz_by_id(ctx: Context, *quiz_id):
    if not quiz_id:
        msg = 'Отсутствует номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING {"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался получить квиз без id')

    elif not quiz_id[0].isdigit() or len(quiz_id) > 1:
        msg = 'Введён некорректный номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING {"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался получить квиз с некорректным id '
              f'({quiz_id})')

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
            print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> '
                  f'получает квиз #{quiz_id}')
        else:
            await ctx.channel.send('Нет доступа к квизу')
            print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> '
                  f'попытался получить квиз #{quiz_id}, но в доступе отказано')

    else:
        quiz_id = int(quiz_id[0])
        quizzes_list = get_user_quizzes(ctx.author.id)
        quizzes_id = [quiz.id for quiz in quizzes_list]
        quizzes_server_id = [quiz.server_id for quiz in quizzes_list]

        if quiz_id in quizzes_id:
            server = client.get_guild(
                quizzes_server_id[quizzes_id.index(quiz_id)]
            )

            view_quiz = embeds.ViewQuiz(quiz_id, server.name, ctx.author.id)
            await ctx.author.send(
                embed=view_quiz,
                components=view_quiz.keyboard
            )
            print(f'[PERSONAL] {ctx.author.name} <{ctx.author.id}> '
                  f'получает квиз #{quiz_id}')
        else:
            await ctx.author.send('Нет доступа к квизу')
            print(f'[WARNING P] {ctx.author.name} <{ctx.author.id}> '
                  f'попытался получить квиз #{quiz_id}, но в доступе отказано')


@client.command(name='рейтинг')
async def get_quiz_rating(ctx: Context, *quiz_id):
    if not quiz_id:
        msg = 'Отсутствует номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
            print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> '
                  f'попытался получить рейтинг квиза без id')

    elif not quiz_id[0].isdigit() or len(quiz_id) > 1:
        msg = 'Введён некорректный номер квиза'
        if ctx.guild:
            await ctx.channel.send(msg)
            print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> попытался '
                  f'получить рейтинг квиза с некорректным id ({quiz_id})')

    elif ctx.guild:
        quiz_id = int(quiz_id[0])
        server_quizzes = get_server_quizzes(ctx.guild.id)
        quizzes_id = [quiz.id for quiz in server_quizzes]

        if quiz_id in quizzes_id:
            await ctx.channel.send(
                embed=embeds.QuizRating(quiz_id)
            )
            print(f'[SERVER] {ctx.author.name} <{ctx.author.id}> '
                  f'получает рейтинг квиза #{quiz_id}')
        else:
            await ctx.channel.send('Нет доступа к квизу')
            print(f'[WARNING S] {ctx.author.name} <{ctx.author.id}> попытался '
                  f'получить рейтинг квиз #{quiz_id}, но в доступе отказано')


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
                        'Пожалуйста, выберите сервер повторно'
                    )

                    servers_names = [
                        server.name for server in message.author.mutual_guilds
                    ]

                    await message.author.send(
                        embed=embeds.ChooseServer(servers_names)
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался выбрать сервер, '
                          f'но список серверов был изменён')

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
                        print(f'[PERSONAL] {message.author.name} '
                              f'<{message.author.id}> выбирает сервер '
                              f'({server.name} <{server.id}>)')

                        del STATE_MACHINE[message.author.id]

                    else:
                        await message.author.send(
                            'Нет сервера с таким номером. '
                            'Пожалуйста, выберите сервер повторно'
                        )
                        print(f'[WARNING P] {message.author.name} '
                              f'<{message.author.id}> попытался выбрать '
                              f'несуществующий сервер из списка')

                else:
                    await message.author.send(
                        'Некорректный ввод. '
                        'Пожалуйста, выберите сервер повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался выбрать '
                          f'сервер некорректным вводом')

            case 'quiz_set_title':
                if len(message.content) > 200:
                    await message.author.send(
                        'Название не должно превышать 200 символов. '
                        'Пожалуйста, введите его повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести слишком '
                          f'длинное название квиза')

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
                    print(f'[PERSONAL] {message.author.name} '
                          f'<{message.author.id}> изменяет название квиза '
                          f'#{quiz_id} ({message.content})')

            case 'quiz_set_description':
                if len(message.content) > 2000:
                    await message.author.send(
                        'Описание не должно превышать 2000 символов. '
                        'Пожалуйста, введите его повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести слишком '
                          f'длинное описание квиза')

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
                    print(f'[PERSONAL] {message.author.name} '
                          f'<{message.author.id}> изменяет описание квиза '
                          f'#{quiz_id} ({message.content})')

            case 'question_set_text':
                if len(message.content) > 200:
                    await message.author.send(
                        'Текст вопроса не должен превышать 200 символов. '
                        'Пожалуйста, введите его повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести слишком '
                          f'длинный текст вопроса')

                else:
                    STATE_MACHINE[message.author.id].question_text_changed()

                    question_id = STATE_MACHINE[message.author.id].question_id
                    number = STATE_MACHINE[message.author.id].question_number
                    quantity = \
                        STATE_MACHINE[message.author.id].question_quantity

                    update_question(question_id, text=message.content)

                    embed = embeds.ChangeQuestion(
                        question_id,
                        number,
                        quantity
                    )

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
                    print(f'[PERSONAL] {message.author.name} '
                          f'<{message.author.id}> изменяет текст вопроса '
                          f'#{question_id} ({message.content})')

            case 'question_set_explanation':
                if len(message.content) > 1000:
                    await message.author.send(
                        'Пояснение не должно превышать 1000 символов. '
                        'Пожалуйста, введите его повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести слишком '
                          f'длинное пояснение вопроса')

                else:
                    STATE_MACHINE[
                        message.author.id
                    ].question_explanation_changed()

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

                    embed = embeds.ChangeQuestion(
                        question_id,
                        number,
                        quantity
                    )

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
                    print(f'[PERSONAL] {message.author.name} '
                          f'<{message.author.id}> изменяет описание вопроса '
                          f'#{question_id} ({message.content})')

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
                    elif message.content == '_':
                        update_question(
                            question_id,
                            media='_'
                        )
                    else:
                        update_question(
                            question_id,
                            media=message.attachments[0].proxy_url
                        )

                    STATE_MACHINE[message.author.id].question_media_changed()

                    embed = embeds.ChangeQuestion(
                        question_id,
                        number,
                        quantity
                    )

                    msg_media = await message.author.send('ᅠ')
                    STATE_MACHINE[message.author.id].msg_media = msg_media
                    if embed.media:
                        await msg_media.edit(embed.media)

                    await message.author.send(
                        embed=embed,
                        components=embed.keyboard
                    )
                    print(f'[PERSONAL] {message.author.name} '
                          f'<{message.author.id}> изменяет медиа вопроса '
                          f'#{question_id} ({message.content})')

                except IndexError:
                    await message.author.send(
                        'Некорректный ввод. '
                        'Пожалуйста, отправьте файл повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался изменить медиа '
                          f'вопроса некорректным вводом')

            case 'question_set_answers':
                if message.content == '_':
                    answers = '_'
                else:
                    answers = message.content.split('\n')

                if len(message.content) > 1000:
                    await message.author.send(
                        'Общий текст вариантов ответа не должен превышать '
                        '1000 символов. Пожалуйста, введите его повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести слишком '
                          f'длинные варианты ответа')
                    return

                if len(answers) > 5 and answers != '_':
                    await message.author.send(
                        'Вариантов ответа не может быть больше 5. '
                        'Пожалуйста, введите их повторно'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести больше 5 '
                          f'вариантов ответа на вопрос')
                    return

                right_answer_count = 0
                right_answer = None

                for i, answer in enumerate(answers):
                    if answer.startswith('+'):
                        right_answer = i
                        right_answer_count += 1
                        answers[i] = answer[1:]

                        if not answer[1:]:
                            await message.author.send(
                                'Вариант ответа не может быть пустым. '
                                'Пожалуйста, повторите ввод'
                            )
                            print(f'[WARNING P] {message.author.name} '
                                  f'<{message.author.id}> попытался ввести '
                                  f'пустой вариант ответа')
                            return

                if right_answer_count == 0 and answers != '_':
                    await message.author.send(
                        'Верный вариант ответа не указан. '
                        'Пожалуйста, повторите ввод'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести ввести '
                          f'варианты ответа, не указав верный')
                    return

                if right_answer_count > 1 and answers != '_':
                    await message.author.send(
                        'Указано несколько верных вариантов. '
                        'Пожалуйста, повторите ввод'
                    )
                    print(f'[WARNING P] {message.author.name} '
                          f'<{message.author.id}> попытался ввести ввести '
                          f'варианты ответа, указав несколько верных')
                    return

                question_id = STATE_MACHINE[message.author.id].question_id
                number = STATE_MACHINE[message.author.id].question_number
                quantity = STATE_MACHINE[message.author.id].question_quantity

                update_question(
                    question_id,
                    answers=answers,
                    right_answer=right_answer
                )

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
                print(f'[PERSONAL] {message.author.name} '
                      f'<{message.author.id}> изменяет варианты ответа для '
                      f'вопроса #{question_id}\n({message.content})')


# ADMIN COMMANDS
@client.command(name='очистить')
async def del_empty_quizzes(ctx: Context, ctx2=None):
    if not ctx2:
        msg = 'Уточните, очистку каких компонентов необходимо выполнить'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING A{"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался выполнить очистку, не указав '
              f'компоненты')
        return

    if ctx.author.id not in DEVELOPERS_ID:
        msg = 'Эта команда доступна только разработчикам'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING A{"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался выполнить очистку, но в доступе '
              f'было отказано')
        return

    match ctx2:
        case 'квизы':
            delete_empty_quizzes()
            await ctx.message.add_reaction('✅')
            print(f'[ADMIN] {ctx.author.name} <{ctx.author.id}> '
                  f'выполняет очистку квизов')


@client.command(name='отмена')
async def cancel(ctx: Context):
    if ctx.author.id not in DEVELOPERS_ID:
        msg = 'Эта команда доступна только разработчикам'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING A{"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался отменить команды, но в доступе '
              f'было отказано')
        return

    if ctx.author.id in STATE_MACHINE:
        del STATE_MACHINE[ctx.author.id]
        await ctx.message.add_reaction('✅')
        print(f'[ADMIN] {ctx.author.name} <{ctx.author.id}> отменяет команды')
    else:
        await ctx.message.add_reaction('❌')
        print(f'[WARNING A] {ctx.author.name} <{ctx.author.id}> попытался '
              f'отменить команды, но текущих команд не найдено')


@client.command(name='состояния')
async def get_users_states(ctx: Context):
    if ctx.author.id not in DEVELOPERS_ID:
        msg = 'Эта команда доступна только разработчикам'
        if ctx.guild:
            await ctx.channel.send(msg)
        else:
            await ctx.author.send(msg)
        print(f'[WARNING A{"S" if ctx.guild else "P"}] {ctx.author.name} '
              f'<{ctx.author.id}> попытался отменить команды, но в доступе '
              f'было отказано')
        return

    response = []

    if not STATE_MACHINE:
        response.append('Машина состояний пуста')

    else:
        for user_id, state in STATE_MACHINE.items():
            user = client.get_user(user_id)
            response.append(f'```{user.name}\t{user.id}\t{state.state}```')

    if ctx.guild:
        await ctx.channel.send('\n'.join(response))
    else:
        await ctx.author.send('\n'.join(response))
    print(f'[ADMIN] {ctx.author.name} <{ctx.author.id}> получает состояния '
          f'пользователей')
