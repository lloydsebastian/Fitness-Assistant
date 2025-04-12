from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from src.database.db_connector import Database

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Fitness Tracker! Use /newplan to get started."
    )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Database()
    user = db.get_user(update.effective_user.id)
    await update.message.reply_text(
        f"Your Progress:\n\n{user[7] or 'No progress tracked yet!'}"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

start_handler = CommandHandler('start', start)
progress_handler = CommandHandler('progress', progress)
cancel_handler = CommandHandler('cancel', cancel)