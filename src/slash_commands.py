import discord
import logging

from discord import app_commands

username = ""

# Function to create a command callback function for commands
def create_command_callback(command, default_message):
    if command == "awgtomm2":
        async def command_callback(interaction: discord.Interaction, gauge: int):
            log_command(command, interaction.user.name, gauge)
            message = awgtomm2_command(default_message, gauge)
            await interaction.response.send_message(message)
    else:
        async def command_callback(interaction: discord.Interaction):
            log_command(command, interaction.user.name)
            await interaction.response.send_message(default_message)

    return command_callback

async def register_commands(client, commands, guild_id):
    tree = app_commands.CommandTree(client)
    
    # Create and register a command for each item in the commands dictionary
    for name, details in commands.items():

        command_callback = create_command_callback(name, details["message"])
        new_command = app_commands.Command(
            name=name,
            description=details["description"],
            callback=command_callback
        )

        # Attach the command to a specific guild using guild_id
        tree.add_command(new_command, guild=discord.Object(id=guild_id))

    await tree.sync(guild=discord.Object(guild_id))

def awgtomm2_command(message, gauge):
    return message.format(gauge, awgtomm2(gauge))

def awgtomm2(gauge):
    diameter = round(0.127 * 92 ** ((36 - gauge) / 39), 2)
    return round(3.14 / 4 * diameter ** 2, 2)

def log_command(command, username, *args):
    parameters = ', '.join(str(arg) for arg in args)
    if args:
        logging.info('{} called the {} command with parameter(s): {}'.format(username, command, parameters))
    else:
        logging.info('{} called the {} command'.format(username, command))