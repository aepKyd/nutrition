import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api import get_recipes, get_remaining_dishes, create_cooked_dish, create_consumed_item, get_today_summary

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SELECT_RECIPE, ENTER_WEIGHTS = range(2)
SELECT_DISH, ENTER_PORTION, SELECT_MEAL_TYPE = range(3, 6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hi! I'm your nutrition assistant. I can help you track what you cook and eat.\n\n"
        "Use /cooked to log a dish you've prepared.\n"
        "Use /ate to log a portion you've consumed."
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the nutritional summary for the current day."""
    summary = get_today_summary()
    if not summary:
        await update.message.reply_text("I couldn't retrieve your summary for today. Have you logged any meals?")
        return

    total = summary['total_nutrition']
    message = f"Your summary for today ({summary['date']}):\n\n"
    message += f"Total Calories: {total['calories']:.0f} kcal\n"
    message += f"Total Proteins: {total['proteins']:.0f} g\n"
    message += f"Total Fats: {total['fats']:.0f} g\n"
    message += f"Total Carbs: {total['carbs']:.0f} g\n\n"

    if summary.get('meals'):
        message += "Meals:\n"
        for meal in summary['meals']:
            message += f"- {meal['meal_type'].capitalize()}: {meal['calories']:.0f} kcal\n"

    await update.message.reply_text(message)


from api import get_recipes, search_recipes, get_remaining_dishes, create_cooked_dish, create_consumed_item, get_today_summary

async def cooked_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the 'I cooked' conversation."""
    query = " ".join(context.args) if context.args else None
    
    if query:
        recipes = search_recipes(query)
        if not recipes:
            await update.message.reply_text("I couldn't find any recipes matching that name. Please try again or type /cancel.")
            return ConversationHandler.END
    else:
        recipes = get_recipes()
        if not recipes:
            await update.message.reply_text("I couldn't find any recipes. Please add some recipes to the database first.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

    context.user_data['recipes'] = recipes
    reply_keyboard = [[recipe['name']] for recipe in recipes]
    await update.message.reply_text(
        "Please choose one of the found recipes:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return SELECT_RECIPE

async def select_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's recipe selection."""
    selected_recipe_name = update.message.text
    recipes = context.user_data.get('recipes', [])
    
    selected_recipe = next((r for r in recipes if r['name'] == selected_recipe_name), None)

    if not selected_recipe:
        await update.message.reply_text("Invalid selection. Please choose from the list or type /cancel.")
        return SELECT_RECIPE
    
    context.user_data['selected_recipe_id'] = selected_recipe['id']
    await update.message.reply_text(f"You selected: {selected_recipe['name']}.\n\nPlease enter the initial and final weights in grams, separated by a comma (e.g., '1200, 1000').", reply_markup=ReplyKeyboardRemove())
    return ENTER_WEIGHTS

async def enter_weights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the input of initial and final weights."""
    try:
        initial_weight, final_weight = map(float, update.message.text.split(','))
    except (ValueError, TypeError):
        await update.message.reply_text("Invalid format. Please enter two numbers separated by a comma (e.g., '1200, 1000').")
        return ENTER_WEIGHTS

    recipe_id = context.user_data.get('selected_recipe_id')
    cooked_dish = create_cooked_dish(recipe_id, initial_weight, final_weight)

    if cooked_dish:
        await update.message.reply_text("I've successfully logged your cooked dish!")
    else:
        await update.message.reply_text("Sorry, I failed to log your dish. Please try again.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def ate_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the 'I ate' conversation."""
    remaining_dishes = get_remaining_dishes()
    if not remaining_dishes:
        await update.message.reply_text("There are no cooked dishes with remaining portions. Use /cooked to log a new dish.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data['remaining_dishes'] = remaining_dishes
    reply_keyboard = [[f"{dish['recipe_name']} ({dish['remaining_weight']}g left)"] for dish in remaining_dishes]
    await update.message.reply_text(
        "What did you eat? Please choose from the list:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return SELECT_DISH

async def select_dish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's dish selection."""
    selected_dish_text = update.message.text
    remaining_dishes = context.user_data.get('remaining_dishes', [])
    
    selected_dish = next((d for d in remaining_dishes if f"{d['recipe_name']} ({d['remaining_weight']}g left)" == selected_dish_text), None)

    if not selected_dish:
        await update.message.reply_text("Invalid selection. Please choose from the list or type /cancel.")
        return SELECT_DISH
    
    context.user_data['selected_dish_id'] = selected_dish['cooked_dish_id']
    await update.message.reply_text(f"You selected: {selected_dish['recipe_name']}.\n\nHow many grams did you eat?", reply_markup=ReplyKeyboardRemove())
    return ENTER_PORTION

async def enter_portion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the input of the portion weight."""
    try:
        weight = float(update.message.text)
    except (ValueError, TypeError):
        await update.message.reply_text("Invalid format. Please enter a number for the weight.")
        return ENTER_PORTION
    
    context.user_data['portion_weight'] = weight
    
    reply_keyboard = [['breakfast', 'lunch', 'dinner', 'snack']]
    await update.message.reply_text(
        "What meal type was this?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return SELECT_MEAL_TYPE

async def select_meal_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the meal type selection and logs the consumed item."""
    meal_type = update.message.text.lower()
    if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
        await update.message.reply_text("Invalid meal type. Please choose from the options.")
        return SELECT_MEAL_TYPE
        
    dish_id = context.user_data.get('selected_dish_id')
    weight = context.user_data.get('portion_weight')

    consumed_item = create_consumed_item(dish_id, weight, meal_type)

    if consumed_item:
        await update.message.reply_text("I've successfully logged what you ate!", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Sorry, I failed to log your meal. Please try again.", reply_markup=ReplyKeyboardRemove())
    
    context.user_data.clear()
    return ConversationHandler.END

async def left(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the remaining portions of all cooked dishes."""
    remaining_dishes = get_remaining_dishes()
    if not remaining_dishes:
        await update.message.reply_text("There are no cooked dishes with remaining portions.")
        return

    message = "Here are your remaining dishes:\n\n"
    for dish in remaining_dishes:
        message += f"- {dish['recipe_name']}: {dish['remaining_weight']:.0f}g\n"
    
    await update.message.reply_text(message)

async def set_commands(application: Application):
    """Sets the bot's commands."""
    commands = [
        ("start", "Welcome message"),
        ("cooked", "Log a cooked dish"),
        ("ate", "Log a consumed portion"),
        ("left", "Show remaining portions"),
        ("today", "Show today's summary"),
        ("cancel", "Cancel the current operation"),
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    """Start the bot."""
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
        return
        
    application = Application.builder().token(token).build()

    # Set the command palette
    application.post_init = set_commands


    cooked_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cooked", cooked_start)],
        states={
            SELECT_RECIPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_recipe)],
            ENTER_WEIGHTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_weights)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    ate_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ate", ate_start)],
        states={
            SELECT_DISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_dish)],
            ENTER_PORTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_portion)],
            SELECT_MEAL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_meal_type)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("left", left))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(cooked_conv_handler)
    application.add_handler(ate_conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()