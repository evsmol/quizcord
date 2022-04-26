from discord import Embed

from core.colors import QuizcordColor


class EndGame(Embed):
    def __init__(self, quiz_name, result, quantity, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        self.title = f'Квиз «{quiz_name}» пройден!'

        self.add_field(
            name='Ваш результат',
            value=f'{result}/{quantity}'
        )
