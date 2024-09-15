import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp import web

from logging import config
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, ConstI18nMiddleware

from bot.config import load_config, Config
from bot.middlewares.last_activity import LastActivity
from bot.middlewares.localization import Localization
from bot.handlers.commands import start_command, exception_command, test_command, schedule_commands
from bot.handlers.others import not_authorized_handler, exceptions_handler
from bot.handlers.menu_keyboards import (authorize_menu, main_manu, schedule_menu, information_menu, settings_menu,
                                         submission_menu)


async def on_startup(bot: Bot, configs) -> None:
    logging.info("Bot started!")

    await bot.set_webhook(f"{configs.webhook_url}{configs.webhook_path}", secret_token=configs.webhook_secret)

    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Показати головне меню"),
            BotCommand(command="today", description="Отримати розклад на сьогодні"),
            BotCommand(command="tomorrow", description="Отримати розклад на завтра"),
            BotCommand(command="this_week", description="Отримати розклад на цей тиждень"),
            BotCommand(command="next_week", description="Отримати розклад на настурний тиждень"),
        ]
    )


def main() -> None:
    # Dispatcher is a root router
    configs = load_config()
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="uk", domain="default")

    # I18n Localization middleware
    dp.message.middleware(Localization(i18n=i18n))
    dp.message.outer_middleware(Localization(i18n=i18n))

    # Last Activity middleware
    dp.message.middleware(LastActivity())

    # Command handlers
    dp.include_routers(start_command.router, exception_command.router, test_command.router,
                       schedule_commands.router)

    # Menu handlers
    dp.include_routers(authorize_menu.router, main_manu.router, schedule_menu.router, information_menu.router,
                       settings_menu.router, submission_menu.router)

    # Other handlers
    dp.include_router(not_authorized_handler.router)

    # Exception handler
    dp.include_router(exceptions_handler.router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    logging.config.dictConfig(configs.logger_settings)

    bot = Bot(configs.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()

    dp["configs"] = configs

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=configs.webhook_secret,
        cache={},
        i18n=i18n,
        configs=configs
    )

    webhook_requests_handler.register(app, path=configs.webhook_path)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=configs.webserver, port=configs.port)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
