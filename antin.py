# pip install telethon
from telethon import TelegramClient, events, sync
from telethon.tl.types import MessageMediaPhoto

api_id = '24517020'
api_hash = '4d926de9ca53d0caa6cf3923df6c9475'
phone = '+380634759992'

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Читання адрес каналів з файлу
    with open('channels.txt', 'r') as file:
        channels = [line.strip() for line in file.readlines()]

    # Отримання ідентифікаторів каналів і слідкування за ними
    for channel_url in channels:
        channel = await client.get_entity(channel_url)
        @client.on(events.NewMessage(chats=channel))
        async def handler(event):
            message = event.message
            if message.media and isinstance(message.media, MessageMediaPhoto):
                media = message.media.photo
                print(f"Message from {channel.title} at {message.date}: {message.text}")
                print(f"Image ID: {media.id}")
            else:
                print(f"Message from {channel.title} at {message.date}: {message.text}")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
