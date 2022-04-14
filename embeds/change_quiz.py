from discord import Embed
from discord_components import Interaction, Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE
from data.quiz_func import get_quiz


class ChangeQuiz(Embed):
    def __init__(self, quiz_id, server_name, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        quiz = get_quiz(quiz_id)

        self.title = quiz.title if quiz.title else NULL_QUIZ_TITLE
        self.description = quiz.description
        self.add_field(name='Автор', value=f'<@{quiz.author_id}>')
        self.add_field(name='Сервер', value=f'{server_name}')

        if quiz.publication:
            self.keyboard = [
                [
                    Button(label='Снять с публикации', style=ButtonStyle.blue,
                           custom_id=f'unpublished_quiz:{quiz_id},'
                                     f'{server_name}'),
                    Button(label='Удалить', style=ButtonStyle.red,
                           custom_id=f'del_quiz:{quiz_id},{server_name}'),
                    Button(label='Назад', style=ButtonStyle.gray,
                           custom_id=f'return_change_quiz:{quiz_id},'
                                     f'{server_name}')
                ]
            ]
        else:
            self.keyboard = [
                [
                    Button(label='Название',
                           custom_id=f'change_title:{quiz_id},{server_name}'),
                    Button(label='Описание',
                           custom_id=f'change_description:{quiz_id},'
                                     f'{server_name}'),
                    Button(label='Вопросы',
                           custom_id=f'change_questions:{quiz_id},'
                                     f'{server_name}')
                ],
                [
                    Button(
                        label='Опубликовать', style=ButtonStyle.green,
                        custom_id=f'published_quiz:{quiz_id},{server_name}'),
                    Button(label='Удалить', style=ButtonStyle.red,
                           custom_id=f'del_quiz:{quiz_id},{server_name}'),
                    Button(label='Назад', style=ButtonStyle.gray,
                           custom_id=f'return_change_quiz:{quiz_id},'
                                     f'{server_name}')
                ]
            ]
