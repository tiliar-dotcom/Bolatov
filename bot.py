import os
import csv
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 токен из Railway Variables
TOKEN = "8429654652:AAHEDXDt8nT_mczfubd4rxf-OkUTFoP0wFk"


questions = [
    {
        "question": "1. Что используется для вывода текста в Python?",
        "answers": ["print()", "echo()", "write()"],
        "correct": "print()"
    },
    {
        "question": "2. Какой язык используется для создания сайтов?",
        "answers": ["HTML", "Windows", "Photoshop"],
        "correct": "HTML"
    },
    {
        "question": "3. Какой символ используется для комментариев в Python?",
        "answers": ["#", "//", "/*"],
        "correct": "#"
    },
    {
        "question": "4. Что означает CPU?",
        "answers": [
            "Центральный процессор",
            "Видеокарта",
            "Оперативная память"
        ],
        "correct": "Центральный процессор"
    },
    {
        "question": "5. Как называется цикл в Python?",
        "answers": ["for", "repeat", "cycle"],
        "correct": "for"
    },
    {
        "question": "6. Какой язык программирования самый популярный для ботов Telegram?",
        "answers": ["Python", "Paint", "Excel"],
        "correct": "Python"
    },
    {
        "question": "7. Как называется ошибка в программе?",
        "answers": ["Баг", "Фикс", "Скрипт"],
        "correct": "Баг"
    },
    {
        "question": "8. Как называется хранение данных в переменной?",
        "answers": ["value", "переменная", "папка"],
        "correct": "переменная"
    },
    {
        "question": "9. Что делает input() в Python?",
        "answers": [
            "Получает ввод от пользователя",
            "Удаляет код",
            "Закрывает программу"
        ],
        "correct": "Получает ввод от пользователя"
    },
    {
        "question": "10. Что такое IDE?",
        "answers": [
            "Среда разработки",
            "Игра",
            "Антивирус"
        ],
        "correct": "Среда разработки"
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
