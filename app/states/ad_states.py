from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_contact = State()


class AdCreation(StatesGroup):
    choosing_category = State()
    answering_questions = State()
    uploading_photos = State()
    confirming = State()
