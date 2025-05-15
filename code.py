from database import add_user_to_db, is_user_allowed, delete_user_from_db, get_allowed_users # type: ignore
from telethon import TelegramClient, events, Button
from email.mime.multipart import MIMEMultipart
from models import Base, engine # type: ignore
from email.mime.text import MIMEText
from datetime import datetime
import asyncio, smtplib, os
default_smtp_server = "smtp.gmail.com"
default_smtp_port = 465
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
user_states = {}
def create_email_message(subject, body, recipient):
    return f"Subject: {subject}\nTo: {recipient}\n\n{body}"
ABH = TelegramClient('session_name', api_id, api_hash)
@ABH.on(events.NewMessage(pattern='/help'))
async def help(event):
    await event.reply('هلا والله \n 1- /start ⇠ ل بدء تعيين الكلايش \n 2- **الكليشة الصغيره** لتعيين الكليشة الصغيره والتي تكون  موضوع الرساله\n 3- **الكليشة الكبيره** لتعيين الكليشة الاساسية والتي تكون هي الرساله الاساسية \n 4- **المستلم** يمكنك تحديد اي مستلم لكن الابلاغ على مجموعات التلكرام يكون abouse \n 5- **ايميل المرسل** ايميل حسابك لازم يكون حقيقي مفعل بي تحقق وامان الحساب \n 6- **باسورد** لازم يكون نفس الموجود بالفيديو في خطوه تعيين الباسورد')
@ABH.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    if not is_user_allowed(user_id):
        await event.respond("عذراً** , البوت ليس مجاني , للاشتراك 👇** \n المطور @TT_OTbot", file="موارد/abhpic.jpg")
        return
    if user_id in user_states and all(key in user_states[user_id] for key in ['subject', 'body', 'recipient', 'sender_email', 'password']):
        buttons = [[Button.inline("نعم، أريد الشد", b"send_email")], [Button.inline("لا، أريد البدء من جديد", b"restart")]]
        await event.respond("جميع المعلومات موجودة بالفعل. هل تريد الشد؟", buttons=buttons)
    else:
        await event.respond("اهلا اخي عندك طاقة تشد؟ استثمرها هنا", buttons=[[Button.inline("إنشاء رسالة", b"create_message")]])
@ABH.on(events.CallbackQuery(data=b"restart"))
async def restart(event):
    user_states[event.sender_id] = {}
    await event.respond("تم إعادة تعيين الحالة. يمكنك البدء من جديد باستخدام /start.")
@ABH.on(events.CallbackQuery(data=b"create_message"))
async def create_message(event):    
    user_states[event.sender_id] = {'step': 'get_subject'}
    await event.respond("أرسل الموضوع (الكليشة القصيرة)")
@ABH.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender_id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    step = state.get('step')
    if step is None:
        user_states[user_id]['step'] = 'get_subject'
        step = 'get_subject'
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
        await event.respond("أرسل كلمة المرور (كلمة مرور التطبيق كما في الفيديو)", file="https://t.me/recoursec/2")
    elif step == 'get_password':
        state['password'] = event.text
        if not all([state.get('subject'), state.get('body'), state.get('recipient'), state.get('sender_email'), state.get('password')]):
            await event.respond("يرجى التأكد من إدخال جميع المعلومات. حاول مجددًا.")
            user_states[user_id] = {}
            return
        email_message = create_email_message(state['subject'], state['body'], state['recipient'])
        await event.respond(f"تم إنشاء الكليشة التالية:\n\n{email_message}\n\nاضغط على الزر أدناه لإرسالها", buttons=[[Button.inline("إرسال الرسالة", b"send_email")]])
        state['step'] = 'confirm_send'
@ABH.on(events.CallbackQuery(data=b"send_email"))
async def send_email(event):
    user_id = event.sender_id
    if user_id not in user_states or user_states[user_id].get('step') != 'confirm_send':
        await event.respond("أحدا أو كل المعلومات فيها نقص. \n حاول مره أخرى مع /start")
        return
    state = user_states[user_id]
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
    except smtplib.SMTPException as e:
        await event.respond("اما وصلت الى الحد اليومي او هنالك خطأ في الايميل او الباسورد")
    except Exception as e:
        await event.respond("اما وصلت الى الحد اليومي او هنالك خطأ في الايميل او الباسورد")
@ABH.on(events.NewMessage(pattern=r'اضف (\d+)'))
async def add_me(event):
    if event.sender_id != 1910015590:
        return
    user_id = int(event.pattern_match.group(1))
    add_user_to_db(user_id)
    await event.respond(f"تمت إضافة المستخدم `{user_id}` إلى قائمة المسموح لهم في: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}.")
@ABH.on(events.NewMessage(pattern=r'حذف (\d+)'))
async def delete_me(event):
    if event.sender_id != 1910015590:
        return
    user_id = int(event.pattern_match.group(1))
    if delete_user_from_db(user_id):
        await event.respond(f"تم حذف المستخدم `{user_id}` من قائمة المستخدمين المسموح لهم.")
    else:
        await event.respond("لا يوجد هكذا مستخدم")
@ABH.on(events.NewMessage(pattern='/list'))
async def list_users(event):
    if event.sender_id != 1910015590:
        return
    users = get_allowed_users()
    if users:
        await event.respond("قائمة المستخدمين المسموح لهم:\n" + "\n".join([f"(`{user.user_id}`) - {user.added_at.strftime('%Y-%m-%d %I:%M:%S %p')}" for user in users]))
    else:
        await event.respond("لا يوجد اشخاص متاح لهم البوت...")
ABH.start(bot_token=bot_token)
ABH.run_until_disconnected()
