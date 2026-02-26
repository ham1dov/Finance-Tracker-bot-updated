from aiogram import Bot
from database.models import Order, ClientCart, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import ADMIN_TELEGRAM_ID

async def notify_admin_new_order(bot: Bot, order_id: int, db: AsyncSession):
    # Fetch order details
    result = await db.execute(
        select(Order, User)
        .join(ClientCart, Order.cart_id == ClientCart.id)
        .join(User, ClientCart.user_id == User.telegram_id)
        .where(Order.id == order_id)
    )
    row = result.fetchone()
    if not row:
        return

    order, user = row

    amount_str = "{:,.0f}".format(order.total_amount).replace(",", " ")

    msg = (
        f"🔔 <b>Yangi buyurtma!</b>\n\n"
        f"🆔 Buyurtma ID: #{order.id}\n"
        f"👤 Mijoz: {user.fullname}\n"
        f"💰 Umumiy summa: {amount_str} so'm\n"
        f"🕒 Vaqt: {order.created_at.strftime('%H:%M')}\n\n"
        f"Buyurtmani boshqarish uchun Admin panelga o'ting."
    )

    try:
        await bot.send_message(ADMIN_TELEGRAM_ID, msg, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to notify admin: {e}")
