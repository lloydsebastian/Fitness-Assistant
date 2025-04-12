from functools import wraps
from telegram import Update
from datetime import datetime
from src.database.db_connector import Database
from telegram.ext import (
    ConversationHandler
)
def handle_async_errors(func):
    @wraps(func)
    async def wrapper(update: Update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            await update.effective_message.reply_text(
                f"⚠️ Error: {str(e)}\nPlease try again."
            )
            return ConversationHandler.END
    return wrapper

def get_current_day(user_id):
    # Calculate current workout day based on start date
    db = Database()
    user = db.get_user(user_id)
    start_date = datetime.fromisoformat(user[8])
    return (datetime.now() - start_date).days % 28 + 1