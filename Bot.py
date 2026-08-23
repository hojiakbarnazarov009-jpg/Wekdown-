import aiohttp  # Kodning eng yuqori qismida aiohttp import qilingan bo'lishi kerak
import logging
from aiogram import types

@dp.message_handler()
async def handle_video_download(message: types.Message):
    user_id = message.from_user.id
    url = message.text
    
    if not await check_subscription(user_id):
        await message.reply("Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())
        return

    if any(domain in url for domain in ["instagram.com", "youtube.com", "youtu.be", "tiktok.com"]):
        msg = await message.answer("Sizning so'rovingiz qabul qilindi, video yuklanmoqda... ⏳")
        
        # ⚠️ DIQQAT: Bu yerga RapidAPI'dan sotib olgan/olgan API endpointingiz manzilini to'liq yozing!
        # Masalan: "https://rapidapi.com" kabi bo'ladi.
        api_url = "BU_YERGA_RAPIDAPI_DAN_OLINGAN_API_URL_YAZILADI"
        
        querystring = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            # ⚠️ DIQQAT: Bu yerga API hostini to'g'ri yozing. Masalan: "social-download-all-in-one.p.rapidapi.com"
            "x-rapidapi-host": "BU_YERGA_API_HOST_NOMI_YOZILADI" 
        }

        try:
            # Asinxron so'rov yuborish (Bot qotib qolmasligi uchun)
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, params=querystring, timeout=30) as response:
                    
                    logging.info(f"API Javob kodi: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        video_url = None
                        
                        # API formatlarini tekshirish
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
                            await msg.edit_text("Ushbu havoladan videoni yuklab bo'lmadi yoki havola topilmadi.")
                    else:
                        response_text = await response.text()
                        await msg.edit_text(f"API xatoligi yuz berdi. Kod: {response.status}\nMatn: {response_text[:100]}")
                        
        except Exception as e:
            logging.error(f"Yuklashda xato: {e}")
            await msg.edit_text(f"Videoni yuklashda texnik xatolik yuz berdi.")
    else:
        await message.reply("Iltimos, faqat to'g'ri Instagram, TikTok yoki YouTube video havolasini yuboring!")
