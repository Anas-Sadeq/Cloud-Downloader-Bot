import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import re
from flask import Flask
from threading import Thread

# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8466380764:AAHH3k3U4vEepn9C20Rz1jwfCyFumv9jyzQ"
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# إعداد سيرفر فلاسك لمنع السبات
# ==========================================
app = Flask(__name__)

@app.route('/')
def index():
    return "Bilingual Bot is Alive and Running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# ذاكرة البوت (لحل مشكلة الروابط الطويلة)
# ==========================================
user_urls = {}

# ==========================================
# كود البوت الأساسي
# ==========================================
def generate_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    # أزلنا الرابط من الأزرار لتجنب خطأ 400 في تيليجرام
    btn_audio = InlineKeyboardButton("🎵 Audio / صوت (MP3)", callback_data="audio")
    btn_vid_low = InlineKeyboardButton("🎥 Medium Quality / جودة متوسطة", callback_data="low")
    btn_vid_high = InlineKeyboardButton("🎬 High Quality / جودة عالية", callback_data="high")
    
    markup.add(btn_vid_high, btn_vid_low, btn_audio)
    return markup

base_ydl_opts = {
    'quiet': True,
    'noplaylist': True,
    'geo_bypass': True,
    'extractor_args': {'youtube': ['client=android,ios']}
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "**Welcome! / أهلاً بك!** 🚀\n\n"
        "🇬🇧 Send me any video link (YouTube, TikTok, Instagram...) and I will download it for you.\n"
        "🇸🇦 أرسل لي أي رابط فيديو وسأقوم بتحميله لك فوراً."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def handle_link(message):
    chat_id = message.chat.id
    
    # استخراج الرابط النظيف بدقة متناهية متجاهلاً الأقواس
    match = re.search(r'(https?://[^\s\)\]]+)', message.text)
    if not match:
        bot.send_message(chat_id, "❌ لم أتمكن من العثور على رابط صالح.")
        return
        
    clean_url = match.group(1)
    # حفظ الرابط في ذاكرة البوت المرتبطة برقم الشات الخاص بك
    user_urls[chat_id] = clean_url
    
    msg = bot.send_message(chat_id, "⏳ Analyzing link... / جاري تحليل الرابط...")
    
    try:
        ydl_opts = base_ydl_opts.copy()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            title = info.get('title', 'Unknown Video')
        
        bot.edit_message_text(
            f"✅ **Video:** `{title}`\n\nChoose format / اختر الصيغة:",
            chat_id=chat_id, message_id=msg.message_id,
            reply_markup=generate_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        error_msg = str(e).split('\n')[0][:70]
        bot.edit_message_text(f"❌ خطأ من المصدر:\n`{error_msg}...`", chat_id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    action = call.data
    
    # استدعاء الرابط من الذاكرة
    url = user_urls.get(chat_id)
    if not url:
        bot.edit_message_text("❌ انتهت صلاحية الجلسة، أرسل الرابط من جديد.", chat_id, msg_id)
        return
    
    bot.edit_message_text("⬇️ Downloading... Please wait / جاري التحميل... يرجى الانتظار", chat_id, msg_id)
    os.makedirs('downloads', exist_ok=True)
    
    ydl_opts = base_ydl_opts.copy()
    ydl_opts['outtmpl'] = f'downloads/{chat_id}_%(id)s.%(ext)s'

    if action == 'audio':
        ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]})
    elif action == 'low':
        ydl_opts.update({'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best[height<=480]'})
    elif action == 'high':
        ydl_opts.update({'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'})

    downloaded_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            if action == 'audio':
                downloaded_file = downloaded_file.rsplit('.', 1)[0] + '.mp3'

        bot.edit_message_text("📤 Uploading to Telegram... / جاري الإرسال...", chat_id, msg_id)
        caption_text = "✨ Downloaded via / تم التحميل بواسطة:\n👨‍💻 Dev: Anas Sadeq"
        
        with open(downloaded_file, 'rb') as file:
            if action == 'audio':
                bot.send_audio(chat_id, file, caption=caption_text)
            else:
                bot.send_video(chat_id, file, caption=caption_text)
                
        bot.delete_message(chat_id, msg_id)
    except Exception as e:
        error_msg = str(e).split('\n')[0][:70]
        bot.edit_message_text(f"⚠️ خطأ أثناء التحميل:\n`{error_msg}...`", chat_id, msg_id)
    finally:
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

# ==========================================
# تشغيل الخوادم معاً
# ==========================================
keep_alive()
bot.infinity_polling()
