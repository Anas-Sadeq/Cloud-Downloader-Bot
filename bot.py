import telebot
import requests
import os
from flask import Flask
from threading import Thread

# ==========================================
# إعدادات تيليجرام
# ==========================================
# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8466380764:AAHH3k3U4vEepn9C20Rz1jwfCyFumv9jyzQ"
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# إعداد سيرفر فلاسك لمنع السبات
# ==========================================
app = Flask(__name__)

@app.route('/')
def index(): 
    return "Bilingual Bot is Alive and Running (Cobalt API)!"

def run(): 
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

Thread(target=run).start()

# ==========================================
# كود البوت الأساسي
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "**Welcome! / أهلاً بك!** 🚀\n\n"
        "🇬🇧 Send me any video link (YouTube, TikTok, Instagram...) and I will download it for you.\n"
        "🇸🇦 أرسل لي أي رابط فيديو وسأقوم بتحميله فوراً عبر خدمة Cobalt."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def download(message):
    url = message.text.split()[0]
    msg = bot.send_message(message.chat.id, "⏳ جاري المعالجة من خوادم Cobalt...")
    
    try:
        # إرسال طلب لخدمة Cobalt
        payload = {"url": url}
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        res = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers)
        response = res.json()
        
        # التحقق من وجود رابط الفيديو في الرد
        if "url" in response:
            bot.edit_message_text("⬇️ جاري التحميل للإرسال...", message.chat.id, msg.message_id)
            bot.send_video(
                message.chat.id, 
                response["url"], 
                caption="✨ تم التحميل بواسطة:\n👨‍💻 Dev: Anas Sadeq"
            )
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            # هنا التعديل الهندسي: إظهار الخطأ الحقيقي القادم من الخادم
            error_text = response.get("text", str(response))
            bot.edit_message_text(
                f"❌ خادم Cobalt يقول:\n`{error_text}`", 
                message.chat.id, 
                msg.message_id, 
                parse_mode="Markdown"
            )
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ الاتصال:\n`{str(e)}`", message.chat.id, msg.message_id)

# ==========================================
# تشغيل البوت
# ==========================================
bot.infinity_polling(timeout=60, long_polling_timeout=60)
