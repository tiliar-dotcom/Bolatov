import os
from openpyxl import Workbook, load_workbook
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 токен (Railway)
TOKEN = os.getenv("8429654652:AAHEDXDt8nT_mczfubd4rxf-OkUTFoP0wFk")

# 🔒 твой Telegram ID (вставь свой!)
ADMIN_ID = kyops1254

questions = [
    {"question": "1. Что используется для вывода текста в Python?", "options": ["print()", "echo()", "write()"], "answer": "print()"},
    {"question": "2. Какой язык используется для создания сайтов?", "options": ["HTML", "Windows", "Photoshop"], "answer": "HTML"},
    {"question": "3. Какой символ используется для комментариев в Python?", "options": ["#", "//", "/*"], "answer": "#"},
    {"question": "4. Что означает CPU?", "options": ["Центральный процессор", "Видеокарта", "Оперативная память"], "answer": "Центральный процессор"},
    {"question": "5. Как называется цикл в Python?", "options": ["for", "repeat", "cycle"], "answer": "for"},
    {"question": "6. Какой язык программирования самый популярный для ботов Telegram?", "options": ["Python", "Paint", "Excel"], "answer": "Python"},
    {"question": "7. Как называется ошибка в программе?", "options": ["Баг", "Фикс", "Скрипт"], "answer": "Баг"},
    {"question": "8. Как называется хранение данных в переменной?", "options": ["value", "переменная", "папка"], "answer": "переменная"},
    {"question": "9. Что делает input() в Python?", "options": ["Получает ввод от пользователя", "Удаляет код", "Закрывает программу"], "answer": "Получает ввод от пользователя"},
    {"question": "10. Что такое IDE?", "options": ["Среда разработки", "Игра", "Антивирус"], "answer": "Среда разработки"}
]

user_data = {}

# 📊 сохранение в Excel
def save_to_excel(data):
    file_name = "results.xlsx"

    if not os.path.exists(file_name):
        wb = Workbook()
        ws = wb.active
        ws.append(["ФИО", "Вопрос", "Ответ", "Правильный", "Верно"])
        wb.save(file_name)

    wb = load_workbook(file_name)
    ws = wb.active

    for row in data:
        ws.append(row)

    wb.save(file_name)

# ▶️ старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_data[user_id] = {"name": None, "score": 0, "q": 0, "answers": []}
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

    save_to_excel(data["answers"])

    await update.message.reply_text(
        f"Тест завершён!\nРезультат: {data['score']}/{len(questions)}"
    )

# 📄 отправка Excel (только тебе)
async def send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа ❌")
        return

    try:
        with open("results.xlsx", "rb") as file:
            await update.message.reply_document(document=InputFile(file))
    except:
        await update.message.reply_text("Файл пока не создан")

# 🚀 запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("results", send_results))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
