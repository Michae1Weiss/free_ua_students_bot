#!/usr/bin/env python
"""
The bot is started and runs until we press Ctrl-C on the command line.

Usage:
Telegram bot that helps students.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import urllib.parse

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from peewee import *

# Enable logging
from models import Comment, User, Tweet, CommentedTweet, LANGUAGES, LANGUAGE_CHOICES
from manager import get_database
from settings import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
db = get_database()
reply_template = "https://twitter.com/intent/tweet?in_reply_to={tweet_id}&text={text}"

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, TYPING_COMMENT, DELETE_COMMENT, PERFORM_DELETE = range(6)
TWEET_REPLY_MODE, TWEET_REPLY_STATUS, TWEET_SELECT_COMMENT = range(6, 9)
ADD_TWEET_ID, ADD_TWEET_DESCRIPTION, ADD_TWEET_LANGUAGE, PERFORM_CHOOSING_COMMENT = range(9, 13)

reply_keyboard = [
    ['Зберегти шаблон коментара', 'Видалити шаблон коментара', 'Показати шаблони коментарів'],
    ['Коментувати твіт', 'Додати твіт'],
    ['Вийти'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

tweet_mode_keyboard = [
    ['Обрати шаблон коментара', 'Пропустити'],
    ['Назад']
]
tweet_mode_markup = ReplyKeyboardMarkup(tweet_mode_keyboard, one_time_keyboard=True)

tweet_status_keyboard = [
    ['Я це зробив!'],
    ['Назад']
]
tweet_status_markup = ReplyKeyboardMarkup(tweet_status_keyboard, one_time_keyboard=True)

tweet_lang_keyboard = [
    [lang for (id, lang) in LANGUAGE_CHOICES],
    ['Назад']
]
tweet_lang_markup = ReplyKeyboardMarkup(tweet_lang_keyboard, one_time_keyboard=True)


def get_or_create_user(user_id: str):
    try:
        # check whether user with this ID exists in DB 
        return User.select().where(User.user_id == user_id).get()
    except DoesNotExist as e:
        # Create user in DB if does not exists
        logger.info(f"User with id '{user_id}' does not exists. Create new user...")
        return User.create(user_id=user_id)


def get_comments(user: User):
    try:
        # try to fetch user's comments
        comments = Comment.select().where(Comment.user == user)
    except DoesNotExist as e:
        print(f"Some error: {e}")
        comments = None

    return comments


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Привіт!\n"
        "Давай розповімо усьому світу про студентів України!\n"
        "Бот дає посилання на твіти, тобі треба лише написати або використати готовий коментар.",
        reply_markup=markup,
    )

    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    return CHOOSING


# =============== COMMENTS ===============

def delete_comment(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)
    comments = get_comments(user)

    delete_keyboard = [[i for (i, _) in enumerate(comments, 1)], ['Back']]
    delete_markup = ReplyKeyboardMarkup(delete_keyboard, one_time_keyboard=True)

    update.message.reply_text(
        "Обери номер коментара, який треба видалити:",
        reply_markup=delete_markup,
    )

    return PERFORM_DELETE


def perform_delete(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(f"Trying to delete comment with index {text} ...")

    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)
    comments = get_comments(user)

    if not text.isdigit():
        update.message.reply_text("Повинно бути число")  # TODO: add keyboard
        return PERFORM_DELETE

    try:
        i = int(text) - 1
        comment = comments[i]
    except IndexError as i:
        update.message.reply_text("Нема коментаря з таким номером")  # TODO: add keyboard
        return PERFORM_DELETE

    try:
        comment.delete_instance()
    except Exception as e:
        update.message.reply_text("Неможливо видалити коментар :(")  # TODO: add keyboard
        print(f'ERROR: cannot delete comment - {e}')
        return PERFORM_DELETE

    print(f"Successfully deleted comment with index {i}")
    update.message.reply_text(
        "Коментар видалено!"
        "Вибери наступну дію:",
        reply_markup=markup,
    )
    return CHOOSING


def show_comments(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)
    comments = get_comments(user)

    print(f"Comments: {comments} | User: {user}")
    comments_str = '\n\n'.join([f'{i}: {c.text}' for (i, c) in enumerate(comments, 1)])
    update.message.reply_text(
        f'Кількість коментарів: {len(comments)}\n\n{comments_str}',
        reply_markup=markup,
    )

    return CHOOSING


def add_comment(update: Update, context: CallbackContext) -> int:
    """Ask the user for comment."""
    update.message.reply_text(f'Напиши коментар:')
    return TYPING_COMMENT


def received_comment(update: Update, context: CallbackContext) -> int:
    """Store comment provided by user and ask for the next action."""
    max_length = 280

    text = update.message.text
    text_length = len(text)
    print(text)

    # TODO: if comment is longer than 270 - back to input

    if text_length > max_length:
        update.message.reply_text(
            f"Коментар дуже великий. Максимальна кількість символів - {max_length}.\n"
            f"Коментар налічує {len(text)} символів. Усього {max_length - text_length} зайвих символів.\n"
            f"Напиши коментар:"
        )

        return TYPING_COMMENT

    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    data = {
        "user": user,
        "text": text
    }
    print(data)
    Comment.create(**data)

    update.message.reply_text("Вибери наступну дію:", reply_markup=markup)

    return CHOOSING


# ===== ADD TWEET =====

def add_tweet(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    if not user.is_superuser:
        update.message.reply_text(
            "Треба бути адміном щоб добавляти твіти!\n"
            "Вибери наступну дію:",
            reply_markup=markup,
        )
        return CHOOSING

    update.message.reply_text("Відправ ID твіта:")

    return ADD_TWEET_ID


def add_tweet_id(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text
    user_data['tweet_id'] = text

    update.message.reply_text("Добав короткий опис твіта та людини, яка його написала:")

    return ADD_TWEET_DESCRIPTION


def add_tweet_desctiprion(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text
    user_data['tweet_description'] = text

    update.message.reply_text("Обери мову твіта:", reply_markup=tweet_lang_markup)

    return ADD_TWEET_LANGUAGE


def add_tweet_language(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text
    user_data['tweet_language'] = text

    language_code = LANGUAGES[user_data['tweet_language']]

    data = {
        'tweet_id': user_data['tweet_id'],
        'description': user_data['tweet_description'],
        'language': language_code,
    }

    tweet = Tweet.create(**data)

    print("Tweet was created!")

    update.message.reply_text(
        "Твіт успішно добавлено!\n"
        "Обери наступну опцію:",
        reply_markup=markup,
    )

    return CHOOSING


def comment_tweet(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    commented_tweets = CommentedTweet.select().where(CommentedTweet.user == user)
    try:
        tweet_in_work = commented_tweets.where(CommentedTweet.in_work == True).get()
    except DoesNotExist as e:
        # if no tweets in work - pick random one
        tweets = Tweet.select().where(Tweet.id.not_in([c.id for c in commented_tweets]))

        if tweets.count() < 1:
            update.message.reply_text(
                "Наразі ти відповів на всі твіти!\n"
                "Вибери наступну дію:",
                reply_markup=markup,
            )

            return CHOOSING

        tweet = tweets.order_by(fn.Random()).limit(1)
        tweet_in_work = CommentedTweet.create(user=user, tweet=tweet)

    update.message.reply_text(
        f"Посилання на твіт: {reply_template.format(tweet_id=tweet_in_work.tweet.tweet_id, text='')}\n"
        f"Про твіт: {tweet_in_work.tweet.description}"
        "Використати шаблон коментара чи ні?",
        reply_markup=tweet_mode_markup,
    )

    return TWEET_REPLY_MODE


def comment_tweet_mode(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    commented_tweets = CommentedTweet.select().where(CommentedTweet.user == user)
    tweet_in_work = commented_tweets.where(CommentedTweet.in_work == True).get()

    # if no tweets in work - pick random one
    if not tweet_in_work:
        raise ("WOW! No tweet in work")

    command = update.message.text

    if command == 'Обрати шаблон коментара':

        comments = Comment.select().where(Comment.user == user)

        choose_keyboard = [[i for (i, _) in enumerate(comments, 1)], ['Back']]
        choose_markup = ReplyKeyboardMarkup(choose_keyboard, one_time_keyboard=True)

        print('Choosing reply comment')
        update.message.reply_text(
            f"Обери шаблон коментара:",
            reply_markup=choose_markup,
        )

        return TWEET_SELECT_COMMENT
    elif command == 'Пропустити':
        update.message.reply_text(
            f"Посилання на твіт: {reply_template.format(tweet_id=tweet_in_work.tweet.tweet_id, text='')}\n" \
            f"Про твіт: {tweet_in_work.tweet.description}",
            reply_markup=tweet_status_markup,
        )
        return TWEET_REPLY_STATUS
    else:
        update.message.reply_text(
            f"Команда `{command}` не знайдена.\n" \
            f"Спробуй знову:",
            reply_markup=tweet_mode_markup,
        )
        return TWEET_REPLY_MODE


def choose_tweet_reply_comment(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)
    comments = get_comments(user)

    if not text.isdigit():
        update.message.reply_text("Має бути число")  # TODO: add keyboard
        return TWEET_SELECT_COMMENT

    try:
        i = int(text) - 1
        comment = comments[i]
    except IndexError as i:
        update.message.reply_text("Нема такого коментара")  # TODO: add keyboard
        return TWEET_SELECT_COMMENT

    print(f"Successfully selected comment with index {i}")

    tweet_in_work = CommentedTweet.select().where(CommentedTweet.user == user & CommentedTweet.in_work == True).get()

    _comment = urllib.parse.quote(comment.text)

    update.message.reply_text(
        f"Посилання на твіт: {reply_template.format(tweet_id=tweet_in_work.tweet.tweet_id, text=_comment)}\n" \
        f"Про твіт: {tweet_in_work.tweet.description}\n" \
        "Відповів на твіт?",
        reply_markup=tweet_status_markup,
    )
    return TWEET_REPLY_STATUS


def comment_tweet_status(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    user = get_or_create_user(user_id)

    tweet_in_work = CommentedTweet.select().where(CommentedTweet.user == user & CommentedTweet.in_work == True).get()
    tweet_in_work.in_work = False
    tweet_in_work.save()
    print("Tweet is marked as done!")

    update.message.reply_text(
        "Дякую, ти відповів на твіт! Наша перемога ближче!\n" \
        "Вибери наступну дію:",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    update.message.reply_text(
        "До зустрічі! Щоб знову розпочати медіа-війну напиши /start",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^Додати шаблон коментара$'), add_comment),
                MessageHandler(Filters.regex('^Додати твіт$'), add_tweet),
                MessageHandler(Filters.regex('^Видалити шаблон коментара$'), delete_comment),
                MessageHandler(Filters.regex('^Показати шаблони коментарів$'), show_comments),
                MessageHandler(Filters.regex('^Коментувати твіт$'), comment_tweet),
            ],
            TYPING_COMMENT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    received_comment,
                )
            ],
            ADD_TWEET_ID: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    add_tweet_id,
                )
            ],
            ADD_TWEET_DESCRIPTION: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    add_tweet_desctiprion,
                )
            ],
            ADD_TWEET_LANGUAGE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    add_tweet_language,
                )
            ],
            PERFORM_DELETE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    perform_delete,
                )
            ],
            TWEET_REPLY_MODE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    comment_tweet_mode,
                )
            ],
            TWEET_REPLY_STATUS: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    comment_tweet_status,
                )
            ],
            TWEET_SELECT_COMMENT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Назад$')),
                    choose_tweet_reply_comment,
                )
            ],
        },
        fallbacks=[
            MessageHandler(Filters.regex('^Вийти$'), done),
            MessageHandler(Filters.regex('^Назад$'), start),
        ],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
