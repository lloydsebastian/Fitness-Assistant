import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from src.database.db_connector import Database
from src.handlers import commands, conversation, tracking

nest_asyncio.apply()
load_dotenv()

async def main():
    # Initialize database
    db = Database()
    db.create_tables()
    
    # Build application
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    # Add handlers
    application.add_handlers([
        commands.start_handler,
        commands.progress_handler,
        commands.cancel_handler,
        tracking.workout_handler,
        conversation.conv_handler
    ])
    
    # Start polling
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())