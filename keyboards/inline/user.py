from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

"""<<<---------- USER MAIN MENU BUTTONS ---------->>>"""
async def user_main_menu_buttons(lang:str)->InlineKeyboardMarkup:
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
        'en': "Contact Admin 📨",
        'ru': "Связаться с администратором 📨",
        'uz': "Administrator bilan bog‘lanish 📨"
    }

    settings = {
        'en': "Settings ⚙️",
        'ru': "Настройки ⚙️",
        'uz': "Sozlamalar ⚙️"
    }

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=add_income[lang],
                                     callback_data=callback_data.format(mode='add_income')),
                InlineKeyboardButton(text=add_expense[lang],
                                     callback_data=callback_data.format(mode='add_expense'))
                )

    builder.row(
        InlineKeyboardButton(text=statistics[lang],
                             callback_data=callback_data.format(mode='statistics')),
        InlineKeyboardButton(text=settings[lang], callback_data=callback_data.format(mode='settings')))

    builder.row(InlineKeyboardButton(text=contact_to_admin[lang], callback_data=callback_data.format(mode='contact')))

    return builder.as_markup()


"""<<<------------ USER SELECT LANGUAGE BUTTONS ON REGISTRATION AND ON SETTINGS---------->>>"""
async def select_language_buttons()->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 3
    builder.add(
        InlineKeyboardButton(
            text='🇷🇺 Русский', callback_data='user:select_user_language:ru')
    )
    builder.add(
        InlineKeyboardButton(
            text='🇬🇧 English', callback_data='user:select_user_language:en'
        )
    )
    builder.add(
        InlineKeyboardButton(
            text='🇺🇿 O‘zbekcha', callback_data='user:select_user_language:uz'
        )
    )
    return builder.as_markup()

"""<<<---------- USER SELECT SEX BUTTONS ON REGISTRATION ---------->>>"""
async def select_sex_buttons(lang:str)->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    sex = {
        'uz':{
            'male':"👨 Erkak",
            'female':"👩 Ayol"
        },
        'ru':{
            'male':"👨 Мужчина",
            'female':"👩 Женщина"
        },
        'en':{
            'male':"👨 Male",
            'female':"👩 Female"
        }
    }
    builder.add(
        InlineKeyboardButton(
            text=sex[lang]['male'],
            callback_data='user:select_user_sex:male'
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=sex[lang]['female'],
            callback_data='user:select_user_sex:female'
        )
    )
    return builder.as_markup()

"""<<<---------- USER SELECT SOCIAL STATUS BUTTONS ON REGISTRATION ---------->>>"""
async def select_user_status_buttons(lang:str, sex:Literal['male', 'female'])->InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width=1
    statuses = {
        'pupil': {
            'uz': "👦 O‘quvchi",
            'ru': "👦 Ученик",
            'en': '👦 School student'
        },
        'student': {
            'uz': "👨‍🎓 Talaba",
            'ru': "👨‍🎓 Студент",
            'en': "👨‍🎓 University student"
        },
        'worker': {
            'uz': "👨‍🏭 Ishchi / Hodim",
            'ru': "👨‍🏭 Рабочий / Сотрудник",
            'en': "👨‍🏭 Worker / Employee"
        },
        'businessman': {
            'uz': "👨‍💼 Tadbirkor",
            'ru': "👨‍💼 Предприниматель",
            'en': "👨‍💼 Entrepreneur"
        },
        'retired': {
            'uz': "👴 Pensiyoner",
            'ru': "👴 Пенсионер",
            'en': "👴 Retired"
        },
        'other': {
            'uz': "❓ Boshqa",
            'ru': "❓ Другое",
            'en': "❓ Other"
        }
    }
    if sex=='female':
        statuses = {
            'pupil': {
                'uz': "👧 O‘quvchi",
                'ru': "👧 Ученица",
                'en': '👧 School student'
            },
            'student': {
                'uz': "👩‍🎓 Talaba",
                'ru': "👩‍🎓 Студентка",
                'en': "👩‍🎓 University student"
            },
            'homemaker':{
                'uz':"🏠 Uy bekasi",
                'ru':"🏠 Домохозяйка",
                'en':"🏠 Homemaker"

            },
            'worker': {
                'uz': "👩‍🏭 Ishchi / Hodima",
                'ru': "👩‍🏭 Рабочая / Сотрудница",
                'en': "👩‍🏭 Worker / Employee"
            },
            'businessman': {
                'uz': "👩‍💼 Tadbirkor ayol",
                'ru': "👩‍💼 Предпринимательница",
                'en': "👩‍💼 Entrepreneur"
            },
            'retired': {
                'uz': "👵 Pensiyoner",
                'ru': "👵 Пенсионерка",
                'en': "👵 Retired"
            },
            'other': {
                'uz': "❓ Boshqa",
                'ru': "❓ Другое",
                'en': "❓ Other"
            }
        }

    for key, value in statuses.items():
        builder.add(
            InlineKeyboardButton(
                text=value[lang], callback_data=f"user:select_user_status:{key}"
            )
        )
    return builder.as_markup()

"""<<<---------- SELECT USER CURRENCY BUTTONS ON REGISTRATION ---------->>>"""
async def select_user_currency_buttons(lang:str)->InlineKeyboardMarkup:
    currencies = {
        'usd':"🇺🇸 USD",
        'uzs':"🇺🇿 UZS",
        'eur':"🇪🇺 EUR",
        'rub':"🇷🇺 RUB"
    }
    builder = InlineKeyboardBuilder()
    builder.max_width=4
    for cur in currencies:
        builder.add(
            InlineKeyboardButton(
                text=currencies[cur],
                callback_data=f'user:select_user_currency:{cur}'
            )
        )
    return builder.as_markup()

"""<---------- INCOME SOURCES IN ADDING NEW INCOME ---------->"""
async def select_income_source_buttons(lang:str, social_status:str)->InlineKeyboardMarkup:
    social_statuses = ['pupil', 'student', 'worker', 'businessman', 'retired', 'homemaker', 'other']
    income_sources = {
        'salary': {
            'en': "💼 Salary",
            'uz': "💼 Ish haqi",
            'ru': "💼 Зарплата"
        },
        'business': {
            'en': "🏢 Business Income",
            'uz': "🏢 Biznes daromadi",
            'ru': "🏢 Доход от бизнеса"
        },
        'rental_income': {
            'en': "🏠 Rental Income",
            'uz': "🏠 Ijara daromadi",
            'ru': "🏠 Доход от аренды"
        },
        'investment': {
            'en': "📈 Investment Income",
            'uz': "📈 Investitsiya daromadi",
            'ru': "📈 Инвестиционный доход"
        },
        'gift': {
            'en': "🎁 Gift",
            'uz': "🎁 Sovg‘a",
            'ru': "🎁 Подарок"
        },
        'side_income': {
            'en': "💡 Side Income",
            'uz': "💡 Qo‘shimcha daromad",
            'ru': "💡 Дополнительный доход"
        },
        'refund': {
            'en': "🔄 Refund",
            'uz': "🔄 Qaytarilgan to‘lov",
            'ru': "🔄 Возврат средств"
        },
        'other': {
            'en': "✏️ Other",
            'uz': "✏️ Boshqa",
            'ru': "✏️ Другое"
        }
    }
    if social_status=='pupil':
        income_sources['parents']={
            'en':"👪 Parents’ Support",
            'uz':"👪 Ota-ona yordami",
            'ru':"👪 Поддержка родителей"
        }
        income_sources['rental_income'] = {}
    elif social_status=='student':
        income_sources['scholarship'] = {
            'en':"🎓 Scholarship",
            'uz':"🎓 Stipendiya",
            'ru':"🎓 Стипендия"
        }
        income_sources['rental_income'] = {}
    elif social_status=='worker':
        pass
    elif social_status=='businessman':
        pass
    elif social_status=='retired':
        income_sources['pension'] = {
            'en': "💳 Pension",
            'uz': "💳 Pensiya",
            'ru': "💳 Пенсия"
        }
    elif social_status=='homemaker':
        income_sources['husband'] = {
            'en':"❤️ Husband’s Support",
            'uz':"❤️ Er yordami",
            'ru':"❤️ Поддержка мужа"
        }
    else:
        pass
    builder = InlineKeyboardBuilder()
    for key, value in income_sources.items():
        if value is not {}:
            builder.row(InlineKeyboardButton(text=value[lang], callback_data=f'user:add_income_select:{key}'))

    return builder.as_markup()

async def add_additional_info_button(lang:str, income_id:int)->InlineKeyboardMarkup:
    text = {
        "en": "📝 Enter any additional notes about your income (optional):",
        "uz": "📝 Daromadga oid qo‘shimcha izoh kiriting (ixtiyoriy):",
        "ru": "📝 Введите дополнительные заметки о доходе (необязательно):"
    }

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text[lang], callback_data=f'user:add_income_additional_info:{income_id}')
            ]
        ]
    )

"""<---------- USER ADD EXPENSE SOURCE BUTTONS---------->"""
async def select_expense_source_buttons(lang:str)->InlineKeyboardMarkup:
    expense_categories = {
        "food": {
            "uz": "🍔 Ovqat",
            "en": "🍔 Food",
            "ru": "🍔 Еда"
        },
        "transport": {
            "uz": "🚌 Transport",
            "en": "🚌 Transport",
            "ru": "🚌 Транспорт"
        },
        "shopping": {
            "uz": "🛍 Xarid",
            "en": "🛍 Shopping",
            "ru": "🛍 Покупки"
        },
        "health": {
            "uz": "💊 Sog‘liq",
            "en": "💊 Health",
            "ru": "💊 Здоровье"
        },
        "entertainment": {
            "uz": "🎮 Ko‘ngilochar",
            "en": "🎮 Fun",
            "ru": "🎮 Развлечения"
        },
        "subscriptions": {
            "uz": "📺 Obunalar",
            "en": "📺 Subs",
            "ru": "📺 Подписки"
        },
        "education": {
            "uz": "📚 Ta’lim",
            "en": "📚 Education",
            "ru": "📚 Обучение"
        },
        "housing": {
            "uz": "🏠 Ijara",
            "en": "🏠 Rent",
            "ru": "🏠 Аренда"
        },
        "utilities": {
            "uz": "💡 Kommunal",
            "en": "💡 Utilities",
            "ru": "💡 Коммуналка"
        },
        "personal_care": {
            "uz": "🧴 Parvarish",
            "en": "🧴 Care",
            "ru": "🧴 Уход"
        },
        "gifts": {
            "uz": "🎁 Sovg‘alar",
            "en": "🎁 Gifts",
            "ru": "🎁 Подарки"
        },
        "pets": {
            "uz": "🐾 Hayvonlar",
            "en": "🐾 Pets",
            "ru": "🐾 Питомцы"
        },
        "travel": {
            "uz": "✈️ Sayohat",
            "en": "✈️ Travel",
            "ru": "✈️ Путешествия"
        },
        "loans": {
            "uz": "💳 To‘lovlar",
            "en": "💳 Loans",
            "ru": "💳 Платежи"
        },
        "other": {
            "uz": "🔧 Boshqa",
            "en": "🔧 Other",
            "ru": "🔧 Другое"
        }
    }
    builder = InlineKeyboardBuilder()
    builder.max_width=2
    for key, value in expense_categories.items():
        builder.add(InlineKeyboardButton(text=value[lang], callback_data=f'user:add_expense_source:{key}'))

    return builder.as_markup()

"""<---------- USER GET ADDITIONAL INFO ---------->"""
async def get_expense_additional_info_buttons(lang:str, expense_id:int)->InlineKeyboardMarkup:
    text = {
        "en": "📝 Enter any additional notes about your expense (optional):",
        "uz": "📝 Xarajatga oid qo‘shimcha izoh kiriting (ixtiyoriy):",
        "ru": "📝 Введите дополнительные заметки о расходе (необязательно):"
    }

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text[lang], callback_data=f'user:add_expense_add_info:{expense_id}'))
    return builder.as_markup()