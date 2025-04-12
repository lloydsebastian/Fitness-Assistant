from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from src.utils import helpers, keyboards
from src.database.db_connector import Database

async def workout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Database()
    user = db.get_user(update.effective_user.id)
    
    if not user:
        await update.message.reply_text("Please create a plan first with /start")
        return
    
    current_day = helpers.get_current_day(update.effective_user.id)
    routine = user[6].split("\n\n")[current_day-1]
    
    await update.message.reply_text(
        f"Day {current_day} Workout:\n\n{routine}",
        reply_markup=InlineKeyboardMarkup(keyboards.progress_keyboard(current_day))
    )

async def track_completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    day = int(query.data.split("_")[1])
    db = Database()
    db.update_user(
        query.from_user.id,
        progress=f"Day {day} completed\n"
    )
    
    await query.edit_message_text(f"✅ Day {day} marked complete! Great job!")

workout_handler = CommandHandler('workout', workout_handler)
tracking_handler = CallbackQueryHandler(track_completion, pattern='^complete_')