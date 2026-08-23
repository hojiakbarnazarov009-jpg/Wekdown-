
import os
import logging
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types

# 1. RENDER UCHUN VEB-SERVER (Bot o'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"

def run():
    # Render taqdim etadigan portni aniqlaydi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. BOTNING ASLIY SOZLAMALARI
API_TOKEN = '8800926785:AAF3pqOjlD6GrX9HzmhLLieQRNisdU6NpmY'
RAPIDAPI_KEY = '2d5de4329amsh1ba00ea6d291406p1b9423jsncc55e2274a4a'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Men 'Fast download bot'man. Menga havola yuboring.")

@dp.message_handler()
async def echo(message: types.Message):
    # Bu yerda sizning RapidAPI chaqiruvingiz bo'ladi
    await message.answer("Sizning so'rovingiz qabul qilindi, qayta ishlanmoqda...")

if __name__ == '__main__':
    # Veb-serverni fonda ishga tushiramiz
    keep_alive()
    
    # Botni ishga tushiramiz
    executor.start_polling(dp, skip_updates=True)
