from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import smtplib, asyncio

default_smtp_server = "smtp.gmail.com"
default_smtp_port = 465

# أخذ المعلومات من المستخدم
def get_user_input():
    subject = 'Telegram пожалуйста, помогите мне'
    body = '''Привет Telegram, мою группу заблокировали по ошибке. Вандалы разместили порнографические фотографии и обвинили нас в их публикации. Пожалуйста, снимите групповые ограничения.

Ссылка на группу: https: https://t.me/+Hob1xI1LY8kwOTcy

Идентификатор группы : 1784332159'''
    recipient = 'abuse@telegram.org'
    sender_email = 'a8919832@gmail.com'
    password = 'kofd jgki muzi zwet'
    return subject, body, recipient, sender_email, password

# إنشاء رسالة الإيميل
def create_email_message(subject, body, recipient, sender_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient
    message.attach(MIMEText(body, "plain"))
    return message

# إرسال الرسالة عبر SMTP
async def send_email_loop(message, sender_email, password, recipient, count=100):
    try:
        with smtplib.SMTP_SSL(default_smtp_server, default_smtp_port) as server:
            server.login(sender_email, password)
            for i in range(count):
                server.sendmail(sender_email, recipient, message.as_string())
                print(f"✅ تم إرسال الرسالة رقم {i+1}")
    except smtplib.SMTPException:
        print("❌ فشل الإرسال: تحقق من البريد أو كلمة المرور أو أنك وصلت الحد اليومي.")
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

# تشغيل الأداة
async def main():
    print("🔧 أداة إرسال الكليشة إلى تيليجرام Abuse")
    subject, body, recipient, sender_email, password = get_user_input()

    message = create_email_message(subject, body, recipient, sender_email)

    print("\n✅ تم إنشاء الرسالة. سيتم البدء بالإرسال خلال ثوانٍ...\n")
    await send_email_loop(message, sender_email, password, recipient)

if __name__ == "__main__":
    asyncio.run(main())
