from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline.user import select_income_source_buttons, add_additional_info_button, user_main_menu_buttons, \
    select_expense_source_buttons, get_expense_additional_info_buttons, select_payment_method_buttons
from utils.formatter import get_category_label
from lexicon.userstates import add_income_states, add_expense_states
from states.userstates import AddIncomeState, AddExpenseState
from handlers.user_entrypoint import user_router
from aiogram import F
from aiogram.types import CallbackQuery, Message
from database.db_query import db

"""<---------- /all_earnings AND /all_expenses COMMANDS[TEMPORARY]: ---------->"""
@user_router.message(Command('all_earnings'))
async def user_get_all_incomes_temp(message:Message):
    all_incomes = await db.get_all_users_earnings()
    if not all_incomes:
        await message.answer('There is no any earning')
        return
    message_text = ""
    for index, income in enumerate(all_incomes):
        message_text+=f'{index+1}: {list(dict(income).values())}\n'
    await message.answer(message_text)
    return

@user_router.message(Command('all_expenses'))
async def user_get_all_incomes_temp(message:Message):
    all_expenses = await db.get_all_users_expenses()
    if not all_expenses:
        await message.answer('There is no any expense')
        return
    message_text = ""
    for index, expense in enumerate(all_expenses):
        message_text+=f'{index+1}: {list(dict(expense).values())}\n'
    await message.answer(message_text)
    return

"""<---------- MAIN MENU HANDLER: ---------->"""
@user_router.callback_query(F.data.startswith('user:main_menu:'))
async def user_main_menu_handler(callback:CallbackQuery, state:FSMContext):
    option = callback.data.split(':')[-1]
    user_id = int(callback.from_user.id)
    lang = await db.get_user_language(user_id=user_id)
    if option == 'add_income':
        await callback.message.answer(add_income_states['get_amount'][lang])
        await state.set_state(AddIncomeState.get_amount)
        await state.update_data(user_language=lang)
        return
    elif option == 'add_expense':
        await callback.message.answer(add_expense_states['get_amount'][lang])
        await state.set_state(AddExpenseState.get_amount)
        await state.update_data(user_language=lang)
        return
    elif option == 'statistics':
        pass
    elif option == 'settings':
        pass
    elif option == 'contact':
        pass
    else:
        pass

"""<---------- ADDING USER INCOME ---------->"""
@user_router.message(F.content_type==ContentType.TEXT, AddIncomeState.get_amount)
async def get_income_amount(message:Message, state:FSMContext):
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    user_text = message.text
    try:
        amount = int(user_text)
    except:
        try:
            amount = float(user_text)
        except:
            await message.answer(add_income_states['wrong_amount'][lang])
            await state.set_state(AddIncomeState.get_amount)
            return
    data['amount'] = amount
    await message.answer(add_income_states['get_source'][lang], reply_markup=await select_income_source_buttons(lang=lang, user_id=message.from_user.id))
    await state.update_data(data=data)
    await state.set_state(AddIncomeState.get_source)
    return

@user_router.callback_query(F.data.startswith('user:add_income_select:'), AddIncomeState.get_source)
async def get_income_source(callback:CallbackQuery, state:FSMContext):
    source = callback.data.split(':')[-1]
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    try:
        await callback.message.delete()
    except:
        pass

    if source=='other':
        await callback.message.answer(add_income_states['get_source_manually'][lang])
        await state.set_state(AddIncomeState.get_source_manually)
        return

    data['source'] = source
    await state.update_data(data=data)
    await callback.message.answer(add_income_states['get_payment_method'][lang], reply_markup=await select_payment_method_buttons(lang=lang, type='income'))
    await state.set_state(AddIncomeState.get_payment_method)
    return

@user_router.message(F.text, AddIncomeState.get_source_manually)
async def get_source_manually(message:Message, state:FSMContext):
    source = message.text
    data = await state.get_data()
    data['source'] = source
    lang = data.get('user_language', 'en')
    await state.update_data(data=data)
    await message.answer(add_income_states['get_payment_method'][lang], reply_markup=await select_payment_method_buttons(lang=lang, type='income'))
    await state.set_state(AddIncomeState.get_payment_method)
    return

@user_router.callback_query(F.data.startswith('user:add_income_payment_method:'), AddIncomeState.get_payment_method)
async def get_income_payment_method(callback:CallbackQuery, state:FSMContext):
    payment_method = callback.data.split(':')[-1]
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    amount = data.get('amount')
    source = data.get('source')

    try:
        await callback.message.delete()
    except:
        pass

    user_currency = await db.execute("SELECT currency FROM users WHERE telegram_id = $1", callback.from_user.id, fetchval=True)
    income_id = await db.add_income(user_id=callback.from_user.id, amount=amount, source=source, payment_method=payment_method)
    if income_id is None:
        await callback.message.answer(add_income_states['failed_to_add'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=callback.from_user.id))
        await state.clear()
        return

    source_label = get_category_label(source, lang)
    method_label = "💵 Cash" if payment_method == 'cash' else "💳 Card"
    if lang == 'uz': method_label = "💵 Naqd" if payment_method == 'cash' else "💳 Karta"
    elif lang == 'ru': method_label = "💵 Наличные" if payment_method == 'cash' else "💳 Карта"

    success_msg = add_income_states['added_successfully'][lang].format(
        amount=f"{amount:,}",
        currency=user_currency.upper() if user_currency else "",
        source=source_label,
        method=method_label,
        notes="-"
    )

    button = await add_additional_info_button(lang=lang, income_id=income_id)
    await callback.message.answer(text=success_msg, reply_markup=button)
    await state.clear()
    return

@user_router.callback_query(F.data.startswith('user:add_income_additional_info:'))
async def income_add_additional_info(callback:CallbackQuery, state:FSMContext):
    income_id = int(callback.data.split(':')[-1])
    lang = await db.get_user_language(user_id=callback.from_user.id)
    await callback.message.answer(add_income_states['enter_additional_info'][lang])
    await state.set_state(AddIncomeState.get_more_information)
    await state.update_data(lang=lang, income_id=income_id)
    return

@user_router.message(F.text, AddIncomeState.get_more_information)
async def get_income_additional_info(message:Message, state:FSMContext):
    additional_info = message.text
    data = await state.get_data()
    income_id = data.get('income_id')
    lang = data.get('lang', 'en')
    await db.set_income_additional_info(income_id, additional_info)
    try:
        await message.answer(add_income_states['additional_info_added'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=message.from_user.id))
        await state.clear()
        return
    except Exception as er:
        await message.answer(add_income_states['additional_info_not_added'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=message.from_user.id))
        await state.clear()
        return


"""<----------- ADDING USER EXPENSE --------->"""
@user_router.message(F.content_type==ContentType.TEXT, AddExpenseState.get_amount)
async def expense_add_amount(message:Message, state:FSMContext):
    user_text = message.text
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    try:
        amount = int(user_text)
    except:
        try:
            amount = float(user_text)
        except:
            await message.answer(add_expense_states['wrong_amount'][lang])
            await state.set_state(AddExpenseState.get_amount)
            return

    data['amount'] = amount
    data['user_language']=lang
    await state.update_data(data=data)
    await message.answer(add_expense_states['get_source'][lang], reply_markup=await select_expense_source_buttons(lang=lang, user_id=message.from_user.id))
    await state.set_state(AddExpenseState.get_source)
    return

@user_router.callback_query(F.data.startswith('user:add_expense_source:'), AddExpenseState.get_source)
async def get_expense_source(callback:CallbackQuery, state:FSMContext):
    source = callback.data.split(':')[-1]
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    try:
        await callback.message.delete()
    except:
        pass
    if source=='other':
        await callback.message.answer(add_expense_states['get_source_manually'][lang])
        await state.set_state(AddExpenseState.get_source_manually)
        return

    data['source'] = source
    await state.update_data(data=data)
    await callback.message.answer(add_expense_states['get_payment_method'][lang], reply_markup=await select_payment_method_buttons(lang=lang, type='expense'))
    await state.set_state(AddExpenseState.get_payment_method)
    return

@user_router.message(F.content_type==ContentType.TEXT, AddExpenseState.get_source_manually)
async def get_expense_source_manually(message:Message, state:FSMContext):
    source = message.text.strip()
    data = await state.get_data()
    data['source'] = source
    lang = data.get('user_language', 'en')
    await state.update_data(data=data)
    await message.answer(add_expense_states['get_payment_method'][lang], reply_markup=await select_payment_method_buttons(lang=lang, type='expense'))
    await state.set_state(AddExpenseState.get_payment_method)
    return

@user_router.callback_query(F.data.startswith('user:add_expense_payment_method:'), AddExpenseState.get_payment_method)
async def get_expense_payment_method(callback:CallbackQuery, state:FSMContext):
    payment_method = callback.data.split(':')[-1]
    data = await state.get_data()
    lang = data.get('user_language', 'en')
    amount = data.get('amount')
    source = data.get('source')

    try:
        await callback.message.delete()
    except:
        pass

    user_currency = await db.execute("SELECT currency FROM users WHERE telegram_id = $1", callback.from_user.id, fetchval=True)
    expense_id = await db.add_expense(user_id=callback.from_user.id, amount=amount, source=source, payment_method=payment_method)
    if expense_id is None:
        await callback.message.answer(add_expense_states['failed_to_save'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=callback.from_user.id))
        await state.clear()
        return

    source_label = get_category_label(source, lang)
    method_label = "💵 Cash" if payment_method == 'cash' else "💳 Card"
    if lang == 'uz': method_label = "💵 Naqd" if payment_method == 'cash' else "💳 Karta"
    elif lang == 'ru': method_label = "💵 Наличные" if payment_method == 'cash' else "💳 Карта"

    success_msg = add_expense_states['added_successfully'][lang].format(
        amount=f"{amount:,}",
        currency=user_currency.upper() if user_currency else "",
        source=source_label,
        method=method_label,
        notes="-"
    )

    await callback.message.answer(success_msg, reply_markup=await get_expense_additional_info_buttons(lang=lang, expense_id=expense_id))
    await state.clear()
    return

@user_router.callback_query(F.data.startswith('user:add_expense_add_info:'))
async def get_user_expense_additional_info(callback:CallbackQuery, state:FSMContext):
    text = callback.message.text.strip()
    expense_id = int(callback.data.split(':')[-1])
    lang = await db.get_user_language(user_id=callback.from_user.id)
    await callback.message.answer(add_expense_states['enter_additional_info'][lang])
    await state.set_state(AddExpenseState.get_more_information)
    await state.update_data(lang=lang, expense_id=expense_id)
    return

@user_router.message(F.text, AddExpenseState.get_more_information)
async def get_expense_additional_info(message:Message, state:FSMContext):
    additional_info = message.text
    data = await state.get_data()
    income_id = data.get('expense_id')
    lang = data.get('lang', 'en')
    await db.set_income_additional_info(income_id, additional_info)
    try:
        await message.answer(add_expense_states['additional_info_added'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=message.from_user.id))
        await state.clear()
        return
    except Exception as er:
        await message.answer(add_expense_states['additional_info_not_added'][lang], reply_markup=await user_main_menu_buttons(lang=lang, user_id=message.from_user.id))
        await state.clear()
        return
