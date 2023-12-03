import logging
import re, string, sqlite3
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from api_token import TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Salom, {user.mention_html()}!\nBotni ishga tushirish uchun xabar jo'nating. Agar bot xato topsa, sizni ogohlantiradi.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Ushbu Telegram bot yozishmalarda ruscha va inglizcha so'zlar ishlatilgan xabarlarni aniqlab, foydalanuvchilarga o'zbek tilidagi muqobil so'zlarni tavsiya etadi")


async def chat_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    with open("log.txt", "a") as log:
        log.write(update.__str__() + '\n')

    text = update.message.text
    mistakes = {}
    message = "O'zbekcha gapir!"

    text = re.sub(r'"[^"]*"', '', text)  # remove text with quotation marks. Bot ignores all the text in quotes
    text = text.translate(str.maketrans('', '', string.punctuation + "0123456789"))  # removes all punctuation from the text

    text = text.lower()
    text = text.split(" ")

    conn = sqlite3.connect('dictionary.db')
    cursor = conn.cursor()

    # search for two word tokens
    i = 0
    while i < len(text) - 1:
        cursor.execute(f"SELECT word, translation FROM dictionary WHERE wordCount = 2 AND wholeWord = FALSE AND '{text[i] + ' ' + text[i + 1]}' LIKE word || '%'")
        result = cursor.fetchone()

        if result:
            text.pop(i + 1)
            text.pop(i)
            i -= 1

            if result[0] not in mistakes.keys():
                mistakes[result[0]] = result[1]
                message = message + f"\n* {result[0]} - {result[1]}"
        
        i += 1
            
    i = 0
    while i < len(text):
        # Search for whole words. Do not count words that start with 'prefix'
        cursor.execute("SELECT word, translation FROM dictionary WHERE wordCount = 1 AND word = ? AND wholeWord = TRUE", (text[i],))
        result = cursor.fetchone()

        if not result:
            # Search for words that start with a 'prefix'. Counts multiple variations of a single base word (e. g., translate, translated, translating, ...)
            cursor.execute(f"SELECT word, translation FROM dictionary WHERE wholeWord = FALSE AND '{text[i]}' LIKE word || '%'")
            result = cursor.fetchone()

        if result:
            text.pop(i)
            i -= 1

            if result[0] not in mistakes.keys():
                mistakes[result[0]] = result[1]
                message = message + f"\n* {result[0]} - {result[1]}"
        
        i += 1

    if mistakes:
        await update.message.reply_text(message)

    conn.close()

def main():
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , chat_message_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
