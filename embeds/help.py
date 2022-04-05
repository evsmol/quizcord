from discord import Embed
from discord_components import Interaction, Button

from core.colors import QuizcordColor

keyboard = [[
    Button(label='Серверные квизы', custom_id='get_server_quizzes'),
    Button(label='Создать квиз', custom_id='add_quiz', disabled=True)
]]


class Help(Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = f'Справка по quizcord'
        self.description = '-создать*\n' \
                           '-квизы\n' \
                           '-мои квизы*'
        self.colour = QuizcordColor
