import discord

from discord import app_commands

# Function to create a command callback function for commands
def create_command_callback(message):
    async def command_callback(interaction: discord.Interaction):
        await interaction.response.send_message(message)
    return command_callback

async def register_commands(command_tree, commands, guild_id):
    # Create and register a command for each item in the commands dictionary
    for name, details in commands.items():
        command_callback = create_command_callback(details["Message"])
        new_command = app_commands.Command(
            name=name,
            description=details["Description"],
            callback=command_callback
        )
        # Attach the command to a specific guild using guild_id
        command_tree.add_command(new_command, guild=discord.Object(id=guild_id))