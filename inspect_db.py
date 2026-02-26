import asyncio
from sqlalchemy import create_engine, inspect
from database.db_setup import ASYNC_DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    engine = create_async_engine(ASYNC_DATABASE_URL)
    async with engine.connect() as conn:
        def get_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_tables)
        print(f"Tables: {tables}")

        for table in tables:
            def get_cols(connection):
                inspector = inspect(connection)
                return inspector.get_columns(table)
            columns = await conn.run_sync(get_cols)
            print(f"Table {table} columns: {[c['name'] for c in columns]}")

if __name__ == "__main__":
    asyncio.run(main())
