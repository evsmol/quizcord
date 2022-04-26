from discord import Embed

from core.colors import QuizcordColor
from core.strings import NULL_QUIZ_TITLE
from core.helpers import get_guild_cached
from data.quiz_func import get_user_quizzes


async def embed_user_quizzes(user_id, user_name, server_id=None, client=None):
    embed = Embed()
    embed.colour = QuizcordColor

    user_quizzes = get_user_quizzes(user_id, server_id)

    quizzes_list = []

    for quiz in user_quizzes:
        guild = None

        if quiz.server_id and not server_id:
            guild = await get_guild_cached(quiz.server_id, client)

        if quiz.publication is False and not guild:
            continue

        default_title = quiz.title if quiz.title else NULL_QUIZ_TITLE

        quizzes_list.append(
            f'`[{quiz.id}]` '
            f'{f"**{default_title}**" if guild else default_title}'
            f'{f" для {guild.name}" if guild else ""}'
            f'{" *(не опубликован)*" if quiz.publication is False else ""}'
        )

    embed.title = f'Квизы от {user_name}'

    embed.description = '\n'.join(quizzes_list) if quizzes_list \
        else 'Нет созданных квизов'

    return embed
