from discord import Embed
from discord_components import Interaction, Button

from core.colors import QuizcordColor

# keyboard = [[
#     Button(label='Серверные квизы', custom_id='get_server_quizzes'),
#     Button(label='Создать квиз', custom_id='add_quiz', disabled=True)
# ]]


class Help(Embed):
    def __init__(self, guild, **kwargs):
        super().__init__(**kwargs)
        self.title = f'Справка по quizcord'
        if guild:
            self.description = '-создать*\n' \
                               '-квизы\n' \
                               '-мои квизы*'
        else:
            self.description = '-создать*\n' \
                               '-мои квизы*'
        self.colour = QuizcordColor
