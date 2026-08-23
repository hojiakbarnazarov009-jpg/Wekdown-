import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# 1. LOGLARNI SOZLASh
logging.basicConfig(level=logging.INFO)

# 2. TOKEn VA SOZLAMALAR (O'zingiznikini yozing)
API_TOKEN = 'BU_YERGA_TELEGRAM_BOT_TOKENINI_YOZING'
CHANNELS = ['@uzbek_Ai_m']  # Kanalingiz usernamesi
RAPIDAPI_KEY = 'BU_YERGA_RAPIDAPI_KEYINI_YOZING'

# RapidAPI saytidan olingan manzillar
API_URL = "BU_YERGA_RAPIDAPI_DAN_OLINGAN_API_URL_YOZILADI"
API_HOST = "BU_YERGA_API_HOST_NOMI_YOZILADI"

# 3. BOT VA DISPATChERNI INITIALIZATsIYa QILISh
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# 4. RENDER UChUN FLASK PORTINI TINGLASh (Render o'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run_flask():
    # Render avtomatik ravishda PORT muhit o'zgaruvchisini beradi, bo'lmasa 10000 port
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 5. KANALGA OBUNANI TEKShIRISh FUNKSTsIYaSI
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xato: {e}")
            return False
    return True

# Tugma yaratish
def get_subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for channel in CHANNELS:
        keyboard.add(types.InlineKeyboardButton(text="Kanalga a'zo bo'lish ➕", url=f"https://t.me{channel.strip('@')}"))
    keyboard.add(types.InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_sub"))
    return keyboard

# 6. BOT BUYRUQLARI (START)
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if await check_subscription(user_id):
        await message.reply(f"Salom {message.from_user.full_name}! Menga Instagram, TikTok yoki YouTube havola yuboring.")
    else:
        await message.reply("Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())

# Tekshirish tugmasi bosilganda
@dp.callback_query_handler(text="check_sub")
async def callback_check_sub(call: types.CallbackQuery):
    user_id = call.from_user.id
    if await check_subscription(user_id):
        await call.message.delete()
        await call.message.answer("Rahmat! Obuna tasdiqlandi. Endi havolalarni yuborishingiz mumkin. 🎉")
    else:
        await call.answer("Siz hali barcha kanallarga a'zo bo'lmadingiz! ❌", show_alert=True)

# 7. VIDEONI YuKLAB OLISh (ASOSIY QISM)
@dp.message_handler()
async def handle_video_download(message: types.Message):
    user_id = message.from_user.id
    url = message.text
    
    if not await check_subscription(user_id):
        await message.reply("Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())
        return

    if any(domain in url for domain in ["instagram.com", "youtube.com", "youtu.be", "tiktok.com"]):
        msg = await message.answer("Sizning so'rovingiz qabul qilindi, video yuklanmoqda... ⏳")
        
        querystring = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": API_HOST
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, headers=headers, params=querystring, timeout=30) as response:
                    logging.info(f"API Javob kodi: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        video_url = None
                        
                        # API formatlarini tahlil qilish
                        if "url" in data:
                            video_url = data["url"]
                        elif "links" in data and len(data["links"]) > 0:
                            if isinstance(data["links"], list):
                                video_url = data["links"][0].get("url")
                            else:
                                video_url = data["links"].get("url")
                        elif "medias" in data and len(data["medias"]) > 0:
                            video_url = data["medias"][0].get("url")
                        
                        if video_url:
                            await bot.send_chat_action(message.chat.id, 'upload_video')
                            await message.reply_video(video=video_url, caption="Bot orqali yuklab olindi ✨\n\nKanalimiz: @uzbek_Ai_m")
                            await msg.delete()
                        else:
                            await msg.edit_text("Ushbu havoladan videoni ajratib bo'lmadi. Boshqa havola kiritib ko'ring.")
                    else:
                        res_text = await response.text()
                        await msg.edit_text(f"API xatoligi yuz berdi. Kod: {response.status}")
                        
        except Exception as e:
            logging.error(f"Yuklashda xato: {e}")
            await msg.edit_text("Videoni yuklashda texnik xatolik yuz berdi.")
    else:
        await message.reply("Iltimos, faqat to'g'ri Instagram, TikTok yoki YouTube video havolasini yuboring!")

# 8. ISHGA TUShIRISh
if __name__ == '__main__':
    # Flaskni alohida oqimda (Thread) ishga tushiramiz, u botning ishlashiga xalaqit bermaydi
    server_thread = Thread(target=run_flask)
    server_thread.start()
    
    # Telegram botni ishga tushirish (Eski webhooklarni tozalab yuborish bilan)
    executor.start_polling(dp, skip_updates=True)
