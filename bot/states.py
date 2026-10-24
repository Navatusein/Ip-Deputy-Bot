from aiogram.fsm.state import State, StatesGroup


class StudentStates(StatesGroup):
    select = State()


class TeacherStates(StatesGroup):
    select = State()


class SubjectStates(StatesGroup):
    select = State()


class LinkStates(StatesGroup):
    select = State()


class SettingsStates(StatesGroup):
    language = State()
    schedule_format = State()


class SubmissionStates(StatesGroup):
    subject = State()
    type = State()
    subgroup = State()
