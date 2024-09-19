# pip install telethon
from telethon import TelegramClient, events

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone = 'YOUR_PHONE_NUMBER'

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats='CHANNEL_USERNAME'))
async def handler(event):
    print(event.message.text)

client.start(phone)
client.run_until_disconnected()
