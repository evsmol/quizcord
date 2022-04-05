from discord import Embed
from discord_components import Interaction, Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE, NULL_QUESTION_TEXT
from data.quiz_func import get_quiz, get_quiz_questions

keyboard_no_published = [
    [
        Button(label='Название', custom_id='change_title'),
        Button(label='Описание', custom_id='change_description'),
        Button(label='Вопросы', custom_id='change_questions')
    ],
    [
        Button(label='Опубликовать', style=ButtonStyle.green,
               custom_id='published_quiz'),
        Button(label='Удалить', style=ButtonStyle.red, custom_id='del_quiz')
    ]
]
keyboard_published = [
    [
        Button(label='Снять с публикации', style=ButtonStyle.blue,
               custom_id='unpublished_quiz'),
        Button(label='Удалить', style=ButtonStyle.red, custom_id='del_quiz')
    ]
]


class ChangeQuiz(Embed):
    def __init__(self, quiz_id, server_name, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        quiz = get_quiz(quiz_id)
        questions = get_quiz_questions(quiz_id)
        questions_list = '\n'.join(
            f'{i + 1}) '
            f'{question.text if question.text else NULL_QUESTION_TEXT}'
            for i, question in enumerate(questions))
        self.title = quiz.title if quiz.title else NULL_QUIZ_TITLE
        self.description = quiz.description
        self.add_field(name='Автор', value=f'<@{quiz.author_id}>')
        self.add_field(name='Сервер', value=f'{server_name}')
        self.add_field(
            name='Вопросы',
            value=questions_list if questions_list
            else 'Нет созданных вопросов',
            inline=False
        )
