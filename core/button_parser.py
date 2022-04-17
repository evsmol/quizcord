from discord_components import Interaction

import embeds
from core.state_machine import QuizcordStateMachine, STATE_MACHINE
from data.quiz_func import update_quiz, del_quiz


async def button_parser(interaction: Interaction):
    await interaction.respond(type=6)

    command, parameters = interaction.custom_id.split(':')

    match command:
        case 'quiz_edit':
            quiz_id, server_name = parameters.split(',')
            await interaction.message.edit(
                embed=embeds.ChangeQuiz(quiz_id, server_name),
                components=embeds.ChangeQuiz(int(quiz_id),
                                             server_name).keyboard)
            STATE_MACHINE[interaction.author.id] = QuizcordStateMachine(
                initial='quiz_edit')
        case 'published_quiz':
            del STATE_MACHINE[interaction.author.id]

            quiz_id, server_name = parameters.split(',')

            update_quiz(quiz_id, publication=True)

            await interaction.message.edit(
                embed=embeds.ViewQuiz(int(quiz_id), server_name,
                                      interaction.author.id),
                components=embeds.ViewQuiz(int(quiz_id),
                                           server_name,
                                           interaction.author.id).keyboard)
        case 'unpublished_quiz':
            quiz_id, server_name = parameters.split(',')

            update_quiz(quiz_id, publication=False, players=[])

            await interaction.message.edit(
                embed=embeds.ChangeQuiz(int(quiz_id), server_name),
                components=embeds.ChangeQuiz(int(quiz_id),
                                             server_name).keyboard)
        case 'del_quiz':
            del STATE_MACHINE[interaction.author.id]

            quiz_id, server_name = parameters.split(',')

            del_quiz(quiz_id)

            message = 'Квиз удалён'
            message2 = 'Чтобы создать новый квиз, воспользуйтесь командой ' \
                       '`-создать`'
            await interaction.message.edit(embed=embeds.Notification(message,
                                                                     message2),
                                           components=[])
        case 'return_change_quiz':
            del STATE_MACHINE[interaction.author.id]

            quiz_id, server_name = parameters.split(',')

            await interaction.message.edit(
                embed=embeds.ViewQuiz(int(quiz_id), server_name,
                                      interaction.author.id),
                components=embeds.ViewQuiz(int(quiz_id),
                                           server_name,
                                           interaction.author.id).keyboard)
        case 'change_title':
            STATE_MACHINE[interaction.author.id].edit_quiz_title()

            quiz_id, server_name = parameters.split(',')
            STATE_MACHINE[interaction.author.id].quiz_id = int(quiz_id)
            STATE_MACHINE[interaction.author.id].server_name = server_name

            message = 'Изменение названия'
            message2 = 'Отправьте новое название для квиза'
            await interaction.message.edit(embed=embeds.Notification(
                message, message2), components=[])
        case 'change_description':
            STATE_MACHINE[interaction.author.id].edit_quiz_description()

            quiz_id, server_name = parameters.split(',')
            STATE_MACHINE[interaction.author.id].quiz_id = int(quiz_id)
            STATE_MACHINE[interaction.author.id].server_name = server_name

            message = 'Изменение описания'
            message2 = 'Отправьте новое описание для квиза.\n' \
                       'Чтобы удалить описание, отправьте точку'
            await interaction.message.edit(embed=embeds.Notification(
                message, message2), components=[])