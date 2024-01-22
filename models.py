from aiogram.filters.state import State, StatesGroup
class Form(StatesGroup):
    user_input = State()
    date_input = State()
    time_input = State()
    text_input = State()
    finish_reminder = State()


class States(StatesGroup):
    """ Класс состояния """
    # Ожидание ввода никнейма пользователя
    WaitingForUser = State()
    # Ожидание ввода Даты
    WaitingForDate = State()
    # Ожидание ввода Времени
    WaitingForTime = State()
    # Ожидание ввода Текста сообщения
    WaitingForText = State()
    # Ожидание подтверждения
    WaitingForConfirmation = State()
