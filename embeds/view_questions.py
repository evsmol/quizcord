from discord import Embed
from discord_components import Interaction, Button

from core.colors import QuizcordColor
from core.strings import NULL_QUESTION_TEXT, NULL_QUESTION_ANSWERS
from data.question_func import get_question


class ViewQuestions(Embed):
    def __init__(self, question_id, number, quantity, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        question = get_question(question_id)

        self.media = question.media

        self.title = question.text if question.text else NULL_QUESTION_TEXT
        self.add_field(
            name='Варианты ответов',
            value='\n'.join(
                [f'{i + 1}) {q if i != question.right_answer else f"__{q}__"}'
                 for i, q in enumerate(question.answers)]
            ) if question.answers else NULL_QUESTION_ANSWERS, inline=False
        )

        if question.explanation:
            self.add_field(name='Пояснение',
                           value=f'> *{question.explanation}*')

        self.keyboard = [
            [
                Button(label='⟸',
                       custom_id=f'questions_left:{number}'),
                Button(label=f'{number}/{quantity}',
                       custom_id='none:none'),
                Button(label='⟹',
                       custom_id=f'questions_right:{number}')
            ],
            [
                Button(label='Редактировать',
                       custom_id=f'question_edit:{question_id},{number},'
                                 f'{quantity}'),
                Button(label=f'Добавить',
                       custom_id=f'add_question:{quantity}')
            ],
            [
                Button(label='Назад',
                       custom_id='questions_return:none')
            ]
        ]
