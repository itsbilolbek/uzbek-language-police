import logging
import re, string, sqlite3
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from api_token import TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Ushbu Telegram bot yozishmalarda ruscha va inglizcha so'zlar ishlatilgan xabarlarni aniqlab, foydalanuvchilarga o'zbek tilidagi muqobil so'zlarni tavsiya etadi")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    print(update)

    text = update.message.text
    mistakes = []

    text = re.sub(r'"[^"]*"', '', text)  # remove text with quotation marks. Bot ignores all the text in quotes
    text = text.translate(str.maketrans('', '', string.punctuation))  # removes all punctuation from the text

    text = text.split(" ")

    conn = sqlite3.connect('dictionary.db')
    cursor = conn.cursor()

    for word in text:
        cursor.execute("SELECT translation FROM dictionary WHERE word = ?", (word,))
        result = cursor.fetchone()

        if result:
            mistakes.append(f"* {word} - {result[0]}")

    if mistakes:
        await update.message.reply_text("O'zbekcha gapir!\n" + '\n'.join(mistakes))

    conn.close()

def main():
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
