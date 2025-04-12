import logging
import torch
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging to help debug issues.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
AGE, SEX, HEIGHT, WEIGHT, GOAL, CONFIRMATION = range(6)

# Start conversation: ask for age
def start(update, context):
    update.message.reply_text(
        "Hi, I'm your personal fitness assistant bot! I'll ask you a few questions so I can create a custom exercise plan for you.\n\nWhat's your age?"
    )
    return AGE

# Collect Age
def age_handler(update, context):
    context.user_data['age'] = update.message.text
    update.message.reply_text("Great! Next, please tell me your sex (male/female).")
    return SEX

# Collect Sex
def sex_handler(update, context):
    context.user_data['sex'] = update.message.text
    update.message.reply_text("How tall are you in centimeters? (e.g., 170)")
    return HEIGHT

# Collect Height
def height_handler(update, context):
    context.user_data['height'] = update.message.text
    update.message.reply_text("And your weight in kilograms? (e.g., 70)")
    return WEIGHT

# Collect Weight
def weight_handler(update, context):
    context.user_data['weight'] = update.message.text
    update.message.reply_text("What is your fitness goal? (options: weight loss / muscle gain / maintenance)")
    return GOAL

# Collect Fitness Goal
def goal_handler(update, context):
    context.user_data['goal'] = update.message.text
    # Summarize the input received so far.
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

