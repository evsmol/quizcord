from discord_components_mirror import Interaction

import embeds
from core.strings import NULL_QUIZ_TITLE
from core.state_machine import QuizcordStateMachine, STATE_MACHINE
from core.helpers import check_restart
from data.quiz_func import update_quiz, del_quiz, get_quiz, \
    check_quiz_for_publication
from data.question_func import add_question, del_question, get_question


async def button_parser(interaction: Interaction, client):
    await interaction.respond(type=6)

    command, parameters = interaction.custom_id.split(':')

    match command:

        case 'quiz_edit':
            if interaction.author.id in STATE_MACHINE:
                await interaction.author.send(
                    'Нельзя начать редактировать квиз в этом состоянии'
                )
                print(f'[WARNING] {interaction.author.name} '
                      f'<{interaction.author.id}> попытался редактировать '
                      f'квиз, находясь в состоянии')
                return

            quiz_id, server_name = parameters.split(',')

            embed, keyboard = await embeds.embed_change_quiz(
                quiz_id,
                client
            )
            await interaction.message.edit(
                embed=embed,
                components=keyboard
            )

            STATE_MACHINE[interaction.author.id] = QuizcordStateMachine(
                initial='quiz_edit'
            )
            STATE_MACHINE[interaction.author.id].quiz_id = int(quiz_id)

        case 'published_quiz':
            if await check_restart(interaction, client):
                return

            quiz_id, server_name = parameters.split(',')

            if not check_quiz_for_publication(int(quiz_id)):
                await interaction.author.send(
                    'Нельзя опубликовать квиз. Добавьте варианты ответа для '
                    'каждого вопроса'
                )
                return

            quiz = get_quiz(int(quiz_id))
            if len(quiz.questions) == 0:
                await interaction.author.send(
                    'Нельзя опубликовать пустой квиз'
                )
                return

            del STATE_MACHINE[interaction.author.id]

            update_quiz(quiz_id, publication=True)

            view_quiz = embeds.ViewQuiz(
                int(quiz_id),
                server_name,
                interaction.author.id
            )
            await interaction.message.edit(
                embed=view_quiz,
                components=view_quiz.keyboard
            )

        case 'unpublished_quiz':
            if await check_restart(interaction, client):
                return

            quiz_id, server_name = parameters.split(',')

            update_quiz(quiz_id, publication=False, players=[])

            embed, keyboard = await embeds.embed_change_quiz(
                int(quiz_id),
                client
            )
            await interaction.message.edit(
                embed=embed,
                components=keyboard
            )
        case 'del_quiz':
            if await check_restart(interaction, client):
                return

            del STATE_MACHINE[interaction.author.id]

            quiz_id, server_name = parameters.split(',')

            del_quiz(quiz_id)

            message = 'Квиз удалён'
            message2 = 'Чтобы создать новый квиз, воспользуйтесь командой ' \
                       '`-создать`'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'return_change_quiz':
            if await check_restart(interaction, client):
                return

            del STATE_MACHINE[interaction.author.id]

            quiz_id, server_name = parameters.split(',')

            view_quiz = embeds.ViewQuiz(
                int(quiz_id),
                server_name,
                interaction.author.id
            )
            await interaction.message.edit(
                embed=view_quiz,
                components=view_quiz.keyboard
            )

        case 'change_title':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_quiz_title()

            quiz_id, server_name = parameters.split(',')
            STATE_MACHINE[interaction.author.id].quiz_id = int(quiz_id)

            message = 'Изменение названия'
            message2 = 'Отправьте новое название для квиза.\n' \
                       'Чтобы вернуться назад, отправьте подчёркивание'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'change_description':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_quiz_description()

            quiz_id, server_name = parameters.split(',')
            STATE_MACHINE[interaction.author.id].quiz_id = int(quiz_id)

            message = 'Изменение описания'
            message2 = 'Отправьте новое описание для квиза.\n' \
                       'Чтобы удалить описание, отправьте точку.\n' \
                       'Чтобы вернуться назад, отправьте подчёркивание'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'change_questions':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].select_question()

            question_id, number, quantity = map(int, parameters.split(','))

            if question_id < 0:
                quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
                question_id = add_question(quiz_id)

            await interaction.message.delete()

            msg_media = await interaction.author.send(
                'Открываю редактор вопросов...'
            )
            STATE_MACHINE[interaction.author.id].msg_media = msg_media

            embed = embeds.ViewQuestions(question_id, number, quantity)

            await interaction.author.send(
                embed=embed,
                components=embed.keyboard
            )

            if embed.media:
                await msg_media.edit(embed.media)
            else:
                await msg_media.edit('ᅠ')

        case 'questions_left':
            if await check_restart(interaction, client):
                return

            number_question = int(parameters)

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            quantity = len(questions)

            if number_question > 1:
                question_id = questions[number_question - 2]
                number = number_question - 1
                embed = embeds.ViewQuestions(question_id, number, quantity)
            else:
                question_id = questions[-1]
                number = quantity
                embed = embeds.ViewQuestions(question_id, number, quantity)

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            if embed.media:
                await msg_media.edit(embed.media)
            else:
                await msg_media.edit('ᅠ')

            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'questions_right':
            if await check_restart(interaction, client):
                return

            number_question = int(parameters)

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            quantity = len(questions)

            if number_question < quantity:
                question_id = questions[number_question]
                number = number_question + 1
                embed = embeds.ViewQuestions(question_id, number, quantity)
            else:
                question_id = questions[0]
                number = 1
                embed = embeds.ViewQuestions(question_id, number, quantity)

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            if embed.media:
                await msg_media.edit(embed.media)
            else:
                await msg_media.edit('ᅠ')

            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'question_edit':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question()

            question_id, number, quantity = parameters.split(',')

            embed = embeds.ChangeQuestion(question_id, number, quantity)
            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'add_question':
            if await check_restart(interaction, client):
                return

            quantity = int(parameters)

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id

            question_id = add_question(quiz_id)

            embed = embeds.ViewQuestions(
                question_id,
                quantity + 1,
                quantity + 1
            )

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.edit('ᅠ')

            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'questions_return':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].select_question_return()
            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id

            embed, keyboard = await embeds.embed_change_quiz(
                quiz_id,
                client
            )

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            await interaction.message.edit(
                embed=embed,
                components=keyboard
            )

        case 'question_up':
            if await check_restart(interaction, client):
                return

            question_id, number, quantity = map(int, parameters.split(','))

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            if number < quantity:
                questions[number - 1], questions[number] = \
                    questions[number], questions[number - 1]
                number = number + 1
            else:
                questions[number - 1], questions[0] = \
                    questions[0], questions[number - 1]
                number = 1

            update_quiz(quiz_id, questions=questions)

            embed = embeds.ChangeQuestion(question_id, number, quantity)
            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'question_down':
            if await check_restart(interaction, client):
                return

            question_id, number, quantity = map(int, parameters.split(','))

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            if number > 1:
                questions[number - 1], questions[number - 2] = \
                    questions[number - 2], questions[number - 1]
                number = number - 1
            else:
                questions[number - 1], questions[-1] = \
                    questions[-1], questions[number - 1]
                number = quantity

            update_quiz(quiz_id, questions=questions)

            embed = embeds.ChangeQuestion(question_id, number, quantity)
            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'question_del':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_delete()

            question_id, number, quantity = map(int, parameters.split(','))

            del_question(question_id)

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            if number < quantity:
                question_id = questions[number - 1]
            else:
                question_id = questions[number - 2]
                number -= 1

            questions = embeds.ViewQuestions(question_id, number, quantity - 1)
            await interaction.message.edit(
                embed=questions,
                components=questions.keyboard
            )

        case 'question_text':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_text()

            question_id, number, quantity = map(int, parameters.split(','))
            STATE_MACHINE[interaction.author.id].question_id = question_id
            STATE_MACHINE[interaction.author.id].question_number = number
            STATE_MACHINE[interaction.author.id].question_quantity = quantity

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            message = 'Изменение текста вопроса'
            message2 = 'Отправьте новый текст для вопроса.\n' \
                       'Чтобы вернуться назад, отправьте подчёркивание'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'question_explanation':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_explanation()

            question_id, number, quantity = map(int, parameters.split(','))
            STATE_MACHINE[interaction.author.id].question_id = question_id
            STATE_MACHINE[interaction.author.id].question_number = number
            STATE_MACHINE[interaction.author.id].question_quantity = quantity

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            message = 'Изменение пояснения'
            message2 = 'Отправьте новое пояснение для вопроса.\n' \
                       'Чтобы удалить пояснение, отправьте точку.\n' \
                       'Чтобы вернуться назад, отправьте подчёркивание'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'questions_answers':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_answers()

            question_id, number, quantity = map(int, parameters.split(','))
            STATE_MACHINE[interaction.author.id].question_id = question_id
            STATE_MACHINE[interaction.author.id].question_number = number
            STATE_MACHINE[interaction.author.id].question_quantity = quantity

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            message = 'Изменение вариантов ответа'
            message2 = 'Чтобы вернуться назад, отправьте подчёркивание.\n' \
                       'Отправьте варианты ответа на вопрос в следующем ' \
                       'формате:\n' \
                       'В одной строке — один вариант ответа. Всего ' \
                       'может быть от 1 до 5 вариантов.\n ' \
                       'Для отметки верного поставьте вплотную перед ' \
                       'началом символ `+`.\n' \
                       'Для переноса строки используйте комбинацию клавиш ' \
                       '`Shift + Enter`.\n\n' \
                       '**Пример сообщения:**\n' \
                       'Да, является\n' \
                       '+Нет, не является\n' \
                       'Иногда'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'question_media':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_media()

            question_id, number, quantity = map(int, parameters.split(','))
            STATE_MACHINE[interaction.author.id].question_id = question_id
            STATE_MACHINE[interaction.author.id].question_number = number
            STATE_MACHINE[interaction.author.id].question_quantity = quantity

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            message = 'Изменение медиа'
            message2 = 'Отправьте новый медиафайл для вопроса.\n' \
                       'Чтобы удалить медиа, отправьте точку.\n' \
                       'Чтобы вернуться назад, отправьте подчёркивание.\n' \
                       '*Учтите, что аудио- и видеофайлы участник, ' \
                       'возможно, будет вынужден скачать по ссылке*'
            await interaction.message.edit(
                embed=embeds.Notification(message, message2),
                components=[]
            )

        case 'question_return':
            if await check_restart(interaction, client):
                return

            STATE_MACHINE[interaction.author.id].edit_question_return()

            question_id, number, quantity = parameters.split(',')

            questions = embeds.ViewQuestions(question_id, number, quantity)
            await interaction.message.edit(
                embed=questions,
                components=questions.keyboard
            )

        case 'quiz_play':
            quiz_id = int(parameters)

            if interaction.author.id in STATE_MACHINE:
                await interaction.author.send(
                    'Вы не можете начать проходить квиз в этом состоянии'
                )
                return

            STATE_MACHINE[interaction.author.id] = QuizcordStateMachine(
                initial='quiz_play'
            )
            STATE_MACHINE[interaction.author.id].quiz_id = quiz_id

            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            if not quiz.publication:
                del STATE_MACHINE[interaction.author.id]

                await interaction.message.edit(
                    embed=embeds.Notification(
                        'Квиз снят с публикации',
                        'Прохождение квиза недоступно, '
                        'так как автор снял его с публикации'
                    ),
                    components=[]
                )
                return

            await interaction.author.send(
                f'Открываю квиз '
                f'**{quiz.title if quiz.title else NULL_QUIZ_TITLE}** '
                f'от <@{quiz.author_id}>'
            )

            question_id = questions[0]
            number = 1
            quantity = len(questions)

            STATE_MACHINE[interaction.author.id].question_quantity = quantity

            msg_media = await interaction.author.send('ᅠ')
            STATE_MACHINE[interaction.author.id].msg_media = msg_media

            embed = embeds.GameQuestion(question_id, number, quantity)

            if embed.media:
                await msg_media.edit(embed.media)

            await interaction.author.send(
                embed=embed,
                components=embed.keyboard
            )

        case 'answer_options':
            if await check_restart(interaction, client):
                return

            question_id, number, quantity, answer = map(
                int, parameters.split(',')
            )

            question = get_question(question_id)
            right_answer = question.right_answer

            if right_answer == answer:
                STATE_MACHINE[interaction.author.id].correctly_answered += 1

            quiz_id = question.quiz_id
            quiz = get_quiz(quiz_id)

            if not quiz.publication:
                del STATE_MACHINE[interaction.author.id]

                await interaction.message.edit(
                    embed=embeds.Notification(
                        'Квиз снят с публикации',
                        'Прохождение квиза недоступно, '
                        'так как автор снял его с публикации'
                    ),
                    components=[]
                )
                return

            embed = embeds.GameQuestion(
                question_id,
                number,
                quantity,
                closed=False,
                chosen=answer
            )

            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'next_question':
            if await check_restart(interaction, client):
                return

            number, quantity = map(int, parameters.split(','))

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)
            questions = quiz.questions

            if not quiz.publication:
                del STATE_MACHINE[interaction.author.id]

                await interaction.message.edit(
                    embed=embeds.Notification(
                        'Квиз снят с публикации',
                        'Прохождение квиза недоступно, '
                        'так как автор снял его с публикации'
                    ),
                    components=[]
                )
                return

            question_id = questions[number - 1]

            embed = embeds.GameQuestion(question_id, number, quantity)

            msg_media = STATE_MACHINE[interaction.author.id].msg_media

            if embed.media:
                await msg_media.edit(embed.media)
            else:
                await msg_media.edit('ᅠ')

            await interaction.message.edit(
                embed=embed,
                components=embed.keyboard
            )

        case 'finish_game':
            if await check_restart(interaction, client):
                return

            correctly_answered = \
                STATE_MACHINE[interaction.author.id].correctly_answered

            quiz_id = STATE_MACHINE[interaction.author.id].quiz_id
            quiz = get_quiz(quiz_id)

            if not quiz.publication:
                del STATE_MACHINE[interaction.author.id]

                await interaction.message.edit(
                    embed=embeds.Notification(
                        'Квиз снят с публикации',
                        'Прохождение квиза недоступно, '
                        'так как автор снял его с публикации'
                    ),
                    components=[]
                )
                return

            quantity = len(quiz.questions)

            players = quiz.players
            player = interaction.author.id

            players[str(player)] = correctly_answered

            update_quiz(quiz_id, players=players)

            msg_media = STATE_MACHINE[interaction.author.id].msg_media
            await msg_media.delete()

            del STATE_MACHINE[interaction.author.id]

            await interaction.message.edit(
                embed=embeds.EndGame(quiz.title, correctly_answered, quantity),
                components=[]
            )
