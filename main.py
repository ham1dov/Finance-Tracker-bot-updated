import asyncio
import uvicorn
from web_app.engine import app
from web_app.bot.engine import start_bot
import os
async def main():
    asyncio.create_task(start_bot())

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
