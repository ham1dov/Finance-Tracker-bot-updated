from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import CallbackQuery

from database.db_query import db
user_router = Router()

from lexicon.userstates import registration_states
from keyboards.inline.user import select_language_buttons, select_sex_buttons, select_user_status_buttons, \
    select_user_currency_buttons, user_main_menu_buttons
from config import DEFAULT_LANGUAGE
from states.userstates import RegistrationState

"""<<<---------------COMMAND START---------------->>>"""
@user_router.message(CommandStart())
async def start_command(message:types.Message, state:FSMContext):
    """

    Some code here to check REFERRAL SYSTEM
    Checking referrer_id
    Inserting to tables and so on...
    The logic needed in this stage will be thought in the next stage of development

    """
    telegram_id = message.from_user.id
    user = await db.get_user(telegram_id)

    if user:
        """============= Calling message sender function with main menu buttons =============="""
        return

    """============= Inserting user to 'users' table ============"""
    await message.answer(registration_states['start'][DEFAULT_LANGUAGE], reply_markup=await select_language_buttons())
    await state.set_state(RegistrationState.get_user_language)
    data = {}
    await state.set_data(data=data)
    return

"""<<<--------------- REGISTRATION POINT --------------->>>"""
@user_router.callback_query(F.data.startswith('user:select_user_language:'), RegistrationState.get_user_language)
async def get_user_language(callback:CallbackQuery, state:FSMContext):
    lang = callback.data.split(':')[-1]
    data = await state.get_data()
    data['lang'] = lang
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(registration_states['get_user_name'][lang])
    await state.update_data(data=data)
    await state.set_state(RegistrationState.get_user_name)
    return

@user_router.message(F.text, RegistrationState.get_user_name)
async def get_user_name(message:types.Message, state:FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    data['name'] = name
    await message.answer(registration_states['get_user_sex'][data['lang']], reply_markup=await select_sex_buttons(lang=data['lang']))
    await state.update_data(data=data)
    await state.set_state(RegistrationState.get_user_sex)
    return

@user_router.callback_query(F.data.startswith('user:select_user_sex:'), RegistrationState.get_user_sex)
async def get_user_sex(callback:CallbackQuery, state:FSMContext):
    sex = callback.data.split(':')[-1]
    data = await state.get_data()
    data['sex'] = sex
    lang = data['lang']
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(registration_states['get_user_status'][lang], reply_markup=await select_user_status_buttons(lang=lang, sex=sex))
    await state.update_data(data=data)
    await state.set_state(RegistrationState.get_user_social_status)
    return

@user_router.callback_query(F.data.startswith('user:select_user_status:'), RegistrationState.get_user_social_status)
async def get_user_status(callback:CallbackQuery, state:FSMContext):
    status = callback.data.split(':')[-1]
    data = await state.get_data()
    data['status'] = status
    lang = data['lang']
    try:
        await callback.message.delete()
    except:
        pass
    if status=='other':
        await callback.message.answer(registration_states['ask_user_status'][lang])
        await state.set_state(RegistrationState.get_user_social_status_manual)
        return

    await callback.message.answer(registration_states['get_user_currency'][lang], reply_markup=await select_user_currency_buttons(lang=lang))
    await state.update_data(data=data)
    await state.set_state(RegistrationState.get_user_currency)
    return

@user_router.message(F.text, RegistrationState.get_user_social_status_manual)
async def get_user_status_manual(message:types.Message, state:FSMContext):
    status = message.text.strip()
    data = await state.get_data()
    data['status'] = status
    lang = data['lang']
    await message.answer(registration_states['get_user_currency'][lang], reply_markup=await select_user_currency_buttons(lang=lang))
    await state.update_data(data=data)
    await state.set_state(RegistrationState.get_user_currency)
    return

@user_router.callback_query(F.data.startswith('user:select_user_currency:'), RegistrationState.get_user_currency)
async def get_user_currency(callback:CallbackQuery, state:FSMContext):
    currency = str(callback.data.split(':')[-1])
    data = await state.get_data()
    data['currency'] = currency
    try:
        await callback.message.delete()
    except:
        pass
    lang = data['lang']
    fullname = data['name']
    sex = data['sex']
    status = data['status']
    currency = data['currency']
    try:
        await db.add_new_user(
            user_id=callback.from_user.id,
            fullname=fullname,
            sex=sex,
            language=lang,
            status=status,
            currency=currency
        )
        await state.clear()
        await callback.message.answer(registration_states['successful_registration'][lang],
                                      reply_markup=await user_main_menu_buttons(lang=lang))
        return
    except Exception as er:
        print(str(er))
        await callback.message.answer(registration_states['registration_failed'][lang])
        await state.clear()
        return

