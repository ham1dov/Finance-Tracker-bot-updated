import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db_setup import AsyncSessionLocal
from database.models import Catalog, Product, ProductStock, User, UserRoleMapping, UserRole
from decimal import Decimal

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Create a default admin if not exists
        from config import ADMIN_TELEGRAM_ID

        result = await session.execute(select(User).where(User.telegram_id == ADMIN_TELEGRAM_ID))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(telegram_id=ADMIN_TELEGRAM_ID, fullname="Admin User")
            session.add(admin)
            await session.flush()
            role = UserRoleMapping(user_id=ADMIN_TELEGRAM_ID, role=UserRole.admin)
            session.add(role)

        # 1. Create Categories
        drinks = Catalog(name="Ichimliklar", created_by=ADMIN_TELEGRAM_ID)
        food = Catalog(name="Taomlar", created_by=ADMIN_TELEGRAM_ID)
        session.add_all([drinks, food])
        await session.flush()

        coffee = Catalog(name="Kofe", father_id=drinks.id, created_by=ADMIN_TELEGRAM_ID)
        soda = Catalog(name="Gazli ichimliklar", father_id=drinks.id, created_by=ADMIN_TELEGRAM_ID)
        burger = Catalog(name="Burgerlar", father_id=food.id, created_by=ADMIN_TELEGRAM_ID)
        session.add_all([coffee, soda, burger])
        await session.flush()

        # 2. Create Products
        p1 = Product(name="Kapuchino", description="Klassik kapuchino", price=Decimal("25000"), catalog_id=coffee.id, created_by=ADMIN_TELEGRAM_ID)
        p2 = Product(name="Latte", description="Yumshoq kofe", price=Decimal("22000"), catalog_id=coffee.id, created_by=ADMIN_TELEGRAM_ID)
        p3 = Product(name="Amerikano", description="Qora kofe", price=Decimal("18000"), catalog_id=coffee.id, created_by=ADMIN_TELEGRAM_ID)

        p4 = Product(name="Chizburger", description="Go'shtli va pishloqli", price=Decimal("35000"), catalog_id=burger.id, created_by=ADMIN_TELEGRAM_ID)
        p5 = Product(name="Coca-Cola", description="0.5L", price=Decimal("10000"), catalog_id=soda.id, created_by=ADMIN_TELEGRAM_ID)

        session.add_all([p1, p2, p3, p4, p5])
        await session.flush()

        # 3. Add Stock
        s1 = ProductStock(product_id=p1.id, count=100)
        s2 = ProductStock(product_id=p2.id, count=100)
        s3 = ProductStock(product_id=p3.id, count=100)
        s4 = ProductStock(product_id=p4.id, count=50)
        s5 = ProductStock(product_id=p5.id, count=200)
        session.add_all([s1, s2, s3, s4, s5])

        await session.commit()
    print("Seed data created successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
