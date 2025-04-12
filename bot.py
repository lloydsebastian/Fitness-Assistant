import logging
import torch
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states.
AGE, SEX, HEIGHT, WEIGHT, GOAL, CONFIRMATION = range(6)

# Conversation handler functions remain the same.
def start(update, context):
    update.message.reply_text(
        "Hi, I'm your personal fitness assistant bot! I'll ask you a few questions so I can create a custom exercise plan for you.\n\nWhat's your age?"
    )
    return AGE

def age_handler(update, context):
    context.user_data['age'] = update.message.text
    update.message.reply_text("Great! Next, please tell me your sex (male/female).")
    return SEX

def sex_handler(update, context):
    context.user_data['sex'] = update.message.text
    update.message.reply_text("How tall are you in centimeters? (e.g., 170)")
    return HEIGHT

def height_handler(update, context):
    context.user_data['height'] = update.message.text
    update.message.reply_text("And your weight in kilograms? (e.g., 70)")
    return WEIGHT

def weight_handler(update, context):
    context.user_data['weight'] = update.message.text
    update.message.reply_text("What is your fitness goal? (options: weight loss / muscle gain / maintenance)")
    return GOAL

def goal_handler(update, context):
    context.user_data['goal'] = update.message.text
    summary = (
        f"Age: {context.user_data['age']}\n"
        f"Sex: {context.user_data['sex']}\n"
        f"Height: {context.user_data['height']} cm\n"
        f"Weight: {context.user_data['weight']} kg\n"
        f"Goal: {context.user_data['goal']}\n"
    )
    update.message.reply_text(
        "Please confirm the following details:\n\n" + summary +
        "\nReply with 'yes' to confirm or 'no' to restart."
    )
    return CONFIRMATION

# Load the specialized fitness trainer model.
MODEL_NAME = "Soorya03/Llama-3.2-1B-Instruct-FitnessAssistant"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_routine(user_data):
    prompt = (
        f"You are a professional fitness trainer. Create a clear, numbered exercise plan until the goal is achieved for a "
        f"{user_data['age']}-year-old {user_data['sex']} who is {user_data['height']} cm tall and weighs "
        f"{user_data['weight']} kg. The goal is {user_data['goal']}. Provide day-by-day numbered instructions. "
        "Include a disclaimer: 'This advice is for informational purposes only and is not a substitute for professional guidance.'"
    )
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    output_ids = model.generate(
        input_ids,
        max_length=300,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    routine = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return routine

def confirmation_handler(update, context):
    user_response = update.message.text.lower()
    if user_response == 'yes':
        routine = generate_routine(context.user_data)
        update.message.reply_text("Here is your personalized workout routine:\n\n" + routine)
        return ConversationHandler.END
    else:
        update.message.reply_text("Alright, let's try again. What is your age?")
        context.user_data.clear()  # Clear previous data.
        return AGE

def cancel(update, context):
    update.message.reply_text("Operation cancelled. Stay active, and feel free to come back anytime!")
    return ConversationHandler.END

# Export the ConversationHandler so we can add it in main.py.
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        AGE: [MessageHandler(Filters.text & ~Filters.command, age_handler)],
        SEX: [MessageHandler(Filters.text & ~Filters.command, sex_handler)],
        HEIGHT: [MessageHandler(Filters.text & ~Filters.command, height_handler)],
        WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight_handler)],
        GOAL: [MessageHandler(Filters.text & ~Filters.command, goal_handler)],
        CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), confirmation_handler)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)