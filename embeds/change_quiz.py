from discord import Embed
from discord_components import Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE, NULL_QUESTION_TEXT
from core.helpers import get_guild_cached
from data.quiz_func import get_quiz, get_quiz_questions
from data.question_func import add_question


async def embed_change_quiz(quiz_id, client):
    embed = Embed()
    embed.colour = QuizcordColor

    quiz = get_quiz(quiz_id)
    server = await get_guild_cached(quiz.server_id, client)

    embed.title = quiz.title if quiz.title else NULL_QUIZ_TITLE

    embed.description = quiz.description

    embed.add_field(name='Автор', value=f'<@{quiz.author_id}>')
    embed.add_field(name='Сервер', value=f'{server.name}')

    questions = get_quiz_questions(quiz_id)

    questions_list = '\n'.join(
        f'{i + 1}) {question.text if question.text else NULL_QUESTION_TEXT}'
        for i, question in enumerate(questions)
    )

    embed.add_field(
        name='Вопросы',
        value=questions_list if questions_list else 'Нет созданных вопросов',
        inline=False
    )

    if quiz.publication:
        keyboard = [
            [
                Button(
                    label='Снять с публикации',
                    style=ButtonStyle.blue,
                    custom_id=f'unpublished_quiz:{quiz_id},{server.name}'
                ),

                Button(
                    label='Удалить',
                    style=ButtonStyle.red,
                    custom_id=f'del_quiz:{quiz_id},{server.name}'
                ),

                Button(
                    label='Назад',
                    style=ButtonStyle.gray,
                    custom_id=f'return_change_quiz:{quiz_id},{server.name}'
                )
            ]
        ]

    else:
        number = 1
        if not quiz.questions:
            question_id = -1
            quantity = 1
        else:
            question_id = quiz.questions[0]
            quantity = len(quiz.questions)

        keyboard = [
            [
                Button(
                    label='Название',
                    custom_id=f'change_title:{quiz_id},{server.name}'
                ),
                Button(
                    label='Описание',
                    custom_id=f'change_description:{quiz_id},{server.name}'
                ),
                Button(
                    label='Вопросы',
                    custom_id=f'change_questions:{question_id},{number},'
                              f'{quantity}'
                )
            ],
            [
                Button(
                    label='Опубликовать',
                    style=ButtonStyle.green,
                    custom_id=f'published_quiz:{quiz_id},{server.name}'
                ),
                Button(
                    label='Удалить',
                    style=ButtonStyle.red,
                    custom_id=f'del_quiz:{quiz_id},{server.name}'
                ),
                Button(
                    label='Назад',
                    style=ButtonStyle.gray,
                    custom_id=f'return_change_quiz:{quiz_id},{server.name}'
                )
            ]
        ]

    return embed, keyboard
