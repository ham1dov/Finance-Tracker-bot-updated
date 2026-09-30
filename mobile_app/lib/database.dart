import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('finance_tracker.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    if (!kIsWeb && (Platform.isLinux || Platform.isWindows || Platform.isMacOS)) {
      sqfliteFfiInit();
      databaseFactory = databaseFactoryFfi;
    }

    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future<void> _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE users(
        telegram_id INTEGER PRIMARY KEY,
        fullname TEXT,
        sex TEXT,
        social_status TEXT,
        language TEXT DEFAULT 'uz',
        currency TEXT DEFAULT 'usd',
        registered_at TEXT
      )
    ''');

    await db.execute('''
      CREATE TABLE user_earnings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'usd',
        source TEXT NOT NULL,
        additional_info TEXT,
        inserted_at TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE user_expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'usd',
        source TEXT NOT NULL,
        additional_info TEXT,
        inserted_at TEXT NOT NULL
      )
    ''');

    // Insert default local user
    await db.insert('users', {
      'telegram_id': 1,
      'fullname': 'Local User',
      'language': 'uz',
      'currency': 'usd',
      'registered_at': DateTime.now().toIso8601String(),
    });
  }

  // --- Earnings (Income) CRUD ---
  Future<int> insertEarning({
    required double amount,
    required String source,
    String currency = 'usd',
    String? additionalInfo,
    DateTime? date,
    int userId = 1,
  }) async {
    final db = await instance.database;
    final insertedAt = (date ?? DateTime.now()).toIso8601String();

    return await db.insert('user_earnings', {
      'user_id': userId,
      'amount': amount,
      'currency': currency,
      'source': source,
      'additional_info': additionalInfo,
      'inserted_at': insertedAt,
    });
  }

  // --- Expenses CRUD ---
  Future<int> insertExpense({
    required double amount,
    required String source,
    String currency = 'usd',
    String? additionalInfo,
    DateTime? date,
    int userId = 1,
  }) async {
    final db = await instance.database;
    final insertedAt = (date ?? DateTime.now()).toIso8601String();

    return await db.insert('user_expenses', {
      'user_id': userId,
      'amount': amount,
      'currency': currency,
      'source': source,
      'additional_info': additionalInfo,
      'inserted_at': insertedAt,
    });
  }

  // --- Summary (Current Month) ---
  Future<Map<String, double>> getMonthlySummary({int userId = 1}) async {
    final db = await instance.database;
    final now = DateTime.now();
    final startOfMonth = DateTime(now.year, now.month, 1).toIso8601String();

    final incomeRes = await db.rawQuery(
      'SELECT SUM(amount) as total FROM user_earnings WHERE user_id = ? AND inserted_at >= ?',
      [userId, startOfMonth],
    );

    final expenseRes = await db.rawQuery(
      'SELECT SUM(amount) as total FROM user_expenses WHERE user_id = ? AND inserted_at >= ?',
      [userId, startOfMonth],
    );

    double income = (incomeRes.first['total'] as num?)?.toDouble() ?? 0.0;
    double expense = (expenseRes.first['total'] as num?)?.toDouble() ?? 0.0;

    return {
      'income': income,
      'expense': expense,
      'result': income - expense,
    };
  }

  // --- 12 Month Trend ---
  Future<List<Map<String, dynamic>>> get12MonthTrend({int userId = 1}) async {
    final db = await instance.database;
    final now = DateTime.now();
    List<Map<String, dynamic>> result = [];

    final monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    for (int i = 11; i >= 0; i--) {
      DateTime monthStart = DateTime(now.year, now.month - i, 1);
      DateTime monthEnd = DateTime(now.year, now.month - i + 1, 1);

      String startStr = monthStart.toIso8601String();
      String endStr = monthEnd.toIso8601String();

      final incRes = await db.rawQuery(
        'SELECT SUM(amount) as total FROM user_earnings WHERE user_id = ? AND inserted_at >= ? AND inserted_at < ?',
        [userId, startStr, endStr],
      );

      final expRes = await db.rawQuery(
        'SELECT SUM(amount) as total FROM user_expenses WHERE user_id = ? AND inserted_at >= ? AND inserted_at < ?',
        [userId, startStr, endStr],
      );

      double income = (incRes.first['total'] as num?)?.toDouble() ?? 0.0;
      double expense = (expRes.first['total'] as num?)?.toDouble() ?? 0.0;

      result.add({
        'month': monthNames[monthStart.month - 1],
        'income': income,
        'expense': expense,
      });
    }

    return result;
  }

  // --- Pie Distribution ---
  Future<List<Map<String, dynamic>>> getExpensesPie({
    required DateTime dateFrom,
    required DateTime dateTo,
    int userId = 1,
  }) async {
    final db = await instance.database;
    String df = dateFrom.toIso8601String();
    String dt = dateTo.add(const Duration(days: 1)).toIso8601String();

    final rows = await db.rawQuery(
      'SELECT source, SUM(amount) as total FROM user_expenses WHERE user_id = ? AND inserted_at >= ? AND inserted_at < ? GROUP BY source ORDER BY total DESC',
      [userId, df, dt],
    );

    return rows;
  }

  Future<List<Map<String, dynamic>>> getIncomePie({
    required DateTime dateFrom,
    required DateTime dateTo,
    int userId = 1,
  }) async {
    final db = await instance.database;
    String df = dateFrom.toIso8601String();
    String dt = dateTo.add(const Duration(days: 1)).toIso8601String();

    final rows = await db.rawQuery(
      'SELECT source, SUM(amount) as total FROM user_earnings WHERE user_id = ? AND inserted_at >= ? AND inserted_at < ? GROUP BY source ORDER BY total DESC',
      [userId, df, dt],
    );

    return rows;
  }

  // --- Get Transactions List ---
  Future<List<Map<String, dynamic>>> getRecentTransactions({int userId = 1, int limit = 20}) async {
    final db = await instance.database;
    final earnings = await db.rawQuery(
      "SELECT id, amount, currency, source, additional_info, inserted_at, 'income' as type FROM user_earnings WHERE user_id = ?",
      [userId],
    );
    final expenses = await db.rawQuery(
      "SELECT id, amount, currency, source, additional_info, inserted_at, 'expense' as type FROM user_expenses WHERE user_id = ?",
      [userId],
    );

    List<Map<String, dynamic>> all = [...earnings, ...expenses];
    all.sort((a, b) => (b['inserted_at'] as String).compareTo(a['inserted_at'] as String));

    if (all.length > limit) {
      return all.sublist(0, limit);
    }
    return all;
  }
}
