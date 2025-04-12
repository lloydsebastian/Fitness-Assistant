from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    filters,
    CallbackQueryHandler
)
from src.utils import keyboards, helpers
from src.ai.model_handler import FitnessModel

# Conversation states
AGE, SEX, HEIGHT, WEIGHT, GOAL = range(5)
model = FitnessModel()

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Let's create your fitness plan!\nHow old are you?",
        reply_markup=InlineKeyboardMarkup(keyboards.cancel_keyboard)
    )
    return AGE

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text
    if not age.isdigit() or not 12 <= int(age) <= 100:
        await update.message.reply_text("Please enter a valid age (12-100)")
        return AGE
    context.user_data['age'] = age
    await update.message.reply_text(
        "Select your gender:",
        reply_markup=InlineKeyboardMarkup(keyboards.sex_keyboard)
    )
    return SEX

async def handle_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['sex'] = query.data
    await query.edit_message_text("Enter your height in cm:")
    return HEIGHT

async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    height = update.message.text
    if not height.isdigit() or not 100 <= int(height) <= 250:
        await update.message.reply_text("Please enter valid height (100-250 cm)")
        return HEIGHT
    context.user_data['height'] = height
    await update.message.reply_text("Enter your weight in kg:")
    return WEIGHT

async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weight = update.message.text
    if not weight.isdigit() or not 30 <= int(weight) <= 300:
        await update.message.reply_text("Please enter valid weight (30-300 kg)")
        return WEIGHT
    context.user_data['weight'] = weight
    await update.message.reply_text(
        "Choose your primary goal:",
        reply_markup=InlineKeyboardMarkup(keyboards.goal_keyboard)
    )
    return GOAL

@helpers.handle_async_errors
async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['goal'] = query.data
    
    # Generate workout plan
    plan = model.generate_plan(context.user_data)
    
    # Save to database
    db = Database()
    db.update_user(
        update.effective_user.id,
        age=context.user_data['age'],
        sex=context.user_data['sex'],
        height=context.user_data['height'],
        weight=context.user_data['weight'],
        goal=context.user_data['goal'],
        routine=plan,
        start_date=datetime.now().isoformat()
    )
    
    await query.edit_message_text(
        f"🏋️ Your Custom Plan:\n\n{plan}\n\nUse /workout to start!"
    )
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_conversation)],
    states={
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age)],
        SEX: [CallbackQueryHandler(handle_sex)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weight)],
        GOAL: [CallbackQueryHandler(handle_goal)]
    },
    fallbacks=[CommandHandler('cancel', commands.cancel)]
)