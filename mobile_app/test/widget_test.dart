import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:mobile_app/database.dart';
import 'package:mobile_app/localization.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  group('Localization Tests', () {
    test('Translates keys correctly in Uzbek, English, and Russian', () async {
      SharedPreferences.setMockInitialValues({});
      final loc = AppLocalization();

      // Default uzbek
      expect(loc.translate('income'), equals('Kirim'));
      expect(loc.translate('expense'), equals('Chiqim'));

      // Switch to English
      await loc.setLanguage('en');
      expect(loc.translate('income'), equals('Income'));
      expect(loc.translate('expense'), equals('Expense'));

      // Switch to Russian
      await loc.setLanguage('ru');
      expect(loc.translate('income'), equals('Доход'));
      expect(loc.translate('expense'), equals('Расход'));
    });
  });

  group('Database Tests', () {
    test('Insert income and expense and check monthly summary', () async {
      final dbHelper = DatabaseHelper.instance;

      final initialSummary = await dbHelper.getMonthlySummary();
      final double startIncome = initialSummary['income'] ?? 0.0;
      final double startExpense = initialSummary['expense'] ?? 0.0;

      final earId = await dbHelper.insertEarning(
        amount: 500.0,
        source: 'Salary',
        currency: 'usd',
      );
      expect(earId, greaterThan(0));

      final expId = await dbHelper.insertExpense(
        amount: 150.0,
        source: 'Food',
        currency: 'usd',
      );
      expect(expId, greaterThan(0));

      final summary = await dbHelper.getMonthlySummary();
      expect(summary['income'], equals(startIncome + 500.0));
      expect(summary['expense'], equals(startExpense + 150.0));
      expect(summary['result'], equals((startIncome + 500.0) - (startExpense + 150.0)));

      final txs = await dbHelper.getRecentTransactions();
      expect(txs.length, greaterThanOrEqualTo(2));
    });
  });
}
