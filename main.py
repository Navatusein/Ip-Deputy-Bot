import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config import Config, load_config
from bot.handlers.commands import start_command
from bot.handlers.menu_keyboards import (
    authorize_menu,
    information_menu,
    main_menu,
    schedule_menu,
    settings_menu,
    submission_menu,
)
from bot.handlers.others import exceptions_handler, fallback_handler, not_authorized_handler
from bot.i18n import create_i18n, setup_bot_commands
from bot.logging_setup import setup_logging
from bot.middlewares.last_activity import LastActivityMiddleware
from bot.middlewares.localization import Localization
from bot.middlewares.student_settings import StudentSettingsMiddleware
from bot.services.api_client import ApiClient
from bot.services.settings_cache import SettingsCache

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, dispatcher: Dispatcher, config: Config, api: ApiClient) -> None:
    await api.open()
    await bot.set_webhook(
        config.webhook_full_url,
        secret_token=config.webhook_secret.get_secret_value(),
        allowed_updates=dispatcher.resolve_used_update_types(),
    )
    await setup_bot_commands(bot, dispatcher["i18n"])
    logger.info("Bot started")


async def on_shutdown(bot: Bot, api: ApiClient) -> None:
    await api.close()
    await bot.session.close()
    logger.info("Bot stopped")


def create_dispatcher(config: Config) -> Dispatcher:
    i18n = create_i18n()
    dispatcher = Dispatcher(
        config=config,
        i18n=i18n,
        api=ApiClient(config.api_url, config.api_token.get_secret_value(), config.api_timeout),
        settings_cache=SettingsCache(),
    )

    dispatcher.update.outer_middleware(StudentSettingsMiddleware())
    Localization(i18n=i18n).setup(dispatcher)
    dispatcher.message.outer_middleware(LastActivityMiddleware())

    dispatcher.include_routers(
        start_command.router,
        authorize_menu.router,
        main_menu.router,
        schedule_menu.router,
        information_menu.router,
        settings_menu.router,
        submission_menu.router,
        not_authorized_handler.router,
        fallback_handler.router,
        exceptions_handler.router,
    )

    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
    return dispatcher


def main() -> None:
    config = load_config()
    setup_logging(config.log_level, config.log_file)

    dispatcher = create_dispatcher(config)
    bot = Bot(
        config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
    )

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=config.webhook_secret.get_secret_value(),
    ).register(app, path=config.webhook_path)
    setup_application(app, dispatcher, bot=bot)

    web.run_app(app, host=config.webserver, port=config.port, print=None)


if __name__ == "__main__":
    main()
