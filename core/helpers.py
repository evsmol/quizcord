from discord_components import Interaction

import embeds
from core.colors import WarningColor
from core.config import BOT_ID
from core.state_machine import STATE_MACHINE


async def get_guild_cached(guild_id, client):
    if client.get_guild(guild_id) is None:
        return await client.fetch_guild(guild_id)
    else:
        return client.get_guild(guild_id)


async def check_restart(interaction: Interaction):
    if interaction.author.id not in STATE_MACHINE:
        try:
            await interaction.message.edit(
                embed=embeds.Notification(
                    'quizcord был перезапущен',
                    'После перезапуска бота информация о состояниях '
                    'пользователей была потеряна, внесённая же информация '
                    'сохранена.\n'
                    'Для продолжения редактирования или прохождения квиза '
                    'будет необходимо войти в состояние ещё раз.\n'
                    'Приносим извинения за доставленные неудобства, мы '
                    f'активно работаем над совершенствованием <@{BOT_ID}>',
                    color=WarningColor
                ),
                components=[]
            )
            print(f'[WARNING P] {interaction.author.name} '
                  f'<{interaction.author.id}> попытался нажать на кнопку, '
                  f'но был удалён из машины состояний после перезапуска бота')
            return True
        except AttributeError:
            await interaction.author.send(
                'Хм... Что-то пошло не так. '
                'Отправьте любое сообщение и повторите попытку'
            )
            print(f'[ERROR P] {interaction.author.name} '
                  f'<{interaction.author.id}> попытался нажать на кнопку, '
                  f'но после перезапуска бота что-то пошло не так')
            return True
    return False
