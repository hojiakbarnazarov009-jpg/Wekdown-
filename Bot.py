import os
import logging
import requests
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. RENDER UCHUN VEB-SERVER (Bot o'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. BOTNING ASLIY SOZLAMALARI
API_TOKEN = '8800926785:AAF3pqOjlD6GrX9HzmhLLieQRNisdU6NpmY'
RAPIDAPI_KEY = '2d5de4329amsh1ba00ea6d291406p1b9423jsncc55e2274a4a'
CHANNEL_USERNAME = '@uzbek_Ai_m'  # Majburiy kanal (Bot bu kanalda admin bo'lishi shart!)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscription(user_id: int) -> bool:
    """Foydalanuvchi kanalga a'zo ekanini tekshirish"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Kanalni tekshirishda xatolik: {e}")
        # Agar bot kanalda admin bo'lmasa, hamma uchun bot to'xtab qolmasligi uchun True qaytaramiz
        return True

def get_subscription_keyboard():
    """Kanalga a'zo bo'lish tugmasi"""
    markup = InlineKeyboardMarkup()
    btn_link = InlineKeyboardButton(text="Kanalga a'zo bo'lish", url=f"https://t.me{CHANNEL_USERNAME.replace('@', '')}")
    btn_check = InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")
    markup.add(btn_link)
    markup.add(btn_check)
    return markup

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.reply(f"Salom! Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())
        return
        
    await message.reply("Salom! Men 'Fast download bot'man. Menga Instagram yoki YouTube havola yuboring.")

@dp.callback_query_handler(text="check_sub")
async def callback_check(call: types.CallbackQuery):
    user_id = call.from_user.id
    if await check_subscription(user_id):
        await call.message.delete()
        await call.message.answer("Rahmat! Kanalga a'zo bo'ldingiz. Endi menga video havolasini yuborishingiz mumkin.")
    else:
        await call.answer("Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

@dp.message_handler()
async def handle_video_download(message: types.Message):
    user_id = message.from_user.id
    url = message.text
    
    # Kanal a'zoligini majburiy tekshirish
    if not await check_subscription(user_id):
        await message.reply("Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())
        return

    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        msg = await message.answer("Sizning so'rovingiz qabul qilindi, video yuklanmoqda... ⏳")
        
        # RapidAPI sozlamalari
        api_url = "https://rapidapi.com"
        querystring = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "://rapidapi.com"
        }

        try:
            # GET so'rovi orqali havolani API'ga yuboramiz
            response = requests.get(api_url, headers=headers, params=querystring, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # API qaytargan JSON ichidan video havolasini qidiramiz
                video_url = None
                if "url" in data:
                    video_url = data["url"]
                elif "links" in data and len(data["links"]) > 0:
                    video_url = data["links"][0].get("url")
                
                if video_url:
                    await bot.send_chat_action(message.chat.id, 'upload_video')
                    await message.reply_video(video=video_url, caption="Bot orqali yuklab olindi ✨\n\nKanalimiz: @uzbek_Ai_m")
                    await msg.delete()
                else:
                    await msg.edit_text("Ushbu havoladan video topilmadi. Havola ochiq (publichniy) ekanligini tekshiring.")
            else:
                await msg.edit_text(f"API xatoligi yuz berdi (Kod: {response.status_code}).")
        except Exception as e:
            logging.error(f"Yuklashda xato: {e}")
            await msg.edit_text("Videoni yuklashda texnik xatolik yuz berdi.")
    else:
        await message.reply("Iltimos, faqat to'g'ri Instagram, TikTok yoki YouTube video havolasini yuboring!")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
