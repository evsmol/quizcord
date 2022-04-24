from discord import Embed

from core.colors import QuizcordColor
from data.quiz_func import get_quiz


class QuizRating(Embed):
    def __init__(self, quiz_id, **kwargs):
        super().__init__(**kwargs)
        self.colour = QuizcordColor

        quiz = get_quiz(quiz_id)

        players = list(quiz.players.items())
        players.sort(key=lambda x: x[1], reverse=True)

        quantity = len(quiz.questions)

        rating_list = '\n'.join(
            f'{i + 1}) <@{player[0]}> {player[1]}/{quantity}'
            for i, player in enumerate(players)
        )
        self.title = f'Рейтинг квиза «{quiz.title}»'
        self.description = rating_list if rating_list \
            else 'Никто ещё не прошёл этот квиз'
