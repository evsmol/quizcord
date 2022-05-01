from discord import Embed

from core.colors import QuizcordColor


class Notification(Embed):
    def __init__(self, message, message2=None, color=QuizcordColor, **kwargs):
        super().__init__(**kwargs)
        self.colour = color

        self.title = message

        if message2:
            self.description = message2
