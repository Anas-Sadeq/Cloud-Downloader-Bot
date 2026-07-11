import telebot
import requests
import os
from flask import Flask
from threading import Thread

# التوكن الخاص بك
BOT_TOKEN = "8466380764:AAHH3k3U4vEepn9C20Rz1jwfCyFumv9jyzQ"
bot = telebot.TeleBot(BOT_TOKEN)

# إعداد خادم منع السبات
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is running!"
def run(): app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
Thread(target=run).start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك! أرسل رابط الفيديو وسأقوم بتحميله فوراً عبر خدمة Cobalt.")

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def download(message):
    url = message.text.split()[0]
    msg = bot.send_message(message.chat.id, "⏳ جاري المعالجة من خوادم Cobalt...")
    
    try:
        # إرسال طلب لخدمة Cobalt
        payload = {"url": url, "vQuality": "720"}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        response = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers).json()
        
        if "url" in response:
            bot.edit_message_text("⬇️ جاري التحميل والإرسال...", message.chat.id, msg.message_id)
            bot.send_video(message.chat.id, response["url"], caption="✨ تم التحميل بواسطة: Anas Sadeq Bot")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ لم أتمكن من جلب الفيديو، تأكد من الرابط.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ: {str(e)}", message.chat.id, msg.message_id)

bot.infinity_polling()
