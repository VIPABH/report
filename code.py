from telethon import TelegramClient, events, Button
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio, smtplib, os

# إعدادات SMTP الافتراضية
default_smtp_server = "smtp.gmail.com"
default_smtp_port = 465

# تحميل بيانات التشغيل من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إدارة حالات المستخدمين
user_states = {}

# إنشاء رسالة البريد
def create_email_message(subject, body, recipient):
    return f"Subject: {subject}\nTo: {recipient}\n\n{body}"

# تهيئة البوت
ABH = TelegramClient('session_name', api_id, api_hash)

# أمر /help
@ABH.on(events.NewMessage(pattern='/help'))
async def help(event):
    await event.reply(
        'هلا والله \n'
        '1- /start ⇠ ل بدء تعيين الكلايش\n'
        '2- **الكليشة الصغيره** لتعيين عنوان الرسالة\n'
        '3- **الكليشة الكبيره** لتعيين نص الرسالة\n'
        '4- **المستلم** يمكنك تحديد أي مستلم مثل abuse@telegram.org\n'
        '5- **ايميل المرسل** يجب أن يكون حقيقيًا ومفعّلًا\n'
        '6- **باسورد** يجب أن يكون "App Password" كما بالفيديو'
    )

# أمر /start
@ABH.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    state = user_states.get(user_id, {})
    if all(k in state for k in ['subject', 'body', 'recipient', 'sender_email', 'password']):
        buttons = [
            [Button.inline("نعم، أريد الشد", b"send_email")],
            [Button.inline("لا، أريد البدء من جديد", b"restart")]
        ]
        await event.respond("جميع المعلومات موجودة بالفعل. هل تريد الشد؟", buttons=buttons)
    else:
        await event.respond("اهلا اخي عندك طاقة تشد؟ استثمرها هنا", buttons=[[Button.inline("إنشاء رسالة", b"create_message")]])

# إعادة التهيئة
@ABH.on(events.CallbackQuery(data=b"restart"))
async def restart(event):
    user_states[event.sender_id] = {}
    await event.respond("تم إعادة تعيين الحالة. يمكنك البدء من جديد باستخدام /start.")

# بدء إدخال الرسالة
@ABH.on(events.CallbackQuery(data=b"create_message"))
async def create_message(event):    
    user_states[event.sender_id] = {'step': 'get_subject'}
    await event.respond("أرسل الموضوع (الكليشة القصيرة)")

# إدارة مراحل الإدخال
@ABH.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender_id
    if user_id not in user_states:
        return

    state = user_states[user_id]
    step = state.get('step', 'get_subject')

    if step == 'get_subject':
        state['subject'] = event.text
        state['step'] = 'get_body'
        await event.respond("أرسل نص الكليشة (الكليشة الكبيرة)")

    elif step == 'get_body':
        state['body'] = event.text
        state['step'] = 'get_recipient'
        await event.respond("أرسل الإيميل المستلم (`abuse@telegram.org`)")

    elif step == 'get_recipient':
        state['recipient'] = event.text
        state['step'] = 'get_email'
        await event.respond("أرسل بريدك الإلكتروني (المرسل)")

    elif step == 'get_email':
        state['sender_email'] = event.text
        state['step'] = 'get_password'
        await event.respond("أرسل كلمة مرور التطبيق (App Password)", file="https://t.me/recoursec/2")

    elif step == 'get_password':
        state['password'] = event.text

        if not all(state.get(k) for k in ['subject', 'body', 'recipient', 'sender_email', 'password']):
            await event.respond("يرجى التأكد من إدخال جميع المعلومات. حاول مجددًا.")
            user_states[user_id] = {}
            return

        email_preview = create_email_message(state['subject'], state['body'], state['recipient'])
        await event.respond(
            f"تم إنشاء الكليشة التالية:\n\n{email_preview}\n\nاضغط على الزر أدناه لإرسالها",
            buttons=[[Button.inline("إرسال الرسالة", b"send_email")]]
        )
        state['step'] = 'confirm_send'

# تنفيذ الإرسال
@ABH.on(events.CallbackQuery(data=b"send_email"))
async def send_email(event):
    user_id = event.sender_id
    state = user_states.get(user_id, {})
    
    if state.get('step') != 'confirm_send':
        await event.respond("أحدا أو كل المعلومات فيها نقص. \n حاول مره أخرى مع /start")
        return

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = state['subject']
        message["From"] = state['sender_email']
        message["To"] = state['recipient']
        message.attach(MIMEText(state['body'], "plain"))

        with smtplib.SMTP_SSL(default_smtp_server, default_smtp_port) as server:
            server.login(state['sender_email'], state['password'])
            for i in range(100):
                server.sendmail(state['sender_email'], state['recipient'], message.as_string())
                await event.respond(f"تم الإرسال {i+1} بنجاح")
                await asyncio.sleep(2)

    except Exception:
        await event.respond("اما وصلت الى الحد اليومي او هنالك خطأ في الايميل او الباسورد")

# تشغيل البوت
ABH.start(bot_token=bot_token)
ABH.run_until_disconnected()
