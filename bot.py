import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")  
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ===== SUBJECTS =====
subjects = {
    "Информатика": ["5", "6", "7", "8", "9", "10", "11"],
    "Математика": ["5", "6"]
}

# ===== QUESTION BANK =====
question_bank = {
    "Информатика": {
        "5": [
            {"question":"Что такое компьютер?","options":["Электронное устройство","Игрушка","Телефон","Телевизор"],"answer":"Электронное устройство"},
            {"question":"Как называется устройство ввода текста?","options":["Клавиатура","Монитор","Колонки","Принтер"],"answer":"Клавиатура"},
        ],
        "6": [
            {"question":"Что такое файл?","options":["Хранилище данных","Монитор","Принтер","Игра"],"answer":"Хранилище данных"},
        ],
        "7": [
            {"question":"Что такое алгоритм?","options":["Последовательность действий","Компьютер","Программа","Сайт"],"answer":"Последовательность действий"},
            {"question":"Что такое Python?","options":["Язык программирования","Браузер","Антивирус","Игра"],"answer":"Язык программирования"},
            {"question":"Что делает print()?","options":["Выводит текст","Удаляет файл","Создает папку","Закрывает программу"],"answer":"Выводит текст"},
            {"question":"Что делает input()?","options":["Получает ввод пользователя","Удаляет файл","Выключает ПК","Создает список"],"answer":"Получает ввод пользователя"},
        ]
    }
}

# ===== USER STATE =====
user_data = {}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Информатика", "Математика"]]
    await update.message.reply_text(
        "Выбери предмет:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== HANDLE =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # выбор предмета
    if text in subjects:
        user_data[user_id] = {"subject": text}
        keyboard = [[c] for c in subjects[text]]
        await update.message.reply_text(
            "Выбери класс:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    # выбор класса
    if user_id in user_data and "subject" in user_data[user_id] and "class" not in user_data[user_id]:
        subject = user_data[user_id]["subject"]
        if text in subjects[subject]:
            user_data[user_id]["class"] = text

            questions = question_bank.get(subject, {}).get(text, [])

            if not questions:
                await update.message.reply_text("Вопросов пока нет для этого класса")
                return

            q = random.choice(questions)
            user_data[user_id]["current"] = q

            keyboard = [[o] for o in q["options"]]
            await update.message.reply_text(
                q["question"],
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        return

    # ответы
    if user_id in user_data and "current" in user_data[user_id]:
        q = user_data[user_id]["current"]

        if text == q["answer"]:
            await update.message.reply_text("✅ Правильно!")
        else:
            await update.message.reply_text(f"❌ Неправильно. Ответ: {q['answer']}")

        del user_data[user_id]["current"]

        # следующий вопрос
        subject = user_data[user_id]["subject"]
        class_ = user_data[user_id]["class"]

        questions = question_bank.get(subject, {}).get(class_, [])
        q = random.choice(questions)
        user_data[user_id]["current"] = q

        keyboard = [[o] for o in q["options"]]
        await update.message.reply_text(
            q["question"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

# ===== MAIN =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")
    app.run_polling()
