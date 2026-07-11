import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
from flask import Flask
from threading import Thread

# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8466380764:AAHGrGBkp7iGBFdMYBc-f93tnvEw6H34pho"
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# إعداد سيرفر فلاسك (الخداع الهندسي للمنصة)
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
# كود البوت الأساسي
# ==========================================
def generate_markup(url):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    btn_audio = InlineKeyboardButton("🎵 Audio / صوت (MP3)", callback_data=f"audio|{url}")
    btn_vid_low = InlineKeyboardButton("🎥 Medium Quality / جودة متوسطة", callback_data=f"low|{url}")
    btn_vid_high = InlineKeyboardButton("🎬 High Quality / جودة عالية", callback_data=f"high|{url}")
    
    markup.add(btn_vid_high, btn_vid_low, btn_audio)
    return markup

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
    url = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "⏳ Analyzing link... / جاري تحليل الرابط...")
    
    try:
        ydl_opts = {'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Video')
        
        bot.edit_message_text(
            f"✅ **Video:** `{title}`\n\nChoose format / اختر الصيغة:",
            chat_id=chat_id, message_id=msg.message_id,
            reply_markup=generate_markup(url),
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text("❌ Invalid link or private video. / رابط غير صالح أو فيديو خاص.", chat_id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    action, url = call.data.split('|', 1)
    
    bot.edit_message_text("⬇️ Downloading... Please wait / جاري التحميل... يرجى الانتظار", chat_id, msg_id)
    os.makedirs('downloads', exist_ok=True)
    
    ydl_opts = {
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

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
        bot.edit_message_text("⚠️ Error: File too large or protected / خطأ: الملف كبير جداً أو محمي", chat_id, msg_id)
    finally:
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

# ==========================================
# تشغيل الخوادم معاً
# ==========================================
keep_alive()
print("Bilingual Bot is running securely on Render...")
bot.infinity_polling()
