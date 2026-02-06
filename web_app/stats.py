from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .web_database import get_db
from datetime import date, timedelta
from typing import Annotated

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/summary/{telegram_id}")
async def monthly_summary(telegram_id: int, db: AsyncSession = Depends(get_db)):
    q = text("""
        SELECT
            (SELECT COALESCE(SUM(amount),0)
             FROM user_earnings
             WHERE user_id=:uid
               AND inserted_at >= date_trunc('month', now())) AS income,
            (SELECT COALESCE(SUM(amount),0)
             FROM user_expenses
             WHERE user_id=:uid
               AND inserted_at >= date_trunc('month', now())) AS expense
    """)
    r = (await db.execute(q, {"uid": telegram_id})).first()

    return {
        "income": float(r.income),
        "expense": float(r.expense),
        "result": float(r.income - r.expense)
    }

@router.get("/trend/{telegram_id}")
async def trend(telegram_id: int, db: AsyncSession = Depends(get_db)):
    q = text("""
        SELECT
            to_char(m,'Mon') AS month,
            (SELECT COALESCE(SUM(amount), 0)
             FROM user_earnings
             WHERE date_trunc('month', inserted_at) = m
               AND user_id = :uid)::FLOAT AS income,
            (SELECT COALESCE(SUM(amount), 0)
             FROM user_expenses
             WHERE date_trunc('month', inserted_at) = m
               AND user_id = :uid)::FLOAT AS expense
        FROM generate_series(
            date_trunc('month', now()) - interval '11 months',
            date_trunc('month', now()),
            interval '1 month'
        ) m
        ORDER BY m
    """)
    rows = (await db.execute(q, {"uid": telegram_id})).mappings().all()
    return rows

@router.get("/expenses-pie/{telegram_id}")
async def expenses_pie(
        telegram_id: int,
        date_from: date,
        date_to: date,
        db: AsyncSession = Depends(get_db)
):
    dt_plus_one = date_to + timedelta(days=1)
    q = text("""
        SELECT source, SUM(amount)::FLOAT total
        FROM user_expenses
        WHERE user_id = :uid
          AND inserted_at >= :df
          AND inserted_at < :dt
        GROUP BY source
        ORDER BY total DESC
    """)
    rows = (await db.execute(q, {
        "uid": telegram_id,
        "df": date_from,
        "dt": dt_plus_one
    })).mappings().all()
    return rows

@router.get("/weekly/{telegram_id}")
async def weekly_stats(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    dt_plus_one = date_to + timedelta(days=1)

    # DOW: 0 is Sunday, 1 is Monday, ..., 6 is Saturday
    # We want to return them in order starting from Monday (1)
    q = text(f"""
        SELECT
            CASE dow
                WHEN 0 THEN 'Yak' WHEN 1 THEN 'Dush' WHEN 2 THEN 'Sesh'
                WHEN 3 THEN 'Chor' WHEN 4 THEN 'Pay' WHEN 5 THEN 'Jum' WHEN 6 THEN 'Shan'
            END as day,
            (SELECT COALESCE(SUM(amount), 0)
             FROM {table}
             WHERE user_id = :uid
               AND inserted_at >= :df AND inserted_at < :dt
               AND EXTRACT(DOW FROM inserted_at) = dow)::FLOAT as total
        FROM generate_series(0, 6) as dow
        ORDER BY (dow + 6) % 7
    """)
    rows = (await db.execute(q, {
        "uid": telegram_id,
        "df": date_from,
        "dt": dt_plus_one
    })).mappings().all()
    return rows

@router.get("/daily/{telegram_id}")
async def daily_stats(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    q = text(f"""
        SELECT
            gs.day::date as day,
            (SELECT COALESCE(SUM(amount), 0)
             FROM {table}
             WHERE inserted_at::date = gs.day::date
               AND user_id = :uid)::FLOAT as total
        FROM generate_series(CAST(:df AS timestamp), CAST(:dt AS timestamp), interval '1 day') AS gs(day)
        ORDER BY gs.day
    """)
    rows = (await db.execute(q, {"uid": telegram_id, "df": date_from, "dt": date_to})).mappings().all()
    return rows

@router.get("/metrics/{telegram_id}")
async def metrics(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    dt_plus_one = date_to + timedelta(days=1)
    q = text(f"""
        SELECT
            COALESCE(AVG(amount), 0) as average,
            COUNT(*) as count,
            COALESCE(MAX(amount), 0) as max_val,
            COALESCE(SUM(amount), 0) as total
        FROM {table}
        WHERE user_id = :uid AND inserted_at >= :df AND inserted_at < :dt
    """)
    r = (await db.execute(q, {"uid": telegram_id, "df": date_from, "dt": dt_plus_one})).mappings().first()
    return {
        "average": float(r.average),
        "count": int(r.count),
        "max": float(r.max_val),
        "total": float(r.total)
    }

@router.get("/income-pie/{telegram_id}")
async def income_pie(
        telegram_id: int,
        date_from: date,
        date_to: date,
        db: AsyncSession = Depends(get_db)
):
    dt_plus_one = date_to + timedelta(days=1)
    q = text("""
        SELECT source, SUM(amount)::FLOAT total
        FROM user_earnings
        WHERE user_id = :uid
          AND inserted_at >= :df
          AND inserted_at < :dt
        GROUP BY source
        ORDER BY total DESC
    """)
    rows = (await db.execute(q, {
        "uid": telegram_id,
        "df": date_from,
        "dt": dt_plus_one
    })).mappings().all()
    return rows
