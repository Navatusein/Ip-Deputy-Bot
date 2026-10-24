from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.config import Config
from bot.filters.is_authorized import IsAuthorized
from bot.filters.localized_text import LocalizedText
from bot.keyboards.inline import web_app_keyboard
from bot.keyboards.reply import list_keyboard, submission_menu_keyboard
from bot.models import SubmissionsConfig
from bot.services.api_client import ApiClient
from bot.states import SubmissionStates
from bot.utilities.submission_format import format_submission_list
from bot.utilities.text import quote, unique

router = Router(name="submission_menu")


def subgroup_label(config: SubmissionsConfig) -> str:
    return config.subgroup or _("Усі підгрупи")


async def send_submission_list(message: Message, state: FSMContext, config: SubmissionsConfig,
                               app_config: Config) -> None:
    await state.clear()
    await message.answer(format_submission_list(config, app_config.tz), reply_markup=submission_menu_keyboard())


@router.message(LocalizedText("➕ Записатись"), IsAuthorized())
async def open_submission_registration(message: Message, config: Config) -> None:
    text = _("➕ Записатись") + "\n" + _("Натисніть на кнопку щоб відкрити інтерфейс 👇")
    await message.answer(text, reply_markup=web_app_keyboard(config.frontend_url, "/submission-registration"))


@router.message(LocalizedText("🧾 Мої записи"), IsAuthorized())
async def open_my_submissions(message: Message, config: Config) -> None:
    text = _("🧾 Мої записи") + "\n" + _("Натисніть на кнопку щоб відкрити інтерфейс 👇")
    await message.answer(text, reply_markup=web_app_keyboard(config.frontend_url, "/submission-student"))


@router.message(SubmissionStates.type, LocalizedText("↩ Назад"))
@router.message(LocalizedText("🗳 Отримати список"), IsAuthorized())
async def show_submission_subjects(message: Message, state: FSMContext, api: ApiClient) -> None:
    configs = await api.get_submissions_configs()
    names = unique([item.name for item in configs])

    await state.clear()
    await state.set_state(SubmissionStates.subject)
    await message.answer(_("🗳 Отримати список"), reply_markup=list_keyboard(names, main_menu=True))


@router.message(SubmissionStates.subgroup, LocalizedText("↩ Назад"))
@router.message(SubmissionStates.subject)
async def select_submission_subject(message: Message, state: FSMContext, api: ApiClient) -> None:
    data = await state.get_data()
    current = await state.get_state()
    name = data.get("name") if current == SubmissionStates.subgroup.state else message.text

    configs = await api.get_submissions_configs()
    types = unique([item.type for item in configs if item.name == name])

    if not types:
        await message.answer(_("Не коректне введення!"))
        return

    await state.set_state(SubmissionStates.type)
    await state.set_data({"name": name})
    await message.answer(quote(name), reply_markup=list_keyboard(types, back=True))


@router.message(SubmissionStates.type)
async def select_submission_type(message: Message, state: FSMContext, api: ApiClient, config: Config) -> None:
    data = await state.get_data()
    name: str = data["name"]

    configs = await api.get_submissions_configs()
    matching = [item for item in configs if item.name == name and item.type == message.text]

    if not matching:
        await message.answer(_("Не коректне введення!"))
        return

    if len(matching) == 1:
        await send_submission_list(message, state, matching[0], config)
        return

    await state.set_state(SubmissionStates.subgroup)
    await state.set_data({"name": name, "type": message.text})
    subgroups = unique([subgroup_label(item) for item in matching])
    await message.answer(quote(message.text), reply_markup=list_keyboard(subgroups, back=True))


@router.message(SubmissionStates.subgroup)
async def select_submission_subgroup(message: Message, state: FSMContext, api: ApiClient, config: Config) -> None:
    data = await state.get_data()
    name: str = data["name"]
    subject_type: str = data["type"]

    configs = await api.get_submissions_configs()
    selected = next(
        (item for item in configs
         if item.name == name and item.type == subject_type and subgroup_label(item) == message.text),
        None,
    )

    if selected is None:
        await message.answer(_("Не коректне введення!"))
        return

    await send_submission_list(message, state, selected, config)
