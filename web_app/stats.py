from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .web_database import get_db
from datetime import date, timedelta
from typing import Annotated, Optional
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from .bot.engine import bot
from aiogram.types import BufferedInputFile

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/summary/{telegram_id}")
async def monthly_summary(telegram_id: int, db: AsyncSession = Depends(get_db)):
    q = text("""
        SELECT
            (SELECT COALESCE(SUM(amount),0) FROM user_earnings WHERE user_id=:uid AND inserted_at >= date_trunc('month', now())) AS income,
            (SELECT COALESCE(SUM(amount),0) FROM user_earnings WHERE user_id=:uid AND inserted_at >= date_trunc('month', now()) AND payment_method='cash') AS income_cash,
            (SELECT COALESCE(SUM(amount),0) FROM user_earnings WHERE user_id=:uid AND inserted_at >= date_trunc('month', now()) AND payment_method='card') AS income_card,
            (SELECT COALESCE(SUM(amount),0) FROM user_expenses WHERE user_id=:uid AND inserted_at >= date_trunc('month', now())) AS expense,
            (SELECT COALESCE(SUM(amount),0) FROM user_expenses WHERE user_id=:uid AND inserted_at >= date_trunc('month', now()) AND payment_method='cash') AS expense_cash,
            (SELECT COALESCE(SUM(amount),0) FROM user_expenses WHERE user_id=:uid AND inserted_at >= date_trunc('month', now()) AND payment_method='card') AS expense_card
    """)
    r = (await db.execute(q, {"uid": telegram_id})).mappings().first()

    return {
        "income": float(r['income']),
        "income_cash": float(r['income_cash']),
        "income_card": float(r['income_card']),
        "expense": float(r['expense']),
        "expense_cash": float(r['expense_cash']),
        "expense_card": float(r['expense_card']),
        "result": float(r['income'] - r['expense'])
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

@router.get("/monitoring/{telegram_id}")
async def monitoring(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    q = text(f"""
        SELECT
            (SELECT COALESCE(SUM(amount), 0) FROM {table} WHERE user_id = :uid AND inserted_at::date = now()::date)::FLOAT as total,
            (SELECT COALESCE(SUM(amount), 0) FROM {table} WHERE user_id = :uid AND inserted_at::date = now()::date AND payment_method = 'cash')::FLOAT as cash,
            (SELECT COALESCE(SUM(amount), 0) FROM {table} WHERE user_id = :uid AND inserted_at::date = now()::date AND payment_method = 'card')::FLOAT as card
    """)
    summary = (await db.execute(q, {"uid": telegram_id})).mappings().first()

    q_cat = text(f"""
        SELECT source, SUM(amount)::FLOAT total
        FROM {table}
        WHERE user_id = :uid AND inserted_at::date = now()::date
        GROUP BY source
        ORDER BY total DESC
    """)
    categories = (await db.execute(q_cat, {"uid": telegram_id})).mappings().all()

    return {
        "summary": dict(summary) if summary else None,
        "categories": [dict(c) for c in categories]
    }

@router.get("/report/{telegram_id}")
async def report(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    date_from: date,
    date_to: date,
    source: Optional[str] = None,
    payment_method: Optional[str] = None,
    sort_by: str = "inserted_at",
    order: str = "DESC",
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    dt_plus_one = date_to + timedelta(days=1)

    conditions = ["user_id = :uid", "inserted_at >= :df", "inserted_at < :dt"]
    params = {"uid": telegram_id, "df": date_from, "dt": dt_plus_one}

    if source:
        conditions.append("source = :source")
        params["source"] = source
    if payment_method:
        conditions.append("payment_method = :pm")
        params["pm"] = payment_method

    where_clause = " AND ".join(conditions)

    if sort_by not in ["inserted_at", "amount", "source", "payment_method"]:
        sort_by = "inserted_at"
    if order not in ["ASC", "DESC"]:
        order = "DESC"

    q = text(f"""
        SELECT id, amount::FLOAT, source, payment_method, additional_info, to_char(inserted_at, 'YYYY-MM-DD HH24:MI') as date
        FROM {table}
        WHERE {where_clause}
        ORDER BY {sort_by} {order}
    """)

    rows = (await db.execute(q, params)).mappings().all()
    return rows

@router.delete("/transaction/{telegram_id}/{type}/{transaction_id}")
async def delete_transaction(
    telegram_id: int,
    type: str,
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    q = text(f"DELETE FROM {table} WHERE id = :tid AND user_id = :uid")
    await db.execute(q, {"tid": transaction_id, "uid": telegram_id})
    await db.commit()
    return {"status": "success"}

@router.put("/transaction/{telegram_id}/{type}/{transaction_id}")
async def update_transaction(
    telegram_id: int,
    type: str,
    transaction_id: int,
    amount: float = Body(...),
    source: str = Body(...),
    payment_method: str = Body(...),
    additional_info: Optional[str] = Body(None),
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    q = text(f"""
        UPDATE {table}
        SET amount = :amount, source = :source, payment_method = :pm, additional_info = :info
        WHERE id = :tid AND user_id = :uid
    """)
    await db.execute(q, {
        "amount": amount,
        "source": source,
        "pm": payment_method,
        "info": additional_info,
        "tid": transaction_id,
        "uid": telegram_id
    })
    await db.commit()
    return {"status": "success"}

@router.get("/export/{telegram_id}")
async def export_excel(
    telegram_id: int,
    type: Annotated[str, Query(pattern="^(income|expenses)$")],
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db)
):
    table = "user_earnings" if type == "income" else "user_expenses"
    dt_plus_one = date_to + timedelta(days=1)

    q = text(f"""
        SELECT to_char(inserted_at, 'YYYY-MM-DD HH24:MI') as date, amount::FLOAT, source, payment_method, additional_info
        FROM {table}
        WHERE user_id = :uid AND inserted_at >= :df AND inserted_at < :dt
        ORDER BY inserted_at DESC
    """)
    rows = (await db.execute(q, {"uid": telegram_id, "df": date_from, "dt": dt_plus_one})).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No data found for the selected period")

    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hisobot"

    headers = ["Sana", "Summa", "Kategoriya", "To'lov usuli", "Izoh"]
    ws.append(headers)

    # Style headers
    header_fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        ws.append([row['date'], row['amount'], row['source'], row['payment_method'], row['additional_info']])

    # Auto-adjust columns width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    # Save to buffer
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    # Send via Bot
    filename = f"hisobot_{type}_{date_from}_{date_to}.xlsx"
    input_file = BufferedInputFile(excel_file.read(), filename=filename)

    try:
        await bot.send_document(chat_id=telegram_id, document=input_file, caption=f"📊 Sizning {date_from} dan {date_to} gacha bo'lgan {type} hisobotingiz.")
        return {"status": "success", "message": "Excel file sent to Telegram"}
    except Exception as e:
        print(f"Error sending document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send document: {str(e)}")

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
        "average": float(r['average']),
        "count": int(r['count']),
        "max": float(r['max_val']),
        "total": float(r['total'])
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
