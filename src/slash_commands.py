import discord
import logging

from discord import app_commands

# Function to create a command callback function for commands
def create_command_callback(command, default_message):
    async def command_callback(interaction: discord.Interaction):
        username = interaction.user.name
        message = execute_command_action(command, default_message, username)
        logging.info('{} command has been called by {}'.format(command, username))
        await interaction.response.send_message(message)
    return command_callback

async def register_commands(command_tree, commands, guild_id):
    # Create and register a command for each item in the commands dictionary
    for name, details in commands.items():
        command_callback = create_command_callback(name, details["Message"])
        new_command = app_commands.Command(
            name=name,
            description=details["Description"],
            callback=command_callback
        )
        # Attach the command to a specific guild using guild_id
        command_tree.add_command(new_command, guild=discord.Object(id=guild_id))

def execute_command_action(command, message, username):
    if command == "awgtomm2":
        result = awgtomm2(message)
    else:
        result = message
    return result
    
def awgtomm2(gauge):
    return 1