from database.db_query import db
import asyncio

async def add_incomes_expenses():
    await db.connect()
    await db.create_tables()
    await db.add_new_user(user_id=7583610226, fullname='Javlon', sex='male', status='student', language='en', currency='uzs')

    earnings = [
        {
            "id": 1,
            "user_id": 7583610226,
            "amount": 110000.00,
            "currency": "uzs",
            "source": "refund",
            "comment": "My bro gave me his loan",
            "inserted_at": "2026-01-28 11:49:34.018989"
        },
        {
            "id": 2,
            "user_id": 7583610226,
            "amount": 30000.00,
            "currency": "uzs",
            "source": "gift",
            "comment": "From my sister",
            "inserted_at": "2026-01-31 21:32:03.917573"
        },
        {
            "id": 3,
            "user_id": 7583610226,
            "amount": 300000.00,
            "currency": "rub",
            "source": "investment",
            "comment": None,
            "inserted_at": "2026-02-02 03:25:42.335602"
        }
    ]

    expenses = [
        {
            "id": 1,
            "user_id": 7583610226,
            "amount": 120000.00,
            "currency": "uzs",
            "source": "food",
            "comment": None,
            "inserted_at": "2026-01-29 20:03:03.593497"
        },
        {
            "id": 2,
            "user_id": 7583610226,
            "amount": 121000.00,
            "currency": "uzs",
            "source": "utilities",
            "comment": "Expense saved successfully.",
            "inserted_at": "2026-01-29 20:07:21.412597"
        },
        {
            "id": 3,
            "user_id": 7583610226,
            "amount": 1234.00,
            "currency": "uzs",
            "source": "loans",
            "comment": None,
            "inserted_at": "2026-01-29 20:18:04.093858"
        },
        {
            "id": 4,
            "user_id": 7583610226,
            "amount": 100.00,
            "currency": "uzs",
            "source": "food",
            "comment": "Testing additional info",
            "inserted_at": "2026-01-31 21:04:10.568448"
        },
        {
            "id": 5,
            "user_id": 7583610226,
            "amount": 25000.00,
            "currency": "rub",
            "source": "housing",
            "comment": None,
            "inserted_at": "2026-02-02 03:25:57.834819"
        }
    ]
    for income in earnings:
        await db.add_income(user_id=income['user_id'],
                            amount=income['amount'],
                            currency=income['currency'],
                            source=income['source'],
                            additional_info=income['comment'])

    for expense in expenses:
        await db.add_expense(user_id=expense['user_id'],
                            amount=expense['amount'],
                            currency=expense['currency'],
                            source=expense['source'],
                            additional_info=expense['comment'])


asyncio.run(add_incomes_expenses())

