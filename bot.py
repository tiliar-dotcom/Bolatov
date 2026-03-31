import os
import csv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

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

# 📌 Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_data[user_id] = {"score": 0, "q": 0, "answers": [], "name": None}
    await update.message.reply_text("Введите ваше ФИО:")

# 📌 Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text

    # если нет имени
    if user_data[user_id]["name"] is None:
        user_data[user_id]["name"] = text
        await send_question(update, context)
        return

    q_index = user_data[user_id]["q"]
    correct = questions[q_index]["answer"]

    is_correct = text == correct
    if is_correct:
        user_data[user_id]["score"] += 1

    user_data[user_id]["answers"].append({
        "question": questions[q_index]["question"],
        "user_answer": text,
        "correct_answer": correct,
        "is_correct": is_correct
    })

    user_data[user_id]["q"] += 1
    await send_question(update, context)

# 📌 Отправка вопроса
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

# 📌 Завершение теста
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    data = user_data[user_id]

    # запись в CSV
    with open("results.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for ans in data["answers"]:
            writer.writerow([
                data["name"],
                ans["question"],
                ans["user_answer"],
                ans["correct_answer"],
                ans["is_correct"]
            ])

    await update.message.reply_text(
        f"Тест завершён!\nБаллы: {data['score']}/{len(questions)}"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
