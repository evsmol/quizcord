from discord import Embed
from discord_components_mirror import Button, ButtonStyle

from core.colors import QuizcordColor


class Help(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        self.title = 'Справка по quizcord'

        self.description = 'Подробное руководство по командам, ' \
                           'редактированию и прохождению квизов доступно ' \
                           'по ссылке в кнопке'

        self.keyboard = [
            [
                Button(
                    label='Перейти к справке',
                    style=ButtonStyle.URL,
                    url='https://gist.github.com/evsmol/'
                        '3e5d226057d809bc0243a2c482a9a4c5'
                )
            ]
        ]
