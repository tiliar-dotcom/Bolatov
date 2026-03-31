from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"

questions = [
    {
        "question": "Что выведет print(2 + 2)?",
        "options": ["3", "4", "5"],
        "answer": "4"
    },
    {
        "question": "Как объявить переменную?",
        "options": ["int x = 5", "x = 5", "var x = 5"],
        "answer": "x = 5"
    },
    {
        "question": "Какой тип данных у 'Hello'?",
        "options": ["int", "str", "bool"],
        "answer": "str"
    }
]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_data[user_id] = {"score": 0, "q": 0}
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    q_index = user_data[user_id]["q"]

    if q_index < len(questions):
        q = questions[q_index]
        keyboard = [[opt] for opt in q["options"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(q["question"], reply_markup=reply_markup)
    else:
        score = user_data[user_id]["score"]
        await update.message.reply_text(f"Тест завершён! Твой результат: {score}/{len(questions)}")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_answer = update.message.text

    q_index = user_data[user_id]["q"]
    correct_answer = questions[q_index]["answer"]

    if user_answer == correct_answer:
        user_data[user_id]["score"] += 1

    user_data[user_id]["q"] += 1
    await send_question(update, context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

app.run_polling()
