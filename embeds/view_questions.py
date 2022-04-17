from discord import Embed
from discord_components import Interaction, Button, ButtonStyle

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
        self.add_field(name='Варианты ответов',
                       value='\n'.join([f'{i + 1}) {q}' for i, q in
                                        enumerate(question.answers)])
                       if question.answers
                       else NULL_QUESTION_ANSWERS, inline=False)

        if question.explanation:
            self.add_field(name='Пояснение',
                           value=f'> *{question.explanation}*')

        self.keyboard = [
            [
                Button(label='⇐', style=ButtonStyle.gray,
                       custom_id='none1:none'),
                Button(label=f'{number}/{quantity}',
                       style=ButtonStyle.gray,
                       custom_id='none2:none'),
                Button(label='⇒', style=ButtonStyle.gray,
                       custom_id='none3:none')
            ],
            [
                Button(label='Редактировать', style=ButtonStyle.gray,
                       custom_id='none4:none'),
                Button(label=f'Создать новый', style=ButtonStyle.gray,
                       custom_id='none5:none'),
                Button(label='Назад', style=ButtonStyle.gray,
                       custom_id='none6:none')
            ],
        ]
