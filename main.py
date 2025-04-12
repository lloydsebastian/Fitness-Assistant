import asyncio
from telegram.ext import ApplicationBuilder
from bot import conv_handler
import nest_asyncio
nest_asyncio.apply()

async def main():
    BOT_TOKEN = "REMOVED_SECRET"  # Replace with your token.
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(conv_handler)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())