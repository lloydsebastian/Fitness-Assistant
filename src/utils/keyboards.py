from telegram import InlineKeyboardButton

sex_keyboard = [
    [InlineKeyboardButton("Male", callback_data='male'),
     InlineKeyboardButton("Female", callback_data='female')]
]

goal_keyboard = [
    [InlineKeyboardButton("Weight Loss", callback_data='weight_loss')],
    [InlineKeyboardButton("Muscle Gain", callback_data='muscle_gain')],
    [InlineKeyboardButton("Maintenance", callback_data='maintenance')]
]

cancel_keyboard = [
    [InlineKeyboardButton("Cancel", callback_data='cancel')]
]

def progress_keyboard(day):
    return [[InlineKeyboardButton(f"Day {day} ✅", callback_data=f'complete_{day}')]]