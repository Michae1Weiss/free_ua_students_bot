import logging

from peewee import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler, ConversationHandler

from models import User
from logconf import get_logger
from manager import get_database
from settings import TOKEN

db = get_database()
logger = get_logger(__name__)

reply_template = "https://twitter.com/intent/tweet?in_reply_to={tweet_id}&text={text}"
twitter_max_length = 280


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")
    
    user_id = update.effective_chat.id
    try:
        # check whether user with this ID exists in DB 
        user = User.select().where(User.user_id == user_id).dicts().get()
    except DoesNotExist as e:
        # Create user in DB if does not exists
        logger.info(f"User with id '{user_id}' does not exists. Create new user...")
        user = User.create(user_id=user_id)


def echo(update, context):
    """..."""
    update.message.reply_text(update.message.text)
    # update.effective_chat.id


def unknown(update, context):
    """..."""
    update.message.reply_text("Sorry, I didn't understand that command.")


def main_menu_keyboard():
    """..."""
    keyboard = [[InlineKeyboardButton('Add individual comment', callback_data='m1')],
                [InlineKeyboardButton('Comment related tweet', callback_data='m2')],
                [InlineKeyboardButton('Comment related Facebook post', callback_data='m3')],
                [InlineKeyboardButton('Show statistic', callback_data='m4')]]
    return InlineKeyboardMarkup(keyboard)


def main_menu(update, context):
    """..."""
    update.message.reply_text(
        text="Test main menu:",
        reply_markup=main_menu_keyboard()
    )

def adding_comment(update, context) -> str:
    """Add comment."""
    text = "Okay, write your comment."
    button = InlineKeyboardButton(text="Add comment", callback_data="main")
    keyboard = InlineKeyboardMarkup.from_button(button)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)


if __name__ == "__main__":
    # Create Updater instance
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(adding_comment, pattern='m1')],
        states={},
        fallbacks=[]
    )

    # Register handlers
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", main_menu))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    # dp.add_handler(CallbackQueryHandler(second_menu, pattern='m2'))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    dp.add_handler(MessageHandler(Filters.text, echo))

    # Start the bot
    updater.start_polling()
