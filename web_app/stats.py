from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .web_database import get_db
from datetime import timedelta
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
            COALESCE(SUM(e.amount),0) AS income,
            COALESCE(SUM(x.amount),0) AS expense
        FROM generate_series(
            date_trunc('month', now())-interval '11 months',
            date_trunc('month', now()),
            interval '1 month'
        ) m
        LEFT JOIN user_earnings e
            ON date_trunc('month', e.inserted_at)=m
            AND e.user_id=:uid
        LEFT JOIN user_expenses x
            ON date_trunc('month', x.inserted_at)=m
            AND x.user_id=:uid
        GROUP BY m
        ORDER BY m
    """)
    rows = (await db.execute(q, {"uid": telegram_id})).mappings().all()
    return rows

from datetime import date
from fastapi import Query

@router.get("/expenses-pie/{telegram_id}")
async def expenses_pie(
        telegram_id: int,
        date_from: date = Query(...),
        date_to: date = Query(...),
        db: AsyncSession = Depends(get_db)
):
    # convert to datetime and add 1 day for upper bound
    dt_plus_one = date_to + timedelta(days=1)

    q = text("""
            SELECT source, SUM(amount) total
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
