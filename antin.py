# pip install telethon
import os
import sys
import logging
from datetime import datetime
from telethon import TelegramClient, events, sync
from telethon.tl.types import MessageMediaPhoto
from config import api_id, api_hash, bot_token

# Створюємо директорії для логів та повідомлень якщо вони не існують
os.makedirs('logs', exist_ok=True)
os.makedirs('messages', exist_ok=True)

# Налаштування логування
def setup_logging():
    # Встановлюємо кодування для виводу в консоль
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    log_filename = f'logs/telegram_bot_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Налаштування форматування
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Налаштування файлового хендлера з UTF-8 кодуванням
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Налаштування консольного хендлера
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Налаштування логера
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Ініціалізація логера
logger = setup_logging()

client = TelegramClient('session_name', api_id, api_hash)

def save_message_to_file(channel_title, message_date, message_text, media_info=None):
    # Створюємо файл для каналу (або відкриваємо існуючий)
    filename = f'messages/{channel_title}_{message_date.strftime("%Y%m%d")}.txt'
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Дата: {message_date}\n")
        f.write(f"Текст: {message_text}\n")
        if media_info:
            f.write(f"Медіа: {media_info}\n")
        f.write(f"{'='*50}\n")

async def main():
    # Читання адрес каналів з файлу
    try:
        with open('channels.txt', 'r') as file:
            channels = [line.strip() for line in file.readlines()]
        logger.info(f"Завантажено {len(channels)} каналів для моніторингу")
    except FileNotFoundError:
        logger.error("Файл channels.txt не знайдено!")
        return
    except Exception as e:
        logger.error(f"Помилка при читанні channels.txt: {str(e)}")
        return

    # Отримання ідентифікаторів каналів і слідкування за ними
    for channel_url in channels:
        try:
            channel = await client.get_entity(channel_url)
            client.add_event_handler(create_handler(channel), events.NewMessage(chats=channel))
            logger.info(f"Успішно підключено до каналу: {channel.title}")
        except Exception as e:
            logger.error(f"Помилка при підключенні до каналу {channel_url}: {str(e)}")

def create_handler(channel):
    async def handler(event):
        try:
            message = event.message
            logger.info(f"Отримано нове повідомлення з каналу '{channel.title}'")
            
            # Логуємо деталі повідомлення
            log_message = (
                f"\nКанал: {channel.title}"
                f"\nДата: {message.date}"
                f"\nID повідомлення: {message.id}"
                f"\nДовжина тексту: {len(message.text) if message.text else 0} символів"
            )
            
            if message.media and isinstance(message.media, MessageMediaPhoto):
                media = message.media.photo
                media_info = f"Photo (ID: {media.id})"
                log_message += f"\nТип медіа: Фото (ID: {media.id})"
                logger.info(f"Повідомлення містить фото, ID: {media.id}")
            else:
                media_info = None
                log_message += "\nТип медіа: Немає"
            
            logger.info(log_message)
                
            # Зберігаємо повідомлення у файл
            save_message_to_file(
                channel.title,
                message.date,
                message.text if message.text else "[Немає тексту]",
                media_info
            )
            
            logger.info(f"Повідомлення з каналу '{channel.title}' успішно збережено")
            
        except Exception as e:
            logger.error(f"Помилка при обробці повідомлення з каналу '{channel.title}': {str(e)}")
            
    return handler

def main_wrapper():
    logger.info("="*50)
    logger.info("Запуск бота...")
    logger.info(f"Версія Python: {sys.version}")
    logger.info(f"Поточна директорія: {os.getcwd()}")
    logger.info(f"Кодування консолі: {sys.stdout.encoding}")
    
    try:
        with client:
            client.connect()
            logger.info("Підключення до Telegram API встановлено")
            
            if not client.is_user_authorized():
                client.start(bot_token=bot_token)
                logger.info("Успішна авторизація за допомогою бот токена")
                
            client.loop.run_until_complete(main())
            logger.info("Бот успішно запущений і очікує повідомлення")
            client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Отримано сигнал завершення роботи")
    except Exception as e:
        logger.error(f"Критична помилка: {str(e)}")
    finally:
        logger.info("Завершення роботи бота")
        logger.info("="*50)

if __name__ == "__main__":
    main_wrapper()
