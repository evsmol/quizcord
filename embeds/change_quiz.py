from discord import Embed
from discord_components import Interaction, Button

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE, NULL_QUESTION_TEXT
from data.quiz_func import get_quiz, get_quiz_questions

keyboard = [
    [
        Button(label='Изменить название', custom_id='change_title',
               disabled=True)
    ],
    [
        Button(label='Добавить описание', custom_id='add_description',
               disabled=True),
        Button(label='Изменить описание', custom_id='change_description',
               disabled=True),
        Button(label='Удалить описание', custom_id='del_description',
               disabled=True)
    ],
    [
        Button(label='Добавить вопрос', custom_id='add_question',
               disabled=True),
        Button(label='Изменить вопрос', custom_id='change_question',
               disabled=True),
        Button(label='Удалить вопрос', custom_id='del_question',
               disabled=True)
    ]
]


class ChangeQuiz(Embed):
    def __init__(self, quiz_id, server_name, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        quiz = get_quiz(quiz_id)
        questions = get_quiz_questions(quiz_id)
        questions_list = '\n'.join(
            f'{i}) {question.text if question.text else NULL_QUESTION_TEXT}'
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
