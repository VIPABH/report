from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telethon import TelegramClient, events, Button
import smtplib, asyncio, os

# إعداد SMTP مع STARTTLS
default_smtp_server = "smtp.gmail.com"
default_smtp_port = 587  # تعديل المنفذ إلى 587

# إعداد API الخاصة بالبوت
api_id = int(os.getenv("API_ID", 123456))       # استبدل أو استخدم environment variables
api_hash = os.getenv("API_HASH", "your_api_hash")
bot_token = os.getenv("BOT_TOKEN", "your_bot_token")

# دالة إعداد الرسالة
def get_email_content():
    subject = 'Telegram пожалуйста, помогите мне'
    body = '''Привет Telegram, мою группу заблокировали по ошибке. Вандалы разместили порнографические фотографии и обвинили нас в их публикации. Пожалуйста, снимите групповые ограничения.

Ссылка на группу: https://t.me/+Hob1xI1LY8kwOTcy

Идентификатор группы : 1784332159'''
    recipient = 'abuse@telegram.org'
    sender_email = 'abh780988@gmail.com'
    password = 'xxpv aato gwnv mhlc'
    return subject, body, recipient, sender_email, password

# دالة إنشاء الرسالة
def create_email_message(subject, body, recipient, sender_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient
    message.attach(MIMEText(body, "plain"))
    return message

# دالة إرسال الإيميل
async def send_email_loop(event):
    subject, body, recipient, sender_email, password = get_email_content()
    message = create_email_message(subject, body, recipient, sender_email)

    await event.respond("🔄 جاري الإرسال، سيتم إرسال الرسالة 100 مرة...")

    try:
        with smtplib.SMTP(default_smtp_server, default_smtp_port) as server:
            server.ehlo()
            server.starttls()  # تفعيل STARTTLS
            server.login(sender_email, password)
            for i in range(100):
                server.sendmail(sender_email, recipient, message.as_string())
                await event.respond(f"✅ تم إرسال الرسالة رقم {i+1}")
                await asyncio.sleep(2)
    except smtplib.SMTPException:
        await event.respond("❌ فشل في الإرسال: تحقق من البريد أو كلمة المرور أو أنك وصلت الحد اليومي.")
    except Exception as e:
        await event.respond(f"❌ حدث خطأ غير متوقع: {e}")

# تشغيل البوت
bot = TelegramClient("emailbot", api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond("مرحباً، هل ترغب في إرسال الرسالة؟", buttons=[
        [Button.inline("نعم، أرسل الآن", b"send_now")],
        [Button.inline("إلغاء", b"cancel")]
    ])

@bot.on(events.CallbackQuery(data=b"send_now"))
async def handle_send_now(event):
    await send_email_loop(event)

@bot.on(events.CallbackQuery(data=b"cancel"))
async def handle_cancel(event):
    await event.edit("تم الإلغاء ✅")

bot.run_until_disconnected()
