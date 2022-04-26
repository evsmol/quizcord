from discord import Embed
from discord_components import Button

from core.colors import QuizcordColor

# keyboard = [[
#     Button(label='Серверные квизы', custom_id='get_server_quizzes'),
#     Button(label='Создать квиз', custom_id='add_quiz', disabled=True)
# ]]


class Help(Embed):
    def __init__(self, guild, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        self.title = 'Справка по quizcord'

        if guild:
            self.description = '-создать*\n' \
                               '-квизы\n' \
                               '-мои квизы*\n' \
                               '-квиз id*'

        else:
            self.description = '-создать*\n' \
                               '-мои квизы*\n' \
                               '-квиз id*'
