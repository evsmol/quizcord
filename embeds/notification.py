from discord import Embed
from discord_components import Interaction

from core.colors import QuizcordColor


class Notification(Embed):
    def __init__(self, message, message2=None, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        self.title = message
        if message2:
            self.description = message2
