TRANSLATIONS = {
    "uz": {
        "title": "Moliya Nazorati",
        "nav_add": "➕ Tranzaksiya",
        "nav_settings": "⚙️ Sozlamalar",

        # Add Transaction Screen
        "add_transaction": "Yangi Tranzaksiya Qo'shish",
        "type": "Turi:",
        "expense": "Chiqim 💸",
        "income": "Kirim 💰",
        "amount": "Mablaq:",
        "amount_hint": "Summani kiriting...",
        "category": "Kategoriya:",
        "currency": "Valyuta:",
        "notes": "Qo'shimcha izoh:",
        "notes_hint": "Izoh (ixtiyoriy)...",
        "submit": "Saqlash",
        "success_add": "Tranzaksiya muvaffaqiyatli saqlandi!",
        "error_invalid_amount": "Iltimos, to'g'ri summa kiriting!",
        "error_no_category": "Iltimos, kategoriyani tanlang!",

        # Settings Screen
        "settings_title": "Sozlamalar",
        "user_profile": "Foydalanuvchi Profili",
        "fullname": "To'liq ism:",
        "sex": "Jinsi:",
        "male": "Erkak",
        "female": "Ayol",
        "status": "Ijtimoiy maqom:",
        "employee": "Xodim",
        "student": "Talaba",
        "businessman": "Tadbirkor",
        "unemployed": "Ishsiz",
        "language": "Ilova tili:",
        "default_currency": "Asosiy valyuta:",
        "save_profile": "Profilni Saqlash",
        "profile_saved": "Profil muvaffaqiyatli saqlandi!",

        # Category Management
        "categories_title": "Kategoriyalarni Boshqarish",
        "manage_expense_cats": "Chiqim Kategoriyalari",
        "manage_income_cats": "Kirim Kategoriyalari",
        "add_cat_hint": "Yangi kategoriya nomi...",
        "add_cat_btn": "Qo'shish",
        "delete": "O'chirish",
        "cat_added": "Kategoriya qo'shildi!",
        "cat_deleted": "Kategoriya o'chirildi!",
        "cat_exists": "Bu kategoriya allaqachon mavjud!",
        "cat_empty": "Kategoriya nomi bo'sh bo'lishi mumkin emas!"
    },
    "en": {
        "title": "Finance Tracker",
        "nav_add": "➕ Transaction",
        "nav_settings": "⚙️ Settings",

        # Add Transaction Screen
        "add_transaction": "Add New Transaction",
        "type": "Type:",
        "expense": "Expense 💸",
        "income": "Income 💰",
        "amount": "Amount:",
        "amount_hint": "Enter amount...",
        "category": "Category:",
        "currency": "Currency:",
        "notes": "Additional Notes:",
        "notes_hint": "Note (optional)...",
        "submit": "Save Transaction",
        "success_add": "Transaction saved successfully!",
        "error_invalid_amount": "Please enter a valid amount!",
        "error_no_category": "Please select a category!",

        # Settings Screen
        "settings_title": "Settings",
        "user_profile": "User Profile",
        "fullname": "Full Name:",
        "sex": "Gender:",
        "male": "Male",
        "female": "Female",
        "status": "Social Status:",
        "employee": "Employee",
        "student": "Student",
        "businessman": "Businessman",
        "unemployed": "Unemployed",
        "language": "App Language:",
        "default_currency": "Default Currency:",
        "save_profile": "Save Profile",
        "profile_saved": "Profile saved successfully!",

        # Category Management
        "categories_title": "Manage Categories",
        "manage_expense_cats": "Expense Categories",
        "manage_income_cats": "Income Categories",
        "add_cat_hint": "New category name...",
        "add_cat_btn": "Add",
        "delete": "Delete",
        "cat_added": "Category added!",
        "cat_deleted": "Category deleted!",
        "cat_exists": "Category already exists!",
        "cat_empty": "Category name cannot be empty!"
    },
    "ru": {
        "title": "Финансовый Трекер",
        "nav_add": "➕ Транзакция",
        "nav_settings": "⚙️ Настройки",

        # Add Transaction Screen
        "add_transaction": "Добавить Транзакцию",
        "type": "Тип:",
        "expense": "Расход 💸",
        "income": "Доход 💰",
        "amount": "Сумма:",
        "amount_hint": "Введите сумму...",
        "category": "Категория:",
        "currency": "Валюта:",
        "notes": "Примечание:",
        "notes_hint": "Заметка (необязательно)...",
        "submit": "Сохранить",
        "success_add": "Транзакция успешно сохранена!",
        "error_invalid_amount": "Пожалуйста, введите корректную сумму!",
        "error_no_category": "Пожалуйста, выберите категорию!",

        # Settings Screen
        "settings_title": "Настройки",
        "user_profile": "Профиль Пользователя",
        "fullname": "Полное имя:",
        "sex": "Пол:",
        "male": "Мужской",
        "female": "Женский",
        "status": "Социальный статус:",
        "employee": "Сотрудник",
        "student": "Студент",
        "businessman": "Предприниматель",
        "unemployed": "Безработный",
        "language": "Язык приложения:",
        "default_currency": "Основная валюта:",
        "save_profile": "Сохранить Профиль",
        "profile_saved": "Профиль успешно сохранен!",

        # Category Management
        "categories_title": "Управление Категориями",
        "manage_expense_cats": "Категории Расходов",
        "manage_income_cats": "Категории Доходов",
        "add_cat_hint": "Имя новой категории...",
        "add_cat_btn": "Добавить",
        "delete": "Удалить",
        "cat_added": "Категория добавлена!",
        "cat_deleted": "Категория удалена!",
        "cat_exists": "Категория уже существует!",
        "cat_empty": "Имя категории не может быть пустым!"
    }
}

def get_text(key: str, lang: str = "uz") -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["uz"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
