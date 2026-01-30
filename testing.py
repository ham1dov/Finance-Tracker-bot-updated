from database.db_query import db

async def test_db():
    await db.connect()
    print(await db.get_all_users())

import asyncio
asyncio.run(test_db())