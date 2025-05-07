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
    "BQGMcpgAmRp608NdyIJ49a5cMpvtgSayQns6Yftews_Ow-snguTqn10rcFrVq8LX1ybBhWMlmvpUKyJVFyFlJ22ymQIMJ7NQJth-ex3qqZVRu39w83OAZZXo7FyhQq7ivAlhiEG14G81vdTp2tKLFHmSLNidwc5anLL-xVJaycpVH_j82Kv9SLsn3EhYwk1hzvnu-Zsatj5VNH7WH1RS2znPEZejZom4l9wqiegReKFQnQNh3ldZ9_saKKc0BJPqmH2ZWlWUMpuGH8pB8osCWz1ZBH-J1qZA7R-tL1s4YBPhQNjnEgKO6fo2OQ8iuN1ibv4WgC4RxYx4Vky3afKtlrDhoeno5gAAAAGh48SPAA",
    "BQGMcpgApMUCqvW-_CVrwOjNC2wBaX6UAeRvDmQfeaWP4RUFn4mfNXlQLuRTQWTiV5H463aLMaq3vwERPiy0mQ1MyvSEXZNxrQJ_9_x0v0Bn1h1JvAYwt3hgbUmPnkmVZLqcsfC48jCsZb1gvTO_wSVsDXK9ah-CEC5F0FWClgZNewPai0I-FHEzY-opuH2n1PHMjeAJM7wANj10LmTAR5T0XrXLjJOd6fiBlJvykH3krB5KLAdTG8JqC-h_-c-B70I2VONMgVPewqy-kR9c1L5qEFRG7HzNztU6gqFYnDgomUGkkPPBwX9z_9lHKAF2G9UQAGumhnfTU35VU_EdgvMFavfi1AAAAAHRRT_uAA",
    "BAGMcpgAAzAYrfBgGVT0sP2hTaqE8a1zZkhFhTR2yq1xrh94SGlrzvPeDqgOy4HUpcvRUdz3MBTUB2oTCM_F645kwnyyoLFocQ0ViBiQHTNTZ9uCcirC6k4AEldWfrXLEFGrNIt3_TXSytegKSvBMqjXH9nrwhSPqrTpBK9X9Fkg3H35j22RnaFzBpmE3ZSpGDU4ptTYdprF_VFHNb7bdbrCzEdeYUf39Ye8IjIilQlsuKPtewaAtC7TTD6oBxHn6n2PRdtk54ZSnHAq7bYtTNkuuFvNLRA-40CvpeMFTXzunRTD1lfg1Oz9abPt5PsTz2GGCU-P4qFNWZ7J323uZ_pyo7xFAgAAAAG_Qa6bAA"
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

for acc_ind, app in enumerate(apps):
    try:
        app.add_handler(MessageHandler(_save_incoming_message, filters.private & filters.text))
        app.add_handler(DeletedMessagesHandler(_report_deleted_message))
        app.start()
    except Exception as e:
        print(acc_ind + 1, type(e).__name__)

bot.start()
print(f"@{bot.me.username} STARTED!")

idle()

for app in apps:
    try:
        app.stop()
    except:
        pass
bot.stop()
print("STOPPED!")
