from discord import Embed

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE
from data.quiz_func import get_server_quizzes


class ServerQuizzes(Embed):
    def __init__(self, server_id, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        server_quizzes = get_server_quizzes(server_id)

        server_list = '\n'.join(
            f'`[{quiz.id}]` {quiz.title if quiz.title else NULL_QUIZ_TITLE} '
            f'от <@{quiz.author_id}>' for quiz in server_quizzes
        )

        self.title = 'Серверные квизы'

        self.description = server_list if server_list \
            else 'Нет доступных квизов'
