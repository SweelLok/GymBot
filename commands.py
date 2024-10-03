from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

PLAN_COMMAND = Command("plan")
POWER_COMMAND = Command("show_power")
CHANGE_POWER = Command("change_power")

START_BOT_COMMAND = BotCommand(command="start", description="Start")
SHOW_PLAN_COMMAND = BotCommand(command="plan", description="Training plan")
SHOW_POWER_COMMAND = BotCommand(command="show_power", description="Show ur powers stat")
CHANGE_POWER_COMMAND = BotCommand(command="change_power", description="Change ur powers stat")
