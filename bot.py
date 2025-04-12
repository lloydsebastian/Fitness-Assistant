import logging
import torch
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states.
AGE, SEX, HEIGHT, WEIGHT, GOAL, CONFIRMATION = range(6)

# Start conversation: ask for age.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi, I'm your personal fitness assistant bot! I'll ask you a few questions so I can create a custom exercise plan for you.\n\nWhat's your age?"
    )
    return AGE

# Collect Age.
async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("Great! Next, please tell me your sex (male/female).")
    return SEX

# Collect Sex.
async def sex_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sex'] = update.message.text
    await update.message.reply_text("How tall are you in centimeters? (e.g., 170)")
    return HEIGHT

# Collect Height.
async def height_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['height'] = update.message.text
    await update.message.reply_text("And your weight in kilograms? (e.g., 70)")
    return WEIGHT

# Collect Weight.
async def weight_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = update.message.text
    await update.message.reply_text("What is your fitness goal? (e.g., weight loss / muscle gain / maintenance)")
    return GOAL

# Collect Fitness Goal and Confirm Details.
async def goal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    summary = (
        f"Age: {context.user_data['age']}\n"
        f"Sex: {context.user_data['sex']}\n"
        f"Height: {context.user_data['height']} cm\n"
        f"Weight: {context.user_data['weight']} kg\n"
        f"Goal: {context.user_data['goal']}\n"
    )
    await update.message.reply_text(
        "Please confirm the following details:\n\n" + summary +
        "\nReply with 'yes' to confirm or 'no' to restart."
    )
    return CONFIRMATION

# Load your model.
MODEL_NAME = "Soorya03/Llama-3.2-1B-Instruct-FitnessAssistant"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Configure tokenizer (add this after loading the tokenizer)
tokenizer.pad_token = tokenizer.eos_token  # Set pad token to eos token
tokenizer.padding_side = "left"  # For batch generation compatibility

async def generate_routine(user_data):
    prompt = (
        f"You are a professional fitness trainer. Create a clear, numbered exercise plan until the goal is achieved for a "
        f"{user_data['age']}-year-old {user_data['sex']} who is {user_data['height']} cm tall and weighs "
        f"{user_data['weight']} kg. The goal is {user_data['goal']}. Provide day-by-day numbered instructions. "
        "Include a disclaimer: 'This advice is for informational purposes only and is not a substitute for professional guidance.'"
    )
    
    # Encode the input with return_attention_mask=True
    inputs = tokenizer(prompt, return_tensors='pt', return_attention_mask=True).to(device)
    
    # Generate with proper attention mask and pad token ID
    output_ids = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        pad_token_id=tokenizer.pad_token_id,
        max_length=500,  # Increased slightly for better responses
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        early_stopping=True,
        temperature=0.7,  # For more focused responses
        top_p=0.9,       # Nucleus sampling
    )
    
    # Decode and clean the output
    full_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    # Remove the prompt from the output
    routine = full_output.replace(prompt, "").strip()
    
    # Additional cleaning if needed
    if routine.startswith(":"):
        routine = routine[1:].strip()
    if routine.endswith('"'):
        routine = routine[:-1].strip()
    
    return routine

# Handle confirmation: If 'yes', generate routine; if 'no', restart.
async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_response = update.message.text.lower()
    if user_response == 'yes':
        routine = await generate_routine(context.user_data)
        await update.message.reply_text("Here is your personalized workout routine:\n\n" + routine)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Alright, let's try again. What is your age?")
        context.user_data.clear()  # Clear previous data.
        return AGE

# Command /cancel to exit the conversation.
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled. Stay active, and feel free to come back anytime!")
    return ConversationHandler.END

# Define the conversation handler.
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)],
        SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, sex_handler)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height_handler)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight_handler)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_handler)],
        CONFIRMATION: [MessageHandler(filters.Regex("^(yes|no)$"), confirmation_handler)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)