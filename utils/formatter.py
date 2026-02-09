import random

CATEGORIES = {
    # Income Sources
    'salary': {'en': '💼 Salary', 'uz': '💼 Ish haqi', 'ru': '💼 Зарплата'},
    'business': {'en': '🏢 Business Income', 'uz': '🏢 Biznes daromadi', 'ru': '🏢 Доход от бизнеса'},
    'rental_income': {'en': '🏠 Rental Income', 'uz': '🏠 Ijara daromadi', 'ru': '🏠 Доход от аренды'},
    'investment': {'en': '📈 Investment Income', 'uz': '📈 Investitsiya daromadi', 'ru': '📈 Инвестиционный доход'},
    'gift': {'en': '🎁 Gift', 'uz': '🎁 Sovg‘a', 'ru': '🎁 Подарок'},
    'side_income': {'en': '💡 Side Income', 'uz': '💡 Qo‘shimcha daromad', 'ru': '💡 Дополнительный доход'},
    'refund': {'en': '🔄 Refund', 'uz': '🔄 Qaytarilgan to‘lov', 'ru': '🔄 Возврат средств'},
    'other': {'en': '✏️ Other', 'uz': '✏️ Boshqa', 'ru': '✏️ Другое'},
    'parents': {'en': '👪 Parents’ Support', 'uz': '👪 Ota-ona yordami', 'ru': '👪 Поддержка родителей'},
    'scholarship': {'en': '🎓 Scholarship', 'uz': '🎓 Stipendiya', 'ru': '🎓 Стипендия'},
    'pension': {'en': '💳 Pension', 'uz': '💳 Pensiya', 'ru': '💳 Пенсия'},
    'husband': {'en': '❤️ Husband’s Support', 'uz': '❤️ Er yordami', 'ru': '❤️ Поддержка мужа'},

    # Expense Categories
    'food': {'uz': '🍔 Ovqat', 'en': '🍔 Food', 'ru': '🍔 Еда'},
    'transport': {'uz': '🚌 Transport', 'en': '🚌 Transport', 'ru': '🚌 Транспорт'},
    'shopping': {'uz': '🛍 Xarid', 'en': '🛍 Shopping', 'ru': '🛍 Покупки'},
    'health': {'uz': '💊 Sog‘liq', 'en': '💊 Health', 'ru': '💊 Здоровье'},
    'entertainment': {'uz': '🎮 Ko‘ngilochar', 'en': '🎮 Fun', 'ru': '🎮 Развлечения'},
    'subscriptions': {'uz': '📺 Obunalar', 'en': '📺 Subs', 'ru': '📺 Подписки'},
    'education': {'uz': '📚 Ta’lim', 'en': '📚 Education', 'ru': '📚 Обучение'},
    'housing': {'uz': '🏠 Ijara', 'en': '🏠 Rent', 'ru': '🏠 Аренда'},
    'utilities': {'uz': '💡 Kommunal', 'en': '💡 Utilities', 'ru': '💡 Коммуналка'},
    'personal_care': {'uz': '🧴 Parvarish', 'en': '🧴 Care', 'ru': '🧴 Уход'},
    'gifts': {'uz': '🎁 Sovg‘alar', 'en': '🎁 Gifts', 'ru': '🎁 Подарки'},
    'pets': {'uz': '🐾 Hayvonlar', 'en': '🐾 Pets', 'ru': '🐾 Питомцы'},
    'travel': {'uz': '✈️ Sayohat', 'en': '✈️ Travel', 'ru': '✈️ Путешествия'},
    'loans': {'uz': '💳 To‘lovlar', 'en': '💳 Loans', 'ru': '💳 Платежи'},
}

def get_category_label(key, lang):
    random_emojis = ["🏷️", "✨", "📌", "💎", "⭐", "🚀", "💡"]
    if key in CATEGORIES:
        return CATEGORIES[key].get(lang, key.capitalize())
    else:
        emoji = random.choice(random_emojis)
        return f"{emoji} {key.capitalize()}"
