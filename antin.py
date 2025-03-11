# pip install telethon
from telethon import TelegramClient, events, sync
from telethon.tl.types import MessageMediaPhoto
from config import api_id, api_hash, bot_token

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Читання адрес каналів з файлу
    with open('channels.txt', 'r') as file:
        channels = [line.strip() for line in file.readlines()]

    # Отримання ідентифікаторів каналів і слідкування за ними
    for channel_url in channels:
        channel = await client.get_entity(channel_url)
        client.add_event_handler(create_handler(channel), events.NewMessage(chats=channel))

def create_handler(channel):
    async def handler(event):
        message = event.message
        if message.media and isinstance(message.media, MessageMediaPhoto):
            media = message.media.photo
            print(f"Message from {channel.title} at {message.date}: {message.text}")
            print(f"Image ID: {media.id}")
        else:
            print(f"Message from {channel.title} at {message.date}: {message.text}")
    return handler

with client:
    client.connect()  # Підключення без автентифікації
    if not client.is_user_authorized():
        client.start(phone=phone)  # Автентифікація тільки якщо потрібно
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
