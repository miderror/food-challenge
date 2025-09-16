from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Перезапустить бота"),
        BotCommand(command="search", description="🔍 Быстрый поиск продукта"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
