import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import 'database.dart';
import 'localization.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final localization = AppLocalization();
  await localization.init();

  runApp(
    ChangeNotifierProvider<AppLocalization>.value(
      value: localization,
      child: const FinanceTrackerApp(),
    ),
  );
}

class FinanceTrackerApp extends StatelessWidget {
  const FinanceTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppLocalization>(
      builder: (context, loc, child) {
        return MaterialApp(
          title: 'Finance Tracker',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            scaffoldBackgroundColor: const Color(0xFFF5F6FA),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF3498DB),
              primary: const Color(0xFF3498DB),
            ),
            useMaterial3: true,
          ),
          home: const MainHomeScreen(),
        );
      },
    );
  }
}

class MainHomeScreen extends StatefulWidget {
  const MainHomeScreen({super.key});

  @override
  State<MainHomeScreen> createState() => _MainHomeScreenState();
}

class _MainHomeScreenState extends State<MainHomeScreen> {
  int _selectedIndex = 0;

  double _income = 0.0;
  double _expense = 0.0;
  double _result = 0.0;

  List<Map<String, dynamic>> _trendData = [];
  List<Map<String, dynamic>> _pieData = [];
  List<Map<String, dynamic>> _recentTransactions = [];

  String _pieType = 'expenses'; // 'expenses' or 'income'
  DateTime _fromDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _toDate = DateTime.now();

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final db = DatabaseHelper.instance;

    final summary = await db.getMonthlySummary();
    final trend = await db.get12MonthTrend();
    final recent = await db.getRecentTransactions();

    List<Map<String, dynamic>> pie;
    if (_pieType == 'expenses') {
      pie = await db.getExpensesPie(dateFrom: _fromDate, dateTo: _toDate);
    } else {
      pie = await db.getIncomePie(dateFrom: _fromDate, dateTo: _toDate);
    }

    setState(() {
      _income = summary['income'] ?? 0.0;
      _expense = summary['expense'] ?? 0.0;
      _result = summary['result'] ?? 0.0;
      _trendData = trend;
      _pieData = pie;
      _recentTransactions = recent;
      _isLoading = false;
    });
  }

  void _showAddTransactionModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AddTransactionSheet(onSaved: _loadData),
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = Provider.of<AppLocalization>(context);

    final List<Widget> pages = [
      _buildDashboardView(loc),
      _buildTransactionsView(loc),
      _buildSettingsView(loc),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.translate('current_month').replaceAll('📊 ', ''),
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showAddTransactionModal,
            tooltip: loc.translate('add_transaction'),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: IndexedStack(
                index: _selectedIndex,
                children: pages,
              ),
            ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        activeColor: const Color(0xFF3498DB),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard_outlined),
            activeIcon: const Icon(Icons.dashboard),
            label: loc.translate('current_month').replaceAll('📊 ', ''),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.receipt_long_outlined),
            activeIcon: const Icon(Icons.receipt_long),
            label: loc.translate('recent_transactions').replaceAll('📋 ', ''),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings_outlined),
            activeIcon: const Icon(Icons.settings),
            label: loc.translate('settings').replaceAll('⚙️ ', ''),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddTransactionModal,
        backgroundColor: const Color(0xFF3498DB),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildDashboardView(AppLocalization loc) {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            loc.translate('current_month'),
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          // Cards Row / Wrap
          Row(
            children: [
              Expanded(
                child: _buildSummaryCard(
                  title: loc.translate('income'),
                  amount: '+\$${_income.toStringAsFixed(2)}',
                  color: const Color(0xFF2ECC71),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSummaryCard(
                  title: loc.translate('expense'),
                  amount: '-\$${_expense.toStringAsFixed(2)}',
                  color: const Color(0xFFE74C3C),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSummaryCard(
                  title: loc.translate('result'),
                  amount: '${_result >= 0 ? "+" : "-"}\$${_result.abs().toStringAsFixed(2)}',
                  color: const Color(0xFF3498DB),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),
          Text(
            loc.translate('trend_12_months'),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          // 12 Month Trend Chart Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: SizedBox(
                height: 200,
                child: _buildTrendChart(),
              ),
            ),
          ),

          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 12),

          // Navigation buttons (Expenses / Incomes)
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _pieType == 'expenses' ? const Color(0xFF3498DB) : Colors.grey[200],
                  foregroundColor: _pieType == 'expenses' ? Colors.white : Colors.black87,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  setState(() => _pieType = 'expenses');
                  _loadData();
                },
                child: Text(loc.translate('expenses')),
              ),
              const SizedBox(width: 12),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _pieType == 'income' ? const Color(0xFF3498DB) : Colors.grey[200],
                  foregroundColor: _pieType == 'income' ? Colors.white : Colors.black87,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  setState(() => _pieType = 'income');
                  _loadData();
                },
                child: Text(loc.translate('incomes')),
              ),
            ],
          ),

          const SizedBox(height: 16),
          Text(
            _pieType == 'expenses' ? loc.translate('expenses_distribution') : loc.translate('incomes_distribution'),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          // Date Filters Row
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _fromDate,
                      firstDate: DateTime(2020),
                      lastDate: DateTime.now(),
                    );
                    if (picked != null) {
                      setState(() => _fromDate = picked);
                    }
                  },
                  child: Text('${loc.translate('from_date')}: ${DateFormat('yyyy-MM-dd').format(_fromDate)}'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton(
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _toDate,
                      firstDate: DateTime(2020),
                      lastDate: DateTime.now(),
                    );
                    if (picked != null) {
                      setState(() => _toDate = picked);
                    }
                  },
                  child: Text('${loc.translate('to_date')}: ${DateFormat('yyyy-MM-dd').format(_toDate)}'),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _loadData,
                child: Text(loc.translate('show')),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Pie Chart & List
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: _pieData.isEmpty
                  ? const Center(child: Padding(padding: EdgeInsets.all(20), child: Text("No data")))
                  : Column(
                      children: [
                        SizedBox(
                          height: 180,
                          child: _buildPieChart(),
                        ),
                        const SizedBox(height: 16),
                        ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: _pieData.length,
                          itemBuilder: (context, index) {
                            final item = _pieData[index];
                            return ListTile(
                              dense: true,
                              title: Text(item['source'].toString()),
                              trailing: Text(
                                '\$${(item['total'] as num).toStringAsFixed(2)}',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildSummaryCard({required String title, required String amount, required Color color}) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        children: [
          Text(title, style: const TextStyle(color: Colors.white, fontSize: 13)),
          const SizedBox(height: 6),
          FittedBox(
            child: Text(
              amount,
              style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrendChart() {
    if (_trendData.isEmpty) return const SizedBox();

    List<FlSpot> incomeSpots = [];
    List<FlSpot> expenseSpots = [];

    for (int i = 0; i < _trendData.length; i++) {
      incomeSpots.add(FlSpot(i.toDouble(), (_trendData[i]['income'] as num).toDouble()));
      expenseSpots.add(FlSpot(i.toDouble(), (_trendData[i]['expense'] as num).toDouble()));
    }

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                int index = value.toInt();
                if (index >= 0 && index < _trendData.length && index % 2 == 0) {
                  return Text(_trendData[index]['month'], style: const TextStyle(fontSize: 10));
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: incomeSpots,
            isCurved: true,
            color: const Color(0xFF2ECC71),
            barWidth: 3,
            dotData: const FlDotData(show: false),
          ),
          LineChartBarData(
            spots: expenseSpots,
            isCurved: true,
            color: const Color(0xFFE74C3C),
            barWidth: 3,
            dotData: const FlDotData(show: false),
          ),
        ],
      ),
    );
  }

  Widget _buildPieChart() {
    List<PieChartSectionData> sections = [];
    final colors = [
      const Color(0xFF2ECC71),
      const Color(0xFFE74C3C),
      const Color(0xFF3498DB),
      const Color(0xFFF1C40F),
      const Color(0xFF9B59B6),
      const Color(0xFFE67E22),
    ];

    for (int i = 0; i < _pieData.length; i++) {
      final item = _pieData[i];
      final double val = (item['total'] as num).toDouble();
      sections.add(
        PieChartSectionData(
          value: val,
          title: item['source'].toString(),
          color: colors[i % colors.length],
          radius: 50,
          titleStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white),
        ),
      );
    }

    return PieChart(PieChartData(sections: sections, centerSpaceRadius: 30));
  }

  Widget _buildTransactionsView(AppLocalization loc) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _recentTransactions.length,
      itemBuilder: (context, index) {
        final tx = _recentTransactions[index];
        final bool isIncome = tx['type'] == 'income';
        final DateTime dt = DateTime.parse(tx['inserted_at']);

        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isIncome ? const Color(0xFF2ECC71) : const Color(0xFFE74C3C),
              child: Icon(
                isIncome ? Icons.arrow_downward : Icons.arrow_upward,
                color: Colors.white,
              ),
            ),
            title: Text(tx['source'] ?? 'General', style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text('${DateFormat('yyyy-MM-dd HH:mm').format(dt)}${tx['additional_info'] != null && tx['additional_info'].toString().isNotEmpty ? ' • ${tx['additional_info']}' : ''}'),
            trailing: Text(
              '${isIncome ? '+' : '-'}\$${(tx['amount'] as num).toStringAsFixed(2)}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: isIncome ? const Color(0xFF2ECC71) : const Color(0xFFE74C3C),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSettingsView(AppLocalization loc) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(loc.translate('settings'), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const Divider(),
              ListTile(
                title: Text(loc.translate('language')),
                trailing: DropdownButton<String>(
                  value: loc.currentLang,
                  items: const [
                    DropdownMenuItem(value: 'uz', child: Text('O‘zbekcha')),
                    DropdownMenuItem(value: 'en', child: Text('English')),
                    DropdownMenuItem(value: 'ru', child: Text('Русский')),
                  ],
                  onChanged: (val) {
                    if (val != null) loc.setLanguage(val);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AddTransactionSheet extends StatefulWidget {
  final VoidCallback onSaved;
  const AddTransactionSheet({super.key, required onSaved}) : onSaved = onSaved;

  @override
  State<AddTransactionSheet> createState() => _AddTransactionSheetState();
}

class _AddTransactionSheetState extends State<AddTransactionSheet> {
  String _type = 'income'; // 'income' or 'expense'
  final _amountController = TextEditingController();
  final _sourceController = TextEditingController();
  final _infoController = TextEditingController();
  String _currency = 'usd';
  DateTime _selectedDate = DateTime.now();

  bool _isSaving = false;

  void _save() async {
    final loc = Provider.of<AppLocalization>(context, listen: false);
    final amountText = _amountController.text.trim();
    final sourceText = _sourceController.text.trim();

    if (amountText.isEmpty || sourceText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(loc.translate('please_fill'))),
      );
      return;
    }

    final double? amount = double.tryParse(amountText);
    if (amount == null || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Enter a valid amount")),
      );
      return;
    }

    setState(() => _isSaving = true);
    final db = DatabaseHelper.instance;

    if (_type == 'income') {
      await db.insertEarning(
        amount: amount,
        source: sourceText,
        currency: _currency,
        additionalInfo: _infoController.text.trim().isEmpty ? null : _infoController.text.trim(),
        date: _selectedDate,
      );
    } else {
      await db.insertExpense(
        amount: amount,
        source: sourceText,
        currency: _currency,
        additionalInfo: _infoController.text.trim().isEmpty ? null : _infoController.text.trim(),
        date: _selectedDate,
      );
    }

    setState(() => _isSaving = false);
    if (mounted) {
      widget.onSaved();
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(loc.translate('success_add'))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = Provider.of<AppLocalization>(context);

    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
        top: 20,
        left: 20,
        right: 20,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              loc.translate('add_transaction'),
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Toggle Income / Expense
            Row(
              children: [
                Expanded(
                  child: ChoiceChip(
                    label: Center(child: Text(loc.translate('income'))),
                    selected: _type == 'income',
                    selectedColor: const Color(0xFF2ECC71),
                    labelStyle: TextStyle(color: _type == 'income' ? Colors.white : Colors.black87),
                    onSelected: (val) {
                      if (val) setState(() => _type = 'income');
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ChoiceChip(
                    label: Center(child: Text(loc.translate('expense'))),
                    selected: _type == 'expense',
                    selectedColor: const Color(0xFFE74C3C),
                    labelStyle: TextStyle(color: _type == 'expense' ? Colors.white : Colors.black87),
                    onSelected: (val) {
                      if (val) setState(() => _type = 'expense');
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _amountController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: loc.translate('amount'),
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.attach_money),
              ),
            ),
            const SizedBox(height: 12),

            TextField(
              controller: _sourceController,
              decoration: InputDecoration(
                labelText: loc.translate('source_category'),
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.category),
              ),
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _currency,
                    decoration: InputDecoration(
                      labelText: loc.translate('currency'),
                      border: const OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'usd', child: Text('USD (\$)')),
                      DropdownMenuItem(value: 'eur', child: Text('EUR (€)')),
                      DropdownMenuItem(value: 'uzs', child: Text('UZS (So\'m)')),
                      DropdownMenuItem(value: 'rub', child: Text('RUB (₽)')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _currency = val);
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    icon: const Icon(Icons.calendar_today),
                    label: Text(DateFormat('yyyy-MM-dd').format(_selectedDate)),
                    onPressed: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: _selectedDate,
                        firstDate: DateTime(2020),
                        lastDate: DateTime.now(),
                      );
                      if (picked != null) {
                        setState(() => _selectedDate = picked);
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            TextField(
              controller: _infoController,
              decoration: InputDecoration(
                labelText: loc.translate('note'),
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.note),
              ),
            ),
            const SizedBox(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(loc.translate('cancel')),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF3498DB),
                    foregroundColor: Colors.white,
                  ),
                  onPressed: _isSaving ? null : _save,
                  child: _isSaving
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(loc.translate('save')),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
