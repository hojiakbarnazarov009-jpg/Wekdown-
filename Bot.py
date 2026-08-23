@dp.message_handler()
async def handle_video_download(message: types.Message):
    user_id = message.from_user.id
    url = message.text
    
    if not await check_subscription(user_id):
        await message.reply("Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:", reply_markup=get_subscription_keyboard())
        return

    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        msg = await message.answer("Sizning so'rovingiz qabul qilindi, video yuklanmoqda... ⏳")
        
        api_url = "https://rapidapi.com"
        querystring = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "://rapidapi.com"
        }

        try:
            response = requests.get(api_url, headers=headers, params=querystring, timeout=30)
            
            # API nima javob berganini aniq ko'rish uchun log yozamiz
            logging.info(f"API Javob kodi: {response.status_code}")
            logging.info(f"API Ma'lumoti: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                video_url = None
                
                # API xilma-xil formatda qaytarishi mumkin, hammasini tekshiramiz
                if "url" in data:
                    video_url = data["url"]
                elif "links" in data and len(data["links"]) > 0:
                    # Agar links ro'yxat bo'lsa
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
                    await msg.edit_text("Ushbu havoladan yuklab olish uchun video havola ajratib olinmadi.")
            else:
                # Agar muammo API kalitda bo'lsa, xato kodini foydalanuvchiga ko'rsatadi
                await msg.edit_text(f"API xatoligi yuz berdi. Kod: {response.status_code}\nMatn: {response.text[:100]}")
        except Exception as e:
            logging.error(f"Yuklashda xato: {e}")
            await msg.edit_text(f"Texnik xatolik: {str(e)[:50]}")
    else:
        await message.reply("Iltimos, faqat to'g'ri Instagram, TikTok yoki YouTube video havolasini yuboring!")
