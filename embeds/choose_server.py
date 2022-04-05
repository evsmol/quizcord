from discord import Embed

from core.colors import QuizcordColor
from core.config import BOT_ID


class ChooseServer(Embed):
    def __init__(self, servers_names, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        server_list = '\n'.join(
            f'`[{i + 1}]` {server_name}'
            for i, server_name in enumerate(servers_names))

        self.title = 'Доступные серверы'
        self.description = server_list
        if server_list:
            self.add_field(
                name='ᅠ',
                value='Для выбора сервера используйте команду '
                      '`-сервер #`, где `#` — номер сервера `[#]` '
                      'из списка выше'
            )
