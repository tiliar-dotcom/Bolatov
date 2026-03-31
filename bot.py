import os
import csv
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 токен из Railway Variables
TOKEN = os.getenv("8615966494:AAEo6b5axjcrlQrHz1K-YCRp0sE_-fSyMBk")

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

# ▶️ старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_data[user_id] = {
        "name": None,
        "score": 0,
        "q": 0,
        "answers": []
    }
    await update.message.reply_text("Введите ваше ФИО:")

# 📩 обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text

    if user_id not in user_data:
        await start(update, context)
        return

    # ввод ФИО
    if user_data[user_id]["name"] is None:
        user_data[user_id]["name"] = text
        await send_question(update, context)
        return

    q_index = user_data[user_id]["q"]

    if q_index < len(questions):
        correct = questions[q_index]["answer"]
        is_correct = text == correct

        if is_correct:
            user_data[user_id]["score"] += 1

        user_data[user_id]["answers"].append([
            user_data[user_id]["name"],
            questions[q_index]["question"],
            text,
            correct,
            is_correct
        ])

        user_data[user_id]["q"] += 1
        await send_question(update, context)

# ❓ отправка вопроса
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    q_index = user_data[user_id]["q"]

    if q_index < len(questions):
        q = questions[q_index]
        keyboard = [[opt] for opt in q["options"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(q["question"], reply_markup=reply_markup)
    else:
        await finish_test(update, context)

# ✅ завершение теста
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    data = user_data[user_id]

    # запись в CSV
    with open("results.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data["answers"])

    await update.message.reply_text(
        f"Тест завершён!\nРезультат: {data['score']}/{len(questions)}"
    )

# 📄 отправка файла
async def send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("results.csv", "rb") as file:
            await update.message.reply_document(document=InputFile(file))
    except:
        await update.message.reply_text("Файл пока не создан")

# 🚀 запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("results", send_results))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
