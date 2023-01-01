from discord import Embed
from discord_components_mirror import Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUESTION_TEXT, NULL_QUESTION_ANSWERS
from data.question_func import get_question


class ChangeQuestion(Embed):
    def __init__(self, question_id, number, quantity, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        question = get_question(question_id)

        self.media = question.media

        self.title = question.text if question.text else NULL_QUESTION_TEXT

        self.add_field(
            name='Варианты ответа',
            value='\n'.join(
                [f'{i + 1}) {q if i != question.right_answer else f"__{q}__"}'
                 for i, q in enumerate(question.answers)]
            )
            if question.answers
            else NULL_QUESTION_ANSWERS,
            inline=False
        )

        if question.explanation:
            self.add_field(
                name='Пояснение',
                value=f'> *{question.explanation}*'
            )

        self.set_footer(text=f'Вопрос {number} из {quantity}')

        self.keyboard = [
            [
                Button(
                    label='⇑',
                    custom_id=f'question_up:{question_id},{number},{quantity}'
                ),
                Button(
                    label='⇓',
                    custom_id=f'question_down:{question_id},{number},'
                              f'{quantity}'
                ),
                Button(
                    label='Удалить',
                    style=ButtonStyle.red,
                    custom_id=f'question_del:{question_id},{number},'
                              f'{quantity}',
                    disabled=False if int(quantity) > 1 else True
                )
            ],
            [
                Button(
                    label='Текст вопроса',
                    custom_id=f'question_text:{question_id},{number},'
                              f'{quantity}'
                ),
                Button(
                    label='Пояснение',
                    custom_id=f'question_explanation:{question_id},{number},'
                              f'{quantity}'
                )
            ],
            [
                Button(
                    label='Варианты ответа',
                    custom_id=f'questions_answers:{question_id},{number},'
                              f'{quantity}'
                ),
                Button(
                    label='Медиа',
                    custom_id=f'question_media:{question_id},{number},'
                              f'{quantity}'
                )
            ],
            [
                Button(
                    label='Назад',
                    custom_id=f'question_return:{question_id},{number},'
                              f'{quantity}'
                )
            ]
        ]
