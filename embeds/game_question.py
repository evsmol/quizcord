from discord import Embed
from discord_components import Button, ButtonStyle

from core.colors import QuizcordColor
from core.strings import NULL_QUESTION_TEXT, NULL_QUESTION_ANSWERS
from data.question_func import get_question


class GameQuestion(Embed):
    def __init__(self, question_id, number, quantity, closed=True,
                 chosen=None, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        question = get_question(question_id)

        right_answer = question.right_answer

        self.media = question.media

        self.title = question.text if question.text else NULL_QUESTION_TEXT

        self.add_field(
            name='Варианты ответа',
            value='\n'.join(
                [f'{i + 1}) {q}' for i, q in enumerate(question.answers)]
            ) if question.answers else NULL_QUESTION_ANSWERS,
            inline=False
        )

        if question.explanation and not closed:
            self.add_field(
                name='ᅠ',
                value=f'> *{question.explanation}*'
            )

        self.set_footer(text=f'Вопрос {number} из {quantity}')

        if closed:
            self.keyboard = [
                [
                    Button(
                        label=f'{i + 1}',
                        custom_id=f'answer_options:{question_id},{number},'
                                  f'{quantity},{i}'
                    )
                    for i in range(len(question.answers))
                ]
            ]
        else:
            self.keyboard = [
                [
                    Button(
                        label=f'{i + 1}',
                        style=ButtonStyle.red
                        if i == chosen and chosen != right_answer
                        else ButtonStyle.green
                        if i == right_answer
                        else ButtonStyle.gray,
                        custom_id=f'answer_options:{i}',
                        disabled=True
                    )
                    for i in range(len(question.answers))
                ],
                [
                    Button(
                        label='Завершить',
                        custom_id=f'finish_game:none'
                    ),
                    Button(
                        label='Далее',
                        custom_id=f'next_question:{number + 1},{quantity}'
                    )
                ]
                if number != quantity
                else
                [
                    Button(
                        label='Завершить',
                        custom_id='finish_game:none'
                    )
                ]
            ]
