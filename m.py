import os
import pytz

from pymongo import MongoClient

from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler, DeletedMessagesHandler


IST = pytz.timezone('Asia/Kolkata')

API_ID = 25981592
API_HASH = "709f3c9d34d83873d3c7e76cdd75b866"
BOT_TOKEN = "6052402912:AAGGodIAMUUwU1f-LkTEWhT-taqlj31TYsw"
SESSIONS = [
    "BAGMcpgAqyJFu3AABcNw_D5uL54JMNCZKqNxykOLDGPPPHHesgRoHMM4XACKDxsYhF3r9yb7OgT7QiNL5WFQNuZb5beJuMD9w-Fkh0kz2tWQT0YtbShsdb-zW4HjrdGk3LUxb6JUG4_pZQZkq0a5VVSMfRlQtCvIgdjv4ngGjJgQokU1PrAcc99WuR4KmmzdaM4Iv9RrOmd43-yvcQp9M1N54CZeiMsQKD34aZWcf0kHYkns8jFZrUg53I81M2EOOvejE75Ms9awiE_mL8frUcj8QvshKdBvG7FjL5q_n_ACoby7jwV3aXS6fPbvjfshdEuPVHYPVQGjOVPBKxdNrYLyDcrePQAAAAG_Qa6bAA",
    "BAGMcpgAjXnPqQXO_1welgUqE4gbpxpCEbgexm2KxTB_5Stm_VSLuzU_-fH5tOKufqgGaxcByPGU0_hM63NtY1WZy4KigXicUdmQ5yrGMVe6ZH4kYj1EnuxaKLHcPGhIyIENUJevPoMvFQjIVeKhg56nTUExrlWhu3hXieVP1uPkXGnR194TjdHytO71Mq7zf-AinLuYZaLMKBH93cXDgid0m_fPLY1M4Uczq9d86w45VqtWk9lTUI2-y5vJX_8sZ7BGn-mfqd1O9ix-wSh5DQ_87UXidh9n549vxROyfRmetBMuXb8016B13EGQrqIEBZXUHrWS7VfftchKqio7Cp2r4bsBsAAAAAHVxWm6AA"
]

_mongo_client_ = MongoClient("mongodb+srv://MIHIRxKHUSHI:print('MIKU1311')@thealtron.rwuawpe.mongodb.net/?retryWrites=true&w=majority")
ChatsCol = _mongo_client_['DeleteDetector']['Chats']

if not os.path.exists("cache"):
    os.mkdir("cache")

apps: list[Client] = []
for session in SESSIONS:
    app = Client("MBot", api_id=API_ID, api_hash=API_HASH, session_string=session, max_message_cache_size=0)
    apps.append(app)

bot = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, max_message_cache_size=3)


async def _save_incoming_message(client: Client, message: Message):
    from_user_name = message.from_user.first_name
    if message.from_user.last_name:
        from_user_name += " " + message.from_user.last_name
    if message.from_user.id != client.me.id:
        to_user = client.me
    else:
        to_user = message.chat
    to_user_name = to_user.first_name
    if to_user.last_name:
        to_user_name += " " + to_user.last_name
    ChatsCol.insert_one({"id": message.id, "from": from_user_name, "to": to_user_name, "time": message.date.astimezone(IST).strftime("%d-%m-%Y %H:%M:%S"), "text": message.text})


async def _report_deleted_message(client: Client, messages: list[Message]):
    message_ids = [message.id for message in messages]
    chats = ChatsCol.find({"id": {"$in": message_ids}})
    content = ""
    for chat in chats:
        content += f"#MESSAGE_{chat['id']}\n - FROM: {chat['from']}\n - TO: {chat['to']}\n - TIME: {chat['time']}\n - TEXT: {chat['text']}\n\n\n"
    if len(content) > 0:
        file_name = f"cache/{client.me.id}.txt"
        with open(file_name, "w", encoding="utf8") as file:
            file.write(content)
        caption = f"⚠️ MESSAGE_DELETE_DETECTED!\n\nAccount = {client.me.mention}\nDeleted = {len(message_ids)}"
        await bot.send_document("PyXen", file_name, caption=caption, file_name="Deleted_Messages.txt")
        await bot.send_document(7536250282, file_name, caption=caption, file_name="Deleted_Messages.txt")
        os.remove(file_name)

for app in apps:
    app.add_handler(MessageHandler(_save_incoming_message, filters.private & filters.text))
    app.add_handler(DeletedMessagesHandler(_report_deleted_message))
    app.start()
bot.start()
print("STARTED!")

idle()

for app in apps:
    app.stop()
bot.stop()
print("STOPPED!")
