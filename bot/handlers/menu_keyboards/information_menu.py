from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from pydantic import BaseModel

from bot.filters.is_authorized import IsAuthorized
from bot.filters.localized_text import LocalizedText
from bot.keyboards.inline import link_keyboard
from bot.keyboards.reply import back_main_keyboard, list_keyboard
from bot.models import LinkInformation, StudentInformation, SubjectInformation, TeacherInformation
from bot.services.api_client import ApiClient
from bot.states import LinkStates, StudentStates, SubjectStates, TeacherStates
from bot.utilities.text import optional_line, quote

router = Router(name="information_menu")


async def show_items(message: Message, state: FSMContext, target_state: State, title: str,
                     items: list[BaseModel], labels: list[str]) -> None:
    await state.clear()
    await state.set_state(target_state)
    await state.set_data({"items": [item.model_dump(mode="json") for item in items], "labels": labels})
    await message.answer(title, reply_markup=list_keyboard(labels, main_menu=True))


async def find_item[ModelT: BaseModel](message: Message, state: FSMContext, model: type[ModelT]) -> ModelT | None:
    data = await state.get_data()
    labels: list[str] = data.get("labels", [])

    if message.text not in labels:
        await message.answer(_("Не коректне введення!"))
        return None

    return model.model_validate(data["items"][labels.index(message.text)])


def join_lines(title: str, lines: list[str | None]) -> str:
    return "\n".join([f"<b>{quote(title)}</b>", ""] + [line for line in lines if line])


@router.message(LocalizedText("🧑‍🎓 Студенти"), IsAuthorized())
@router.message(StudentStates.select, LocalizedText("↩ Назад"))
async def show_students(message: Message, state: FSMContext, api: ApiClient) -> None:
    students = await api.get_students()
    labels = [student.full_name for student in students]
    await show_items(message, state, StudentStates.select, _("🧑‍🎓 Студенти"), students, labels)


@router.message(StudentStates.select)
async def send_student_information(message: Message, state: FSMContext) -> None:
    student = await find_item(message, state, StudentInformation)
    if student is None:
        return

    text = join_lines(student.full_name, [
        optional_line(_("Підгрупа: {value}"), student.subgroup),
        optional_line(_("Номер телефону: +{value}"), student.contact_phone),
        optional_line(_("Пошта: {value}"), student.email),
        optional_line(_("Фітовська пошта: {value}"), student.fit_email),
        optional_line(_("Нік в телеграм: {value}"), student.telegram_nickname),
        optional_line(_("День народження: {value}"), student.birthday),
    ])

    await message.answer(text, reply_markup=back_main_keyboard())

    if student.telegram_phone:
        await message.answer_contact(phone_number=student.telegram_phone, first_name=student.name,
                                     last_name=student.surname)


@router.message(LocalizedText("🧑🏻‍🏫 Викладачі"), IsAuthorized())
@router.message(TeacherStates.select, LocalizedText("↩ Назад"))
async def show_teachers(message: Message, state: FSMContext, api: ApiClient) -> None:
    teachers = await api.get_teachers()
    labels = [teacher.full_name for teacher in teachers]
    await show_items(message, state, TeacherStates.select, _("🧑🏻‍🏫 Викладачі"), teachers, labels)


@router.message(TeacherStates.select)
async def send_teacher_information(message: Message, state: FSMContext) -> None:
    teacher = await find_item(message, state, TeacherInformation)
    if teacher is None:
        return

    text = join_lines(teacher.full_name, [
        optional_line(_("Номер телефону: +{value}"), teacher.contact_phone),
        optional_line(_("Пошта: {value}"), teacher.email),
        optional_line(_("Фітовська пошта: {value}"), teacher.fit_email),
        optional_line(_("Нік в телеграм: {value}"), teacher.telegram_nickname),
    ])

    await message.answer(text, reply_markup=back_main_keyboard())


@router.message(LocalizedText("📖 Предмети"), IsAuthorized())
@router.message(SubjectStates.select, LocalizedText("↩ Назад"))
async def show_subjects(message: Message, state: FSMContext, api: ApiClient) -> None:
    subjects = await api.get_subjects()
    labels = [subject.name for subject in subjects]
    await show_items(message, state, SubjectStates.select, _("📖 Предмети"), subjects, labels)


@router.message(SubjectStates.select)
async def send_subject_information(message: Message, state: FSMContext) -> None:
    subject = await find_item(message, state, SubjectInformation)
    if subject is None:
        return

    text = join_lines(subject.name, [
        optional_line(_("Коротка назва: {value}"), subject.short_name),
        optional_line(_("Кількість лекційних днів: {value}"), subject.lectures_days_count),
        optional_line(_("Кількість практичних днів: {value}"), subject.practical_days_count),
        optional_line(_("Кількість лабораторних днів: {value}"), subject.laboratory_days_count),
    ])

    await message.answer(text, reply_markup=back_main_keyboard())


@router.message(LocalizedText("🌐 Посилання"), IsAuthorized())
async def show_links(message: Message, state: FSMContext, api: ApiClient) -> None:
    links = await api.get_links()
    labels = [item.name for item in links]
    await show_items(message, state, LinkStates.select, _("🌐 Посилання"), links, labels)


@router.message(LinkStates.select)
async def send_link_information(message: Message, state: FSMContext) -> None:
    item = await find_item(message, state, LinkInformation)
    if item is None:
        return

    text = f"<b>{quote(item.name)}</b>"
    if item.description:
        text += f"\n\n{quote(item.description)}"

    await message.answer(text, reply_markup=link_keyboard(item.name, item.url))
