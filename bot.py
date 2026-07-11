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
    return "Bot is running 24/7!"

def run(): 
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

Thread(target=run).start()

# ==========================================
# كود البوت الأساسي
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك! أرسل رابط الفيديو وسأقوم بتحميله فوراً.")

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def download(message):
    url = message.text.split()[0]
    msg = bot.send_message(message.chat.id, "⏳ جاري المعالجة...")
    
    try:
        # الاتصال بالمسار الرئيسي المحدث لخدمة Cobalt
        payload = {"url": url}
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json"
        }
        
        res = requests.post("https://api.cobalt.tools/", json=payload, headers=headers)
        response = res.json()
        
        # الإصدار الجديد يرجع الرابط المباشر
        video_url = response.get("url")
        
        if video_url:
            bot.edit_message_text("⬇️ جاري التحميل للإرسال...", message.chat.id, msg.message_id)
            bot.send_video(
                message.chat.id, 
                video_url, 
                caption="✨ تم التحميل بواسطة:\n👨‍💻 Dev: Anas Sadeq"
            )
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            # معالجة الأخطاء
            error_text = response.get("text", "تعذر جلب الرابط من المصدر.")
            bot.edit_message_text(f"❌ خطأ:\n`{error_text}`", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ الاتصال:\n`{str(e)}`", message.chat.id, msg.message_id)

# ==========================================
# تشغيل البوت
# ==========================================
bot.infinity_polling(timeout=60, long_polling_timeout=60)
