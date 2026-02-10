from typing import Literal
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.formatter import CATEGORIES

from database.db_query import db

"""<<<---------- USER MAIN MENU BUTTONS ---------->>>"""
async def user_main_menu_buttons(lang:str, user_id: int = None)->InlineKeyboardMarkup:
    callback_data = "user:main_menu:{mode}"
    add_income = {
        'en':"Add Income 💰",
        'ru':"Добавить доход 💰",
        'uz':"Daromad qo‘shish 💰"
    }

    add_expense = {
        'en': "Add Expense 💸",
        'ru': "Добавить расход 💸",
        'uz': "Xarajat qo‘shish 💸"
    }

    statistics = {
        'en': "Statistics 📊",
        'ru': "Статистика 📊",
        'uz': "Statistika 📊"
    }

    contact_to_admin = {
        'en': "Support 📨",
        'ru': "Поддержка 📨",
        'uz': "Yordam 📨"
    }

    settings = {
        'en': "Settings ⚙️",
        'ru': "Настройки ⚙️",
        'uz': "Sozlamalar ⚙️"
    }

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=add_income[lang], callback_data=callback_data.format(mode='add_income')),
        InlineKeyboardButton(text=add_expense[lang], callback_data=callback_data.format(mode='add_expense'))
    )

    builder.row(
        InlineKeyboardButton(text=statistics[lang],
                             web_app=WebAppInfo(url='https://dottie-unbespoken-causatively.ngrok-free.dev?page=dashboard')),
        InlineKeyboardButton(text=settings[lang],
                             web_app=WebAppInfo(url='https://dottie-unbespoken-causatively.ngrok-free.dev?page=settings')))

    builder.row(InlineKeyboardButton(text=contact_to_admin[lang], callback_data=callback_data.format(mode='contact')))

    return builder.as_markup()


"""<<<------------ USER SELECT LANGUAGE BUTTONS ON REGISTRATION AND ON SETTINGS---------->>>"""
async def select_language_buttons()->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 3
    builder.add(
        InlineKeyboardButton(text='🇷🇺 Русский', callback_data='user:select_user_language:ru'),
        InlineKeyboardButton(text='🇬🇧 English', callback_data='user:select_user_language:en'),
        InlineKeyboardButton(text='🇺🇿 O‘zbekcha', callback_data='user:select_user_language:uz')
    )
    return builder.as_markup()

"""<<<---------- USER SELECT SEX BUTTONS ON REGISTRATION ---------->>>"""
async def select_sex_buttons(lang:str)->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    sex = {
        'uz': {'male':"👨 Erkak", 'female':"👩 Ayol"},
        'ru': {'male':"👨 Мужчина", 'female':"👩 Женщина"},
        'en': {'male':"👨 Male", 'female':"👩 Female"}
    }
    builder.add(
        InlineKeyboardButton(text=sex[lang]['male'], callback_data='user:select_user_sex:male'),
        InlineKeyboardButton(text=sex[lang]['female'], callback_data='user:select_user_sex:female')
    )
    return builder.as_markup()

"""<<<---------- USER SELECT SOCIAL STATUS BUTTONS ON REGISTRATION ---------->>>"""
async def select_user_status_buttons(lang:str, sex:Literal['male', 'female'])->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width=1
    statuses = {
        'pupil': {'uz': "👦 O‘quvchi", 'ru': "👦 Ученик", 'en': '👦 School student'},
        'student': {'uz': "👨‍🎓 Talaba", 'ru': "👨‍🎓 Студент", 'en': "👨‍🎓 University student"},
        'worker': {'uz': "👨‍🏭 Ishchi / Hodim", 'ru': "👨‍🏭 Рабочий / Сотрудник", 'en': "👨‍🏭 Worker / Employee"},
        'businessman': {'uz': "👨‍💼 Tadbirkor", 'ru': "👨‍💼 Предприниматель", 'en': "👨‍💼 Entrepreneur"},
        'retired': {'uz': "👴 Pensiyoner", 'ru': "👴 Пенсионер", 'en': "👴 Retired"},
        'other': {'uz': "❓ Boshqa", 'ru': "❓ Другое", 'en': "❓ Other"}
    }
    if sex=='female':
        statuses.update({
            'pupil': {'uz': "👧 O‘quvchi", 'ru': "👧 Ученица", 'en': '👧 School student'},
            'student': {'uz': "👩‍🎓 Talaba", 'ru': "👩‍🎓 Студентка", 'en': "👩‍🎓 University student"},
            'homemaker':{'uz':"🏠 Uy bekasi", 'ru':"🏠 Домохозяйка", 'en':"🏠 Homemaker"},
            'worker': {'uz': "👩‍🏭 Ishchi / Hodima", 'ru': "👩‍🏭 Рабочая / Сотрудница", 'en': "👩‍🏭 Worker / Employee"},
            'businessman': {'uz': "👩‍💼 Tadbirkor ayol", 'ru': "👩‍💼 Предпринимательница", 'en': "👩‍💼 Entrepreneur"},
            'retired': {'uz': "👵 Pensiyoner", 'ru': "👵 Пенсионерка", 'en': "👵 Retired"}
        })

    for key, value in statuses.items():
        builder.add(InlineKeyboardButton(text=value[lang], callback_data=f"user:select_user_status:{key}"))
    return builder.as_markup()

"""<<<---------- SELECT USER CURRENCY BUTTONS ON REGISTRATION ---------->>>"""
async def select_user_currency_buttons(lang:str)->InlineKeyboardMarkup:
    currencies = {'usd':"🇺🇸 USD", 'uzs':"🇺🇿 UZS", 'eur':"🇪🇺 EUR", 'rub':"🇷🇺 RUB"}
    builder = InlineKeyboardBuilder()
    builder.max_width=4
    for cur in currencies:
        builder.add(InlineKeyboardButton(text=currencies[cur], callback_data=f'user:select_user_currency:{cur}'))
    return builder.as_markup()

"""<---------- INCOME SOURCES ---------->"""
async def select_income_source_buttons(lang:str, user_id: int)->InlineKeyboardMarkup:
    rows = await db.get_categories(user_id, 'income')

    builder = InlineKeyboardBuilder()
    for r in rows:
        builder.row(InlineKeyboardButton(text=f"{r['emoji']} {r['name']}", callback_data=f"user:add_income_select:{r['name']}"))

    builder.row(InlineKeyboardButton(text="✏️ Other" if lang=='en' else "✏️ Boshqa" if lang=='uz' else "✏️ Другое", callback_data="user:add_income_select:other"))
    return builder.as_markup()

"""<---------- EXPENSE SOURCES ---------->"""
async def select_expense_source_buttons(lang:str, user_id: int)->InlineKeyboardMarkup:
    rows = await db.get_categories(user_id, 'expense')

    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    for r in rows:
        builder.add(InlineKeyboardButton(text=f"{r['emoji']} {r['name']}", callback_data=f"user:add_expense_source:{r['name']}"))

    builder.add(InlineKeyboardButton(text="🔧 Other" if lang=='en' else "🔧 Boshqa" if lang=='uz' else "🔧 Другое", callback_data="user:add_expense_source:other"))
    return builder.as_markup()

async def select_payment_method_buttons(lang:str, type: Literal['income', 'expense'])->InlineKeyboardMarkup:
    methods = {
        'cash': {'en': "💵 Cash", 'uz': "💵 Naqd", 'ru': "💵 Наличные"},
        'card': {'en': "💳 Card", 'uz': "💳 Karta", 'ru': "💳 Карта"}
    }
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    for key, value in methods.items():
        builder.add(InlineKeyboardButton(text=value[lang], callback_data=f'user:add_{type}_payment_method:{key}'))
    return builder.as_markup()

async def add_additional_info_button(lang:str, income_id:int)->InlineKeyboardMarkup:
    text = {'en': "📝 Add Notes", 'uz': "📝 Izoh qo'shish", 'ru': "📝 Добавить заметку"}
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text[lang], callback_data=f'user:add_income_additional_info:{income_id}')]])

async def get_expense_additional_info_buttons(lang:str, expense_id:int)->InlineKeyboardMarkup:
    text = {'en': "📝 Add Notes", 'uz': "📝 Izoh qo'shish", 'ru': "📝 Добавить заметку"}
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text[lang], callback_data=f'user:add_expense_add_info:{expense_id}'))
    return builder.as_markup()
