app = ApplicationBuilder().token(TOKEN).build()

print("Бот запущен")

app.run_polling()
