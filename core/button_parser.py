from discord_components import Interaction

import embeds


async def button_parser(interaction: Interaction):
    await interaction.respond(type=6)
    match interaction.custom_id:
        case 'get_server_quizzes':
            await interaction.message.channel.send(embed=embeds.ServerQuizzes(
                interaction.message.guild.id))
        case 'add_quiz':
            pass
