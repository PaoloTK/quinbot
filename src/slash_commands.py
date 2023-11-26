import discord
import logging

from typing import Literal
from discord import app_commands
from decimal import Decimal as D

COPPER_RESISTANCE = D(1.72 * 10 ** -8)

# Function to create a command callback function for commands
def create_command_callback(command, default_message):
    if command == "awgtomm2":
        async def command_callback(interaction: discord.Interaction, gauge: int):
            log_command(command, interaction.user.name, gauge)
            message = awgtomm2_command(default_message, gauge)
            await interaction.response.send_message(message)
    if command == "dropcalc":
        async def command_callback(interaction: discord.Interaction, units: Literal["metric", "imperial"], gauge: float, length: float, volts: float, amps: float):
            """
            gauge: int
                wire section in mm² (metric) or AWG (imperial)
            length: int
                wire length in meters (metric) or feet (imperial)
            volts: int
                voltage at the start of the wire
            amps: int
                current that will travel over the wire
            """
            log_command(command, interaction.user.name, units, gauge, length, volts, amps)
            message = dropcalc_command(default_message, units, gauge, length, volts, amps)
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
    return message.format(gauge, awg_to_mm2(gauge))

def dropcalc_command(message, units, gauge, length, volts, amps):
    if units == "imperial":
        section = awg_to_mm2(gauge)
        distance = feet_to_meters(length)
        gauge = str(gauge) + " AWG"
        length = str(length) + " feet"
    else:
        section = gauge
        distance = length
        gauge = str(gauge) + " mm²"
        length = str(length) + " meters"
    resistance = 10 ** 9 * D(COPPER_RESISTANCE) / D(section)
    drop = round(D(amps) *  2 * D(distance) * D(resistance) / 1000)
    drop_percentage = D(drop) / D(volts) * 100
    volts = D(volts) - D(drop)
    return message.format(gauge, length, volts, amps, drop_percentage, volts)

def awg_to_mm2(gauge):
    diameter = round(D(0.127) * 92 ** D((36 - gauge) / 39), 2)
    return round(D(3.14) / 4 * D(diameter) ** 2, 2)

def feet_to_meters(feet):
    return round(D(feet) * D(0.3048), 2)

def log_command(command, username, *args):
    parameters = ', '.join(str(arg) for arg in args)
    if args:
        logging.info('{} called the {} command with parameter(s): {}'.format(username, command, parameters))
    else:
        logging.info('{} called the {} command'.format(username, command))