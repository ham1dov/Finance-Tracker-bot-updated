import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppLocalization extends ChangeNotifier {
  static final AppLocalization _instance = AppLocalization._internal();
  factory AppLocalization() => _instance;
  AppLocalization._internal();

  String _currentLang = 'uz';

  String get currentLang => _currentLang;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _currentLang = prefs.getString('language') ?? 'uz';
    notifyListeners();
  }

  Future<void> setLanguage(String lang) async {
    if (['uz', 'en', 'ru'].contains(lang)) {
      _currentLang = lang;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('language', lang);
      notifyListeners();
    }
  }

  static const Map<String, Map<String, String>> _localizedValues = {
    'uz': {
      'current_month': '📊 Joriy oy',
      'income': 'Kirim',
      'expense': 'Chiqim',
      'result': 'Natija',
      'trend_12_months': '📈 12 oylik trend',
      'expenses': '💸 Harajatlar',
      'incomes': '💰 Kirimlar',
      'expenses_distribution': '💸 Harajatlar taqsimoti',
      'incomes_distribution': '💰 Kirimlar taqsimoti',
      'select_date': 'Sanani tanlang',
      'show': 'Ko‘rsat',
      'add_transaction': '➕ Bitim qo‘shish',
      'type': 'Turi',
      'amount': 'Summa',
      'source_category': 'Manba / Kategoriya',
      'note': 'Qo‘shimcha ma‘lumot',
      'date': 'Sana',
      'save': 'Saqlash',
      'cancel': 'Bekor qilish',
      'settings': '⚙️ Sozlamalar',
      'language': 'Til',
      'currency': 'Valyuta',
      'recent_transactions': '📋 So‘nggi operatsiyalar',
      'success_add': 'Muvaffaqiyatli qo‘shildi',
      'please_fill': 'Iltimos, barcha maydonlarni to‘ldiring',
      'from_date': 'Dan',
      'to_date': 'Gacha',
    },
    'en': {
      'current_month': '📊 Current Month',
      'income': 'Income',
      'expense': 'Expense',
      'result': 'Result',
      'trend_12_months': '📈 12 Month Trend',
      'expenses': '💸 Expenses',
      'incomes': '💰 Incomes',
      'expenses_distribution': '💸 Expenses Distribution',
      'incomes_distribution': '💰 Incomes Distribution',
      'select_date': 'Select Date',
      'show': 'Show',
      'add_transaction': '➕ Add Transaction',
      'type': 'Type',
      'amount': 'Amount',
      'source_category': 'Source / Category',
      'note': 'Additional Info',
      'date': 'Date',
      'save': 'Save',
      'cancel': 'Cancel',
      'settings': '⚙️ Settings',
      'language': 'Language',
      'currency': 'Currency',
      'recent_transactions': '📋 Recent Transactions',
      'success_add': 'Successfully added',
      'please_fill': 'Please fill all required fields',
      'from_date': 'From',
      'to_date': 'To',
    },
    'ru': {
      'current_month': '📊 Текущий месяц',
      'income': 'Доход',
      'expense': 'Расход',
      'result': 'Итог',
      'trend_12_months': '📈 12-месячный тренд',
      'expenses': '💸 Расходы',
      'incomes': '💰 Доходы',
      'expenses_distribution': '💸 Распределение расходов',
      'incomes_distribution': '💰 Распределение доходов',
      'select_date': 'Выберите дату',
      'show': 'Показать',
      'add_transaction': '➕ Добавить транзакцию',
      'type': 'Тип',
      'amount': 'Сумма',
      'source_category': 'Источник / Категория',
      'note': 'Дополнительная информация',
      'date': 'Дата',
      'save': 'Сохранить',
      'cancel': 'Отмена',
      'settings': '⚙️ Настройки',
      'language': 'Язык',
      'currency': 'Валюта',
      'recent_transactions': '📋 Последние операции',
      'success_add': 'Успешно добавлено',
      'please_fill': 'Пожалуйста, заполните все обязательные поля',
      'from_date': 'С',
      'to_date': 'По',
    },
  };

  String translate(String key) {
    return _localizedValues[_currentLang]?[key] ?? key;
  }
}
