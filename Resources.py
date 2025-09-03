from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors import ChatForwardsRestrictedError
from telethon.tl.types import ChatParticipantCreator
from telethon.tl.types import ReactionEmoji
import google.generativeai as genai
import pytz, os, json
from ABH import ABH
developers = {}
def delsave(dev_id=None, filename="secondary_devs.json"):
    if filename is None:
        return
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    if dev_id is None:
        return data
    if ":" not in dev_id:
        return data
    parts = dev_id.split(":", 1)
    if len(parts) != 2:
        return data
    chat_id, dev_id_num = parts
    if chat_id in data and dev_id_num in data[chat_id]:
        data[chat_id].remove(dev_id_num)
        if not data[chat_id]:
            del data[chat_id]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
def save(dev_id=None, filename="secondary_devs.json"):
    if filename is None:
        return
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    if dev_id is None:
        return data
    if ":" not in dev_id:
        return data
    parts = dev_id.split(":", 1)
    if len(parts) != 2:
        return data
    chat_id, dev_id_num = parts
    if chat_id not in data:
        data[chat_id] = []
    if dev_id_num not in data[chat_id]:
        data[chat_id].append(dev_id_num)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
async def react(event, x):
    try:    
        await ABH(SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.id,
            reaction=[ReactionEmoji(emoticon=f'{x}')],
            big=True
        ))
    except Exception as e:
        await ABH(SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.message.id,
            reaction=[ReactionEmoji(emoticon=f'{x}')],
            big=True
        ))        
def adj(filename: str, data: dict):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}
    existing_data.update(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
async def hint(e):
    await ABH.send_message(wfffp, str(e))
async def mention(event):
    name = getattr(event.sender, 'first_name', None) or 'غير معروف'
    user_id = event.sender_id
    return f"[{name}](tg://user?id={user_id})"
