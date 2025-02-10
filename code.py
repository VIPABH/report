from telethon import TelegramClient, events, Button
import os
from database import add_user_to_db, is_user_allowed, delete_user_from_db, get_allowed_users # type: ignore
from models import Base, engine # type: ignore
from datetime import datetime
from telethon import TelegramClient, events, Button
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os, asyncio, smtplib

default_smtp_server = "smtp.gmail.com"
default_smtp_port = 465
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

user_states = {}
def create_email_message(subject, body, recipient):
    return f"Subject: {subject}\nTo: {recipient}\n\n{body}"
client = TelegramClient('session_name', api_id, api_hash)
Base.metadata.create_all(bind=engine)
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    if not is_user_allowed(user_id):
        await event.respond("عذراً** , انت لست مشترك في البوت** \n المطور @k_4x1", file="موارد/photo_2025-02-10_11-40-17.jpg")
        return
    user_id = event.sender_id
    if user_id in user_states and all(key in user_states[user_id] for key in ['subject', 'body', 'recipient', 'sender_email', 'password']):
        buttons = [
            [Button.inline("نعم، أريد الشد", b"send_email")],
            [Button.inline("لا، أريد البدء من جديد", b"restart")]
        ]
        await event.respond(
            "جميع المعلومات موجودة بالفعل. هل تريد الشد؟",
            buttons=buttons
        )
    else:
        buttons = [
            [Button.inline("إنشاء رسالة", b"create_message")]
        ]
        await event.respond(
            "اهلا اخي حياك الله , البوت مدفوع يرفع بلاغات بصوره امنة وحقيقية \n المطور @K_4X1",
            buttons=buttons
        )
@client.on(events.CallbackQuery(data=b"restart"))
async def restart(event):
    user_states[event.sender_id] = {}
    await event.edit("تم إعادة تعيين الحالة. يمكنك البدء من جديد باستخدام /start.")

@client.on(events.CallbackQuery(data=b"create_message"))
async def create_message(event):
    user_states[event.sender_id] = {'step': 'get_subject'}
    await event.edit("أرسل الموضوع (الكليشة القصيرة)")

@client.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender_id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    step = state['step']
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
        await event.respond("أرسل بريدك الإلكتروني (الايميل الذي تريد منه الارسال)")
    elif step == 'get_email':
        state['sender_email'] = event.text
        state['step'] = 'get_password'
        await event.respond(
            "أرسل كلمة المرور (كلمة مرور التطبيق كما في الفيديو)",
            file="https://t.me/recoursec/2"
        )
    elif step == 'get_password':
        state['password'] = event.text
        subject = state.get('subject')
        body = state.get('body')
        recipient = state.get('recipient')
        sender_email = state.get('sender_email')
        password = state.get('password')
        if not all([subject, body, recipient, sender_email, password]):
            await event.respond("يرجى التأكد من إدخال جميع المعلومات. حاول مجددًا.")
            user_states[user_id] = {}  # Reset state for user
            return
        email_message = create_email_message(subject, body, recipient)
        buttons = [
            [Button.inline("إرسال الرسالة", b"send_email")]
        ]
        await event.respond(
            f"تم إنشاء الكليشة التالية:\n\n{email_message}\n\nاضغط على الزر أدناه لإرسالها",
            buttons=buttons
        )
        state['step'] = 'confirm_send'
@client.on(events.CallbackQuery(data=lambda data: data.startswith(b"a")))
async def handle_a_buttons(event):
    await send_email(event)
@client.on(events.CallbackQuery(data=b"send_email"))
async def send_email(event):
    user_id = event.sender_id
    if user_id not in user_states or user_states[user_id].get('step') != 'confirm_send':
        await event.edit("أحدا أو كل المعلومات فيها نقص. \n حاول مره أخرى مع /start")
        return
    state = user_states[user_id]
    subject = state['subject']
    body = state['body']
    recipient = state['recipient']
    sender_email = state['sender_email']
    password = state['password']
@client.on(events.CallbackQuery(data=lambda data: data.startswith(b"a")))
async def handle_a_buttons(event):
    await send_email(event)

@client.on(events.CallbackQuery(data=b"send_email"))
async def send_email(event):
    user_id = event.sender_id
    if user_id not in user_states or user_states[user_id].get('step') != 'confirm_send':
        await event.edit("أحدا أو كل المعلومات فيها نقص. \n حاول مره أخرى مع /start")
        return
    state = user_states[user_id]
    subject = state['subject']
    body = state['body']
    recipient = state['recipient']
    sender_email = state['sender_email']
    password = state['password']
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL(default_smtp_server, default_smtp_port) as server:
            server.login(sender_email, password)
            for i in range(100):
                server.sendmail(sender_email, recipient, message.as_string())
                if i == 0:
                    await event.edit(f"تم الإرسال {i+1} بنجاح")
                else:
                    await event.edit(f"تم الإرسال {i+1} بنجاح")
                await asyncio.sleep(1)
    except smtplib.SMTPException:
        pass
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r'اضف (\d+)'))
async def add_me(event):
    sender_id = event.sender_id
    if sender_id != 1910015590:
        return
    user_id = int(event.pattern_match.group(1))
    add_user_to_db(user_id)
    t1 = datetime.now()
    formatted_time = t1.strftime("%Y-%m-%d %I:%M:%S %p")
    await event.respond(f"تمت إضافة المستخدم `{user_id}` إلى قائمة المسموح لهم في: {formatted_time}.")

@client.on(events.NewMessage(pattern=r'حذف (\d+)'))
async def delete_me(event):
    sender_id = event.sender_id    
    if sender_id != 1910015590:
        return
    user_id = int(event.pattern_match.group(1))
    if delete_user_from_db(user_id):
        await event.respond(f"تم حذف المستخدم `{user_id}` من قائمة المستخدمين المسموح لهم.")
    else:
        await event.respond("لا يوجد هكذا مستخدم")

@client.on(events.NewMessage(pattern='/list'))
async def list_users(event):
    user_id = event.sender_id
    if user_id != 1910015590:
        await event.respond("عذرا صديقي , الامر خاص بالمطور فقط")
        return
    users = get_allowed_users()
    if users:
        user_list = "\n".join([f"(`{user.user_id}`) -  {user.added_at.strftime('%Y-%m-%d %I:%M:%S %p')}" for user in users])
        await event.respond(f"قائمة المستخدمين المسموح لهم:\n{user_list}")
    else:
        await event.respond("لا يوجد اشخاص متاح لهم البوت...")
client.start(bot_token=bot_token)
client.run_until_disconnected()
