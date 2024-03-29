from discord import Embed
from discord_components_mirror import Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE
from data.quiz_func import get_quiz


class ViewQuiz(Embed):
    def __init__(self, quiz_id, server_name, message_author_id,
                 is_server=False, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        quiz = get_quiz(quiz_id)

        self.title = quiz.title if quiz.title else NULL_QUIZ_TITLE

        self.description = quiz.description

        self.add_field(name='Автор', value=f'<@{quiz.author_id}>')

        self.add_field(name='Сервер', value=f'{server_name}')

        if message_author_id != quiz.author_id or is_server:
            self.keyboard = [
                [
                    Button(
                        label='Пройти',
                        style=ButtonStyle.green,
                        custom_id=f'quiz_play:{quiz_id}'
                    ),
                ]
            ]

        elif quiz.publication:
            self.keyboard = [
                [
                    Button(
                        label='Пройти',
                        style=ButtonStyle.green,
                        custom_id=f'quiz_play:{quiz_id}'
                    ),
                    Button(
                        label='Редактировать',
                        style=ButtonStyle.gray,
                        custom_id=f'quiz_edit:{quiz_id},{server_name}'
                    )
                ]
            ]

        else:
            self.keyboard = [
                [
                    Button(
                        label='Редактировать',
                        style=ButtonStyle.gray,
                        custom_id=f'quiz_edit:{quiz_id},{server_name}'
                    )
                ]
            ]
