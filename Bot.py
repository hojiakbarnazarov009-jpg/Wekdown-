import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

# Konfiguratsiya
BOT_TOKEN = "8800926785:AAF3pqOjlD6GrX9HzmhLLieQRNisdU6NpmY"
REQUIRED_CHANNEL = "@uzbek_Ai_m"
RAPIDAPI_KEY = "2d5de4329amsh1ba00ea6d291406p1b9423jsncc55e2274a4a" 
RAPIDAPI_HOST = "://rapidapi.com"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        logging.error(f"Kanal tekshirishda xatolik: {e}")
        return False

def get_sub_keyboard():
    channel_url = f"https://t.me{REQUIRED_CHANNEL.lstrip('@')}"
    buttons = [
        [types.InlineKeyboardButton(text="Kanalga a'zo bo'lish", url=channel_url)],
        [types.InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

async def fetch_video_url(url: str) -> str:
    api_url = "https://://rapidapi.com/v1/social/autolink"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    payload = {"url": url}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    medias = data.get("medias", [])
                    if medias and isinstance(medias, list):
                        return medias[0].get("url")
                return None
        except Exception as e:
            logging.error(f"API xatoligi: {e}")
            return None

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer(f"Botdan foydalanish uchun {REQUIRED_CHANNEL} kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
    await message.answer("Salom! Video linkini yuboring (TikTok taqiqlangan).")

@dp.callback_query(F.data == "check_sub")
async def check_callback(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text("Rahmat! Endi video linkini yuborishingiz mumkin.")
    else:
        await callback.answer("Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)

@dp.message(F.text)
async def handle_link(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer(f"Botdan foydalanish uchun {REQUIRED_CHANNEL} kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return

    url = message.text.strip()
    
    if "tiktok.com" in url.lower():
        await message.answer("Kechirasiz, TikTok platformasidan video yuklash taqiqlangan!")
        return

    if not url.startswith(("http://", "https://")):
        await message.answer("Iltimos, to'g'ri havola yuboring.")
        return

    status_msg = await message.answer("Video qayta ishlanmoqda, kuting...")
    video_download_url = await fetch_video_url(url)
    
    if video_download_url:
        try:
            await message.reply_video(video=video_download_url, caption="Sizning videongiz! @Wekdownbot")
            await status_msg.delete()
        except Exception as e:
            logging.error(f"Video yuborishda xatolik: {e}")
            await status_msg.edit_text("Videoni yuborishda xatolik yuz berdi (hajmi juda katta bo'lishi mumkin).")
    else:
        await status_msg.edit_text("Videoni yuklab bo'lmadi. Havola noto'g'ri yoki xizmatda nosozlik.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
