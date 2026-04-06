from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    get_user_language = State()
    get_user_name = State()
    get_user_sex = State()
    get_user_social_status = State()
    get_user_social_status_manual = State()
    get_user_currency = State()

class AddIncomeState(StatesGroup):
    get_amount = State()
    get_source = State()
    get_source_manually = State()
    get_payment_method = State()
    get_more_information = State()

class AddExpenseState(StatesGroup):
    get_amount = State()
    get_source = State()
    get_source_manually = State()
    get_payment_method = State()
    get_more_information = State()