# pip install telethon
import os
import sys
import logging
import re
from datetime import datetime
from telethon import TelegramClient, events, sync
from telethon.tl.types import MessageMediaPhoto
from config import api_id, api_hash

# Створюємо директорії для логів, повідомлень та медіа
os.makedirs('logs', exist_ok=True)
os.makedirs('messages', exist_ok=True)
os.makedirs('media', exist_ok=True)

def sanitize_filename(filename):
    # Видаляємо всі символи, крім букв, цифр, дефісу та підкреслення
    sanitized = re.sub(r'[^\w\-]', '_', filename)
    # Замінюємо множинні підкреслення на одне
    sanitized = re.sub(r'_+', '_', sanitized)
    # Видаляємо підкреслення з початку та кінця
    return sanitized.strip('_')

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

async def download_media(message, channel_title, message_date):
    """Завантажує медіа з повідомлення"""
    if not message.media:
        return None
        
    try:
        # Створюємо підпапку для каналу
        channel_folder = sanitize_filename(channel_title)
        media_path = os.path.join('media', channel_folder)
        os.makedirs(media_path, exist_ok=True)
        
        # Формуємо ім'я файлу з датою та ID повідомлення
        date_str = message_date.strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(media_path, f"{date_str}_{message.id}")
        
        # Завантажуємо медіа
        downloaded_path = await message.download_media(file_path)
        logger.info(f"Медіа збережено: {downloaded_path}")
        return downloaded_path
    except Exception as e:
        logger.error(f"Помилка при завантаженні медіа: {str(e)}")
        return None

def save_message_to_file(channel_title, message_date, message_text, media_info=None):
    # Використовуємо очищену назву каналу для файлу
    safe_channel_title = sanitize_filename(channel_title)
    filename = f'messages/{safe_channel_title}_{message_date.strftime("%Y%m%d")}.txt'
    
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Канал: {channel_title}\n")  # Зберігаємо оригінальну назву в тексті
            f.write(f"Дата: {message_date}\n")
            f.write(f"Текст: {message_text}\n")
            if media_info:
                f.write(f"Медіа: {media_info}\n")
            f.write(f"{'='*50}\n")
    except Exception as e:
        logger.error(f"Помилка при збереженні повідомлення: {str(e)}")

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
            
            media_info = None
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media = message.media.photo
                    # Завантажуємо медіа
                    downloaded_path = await download_media(message, channel.title, message.date)
                    media_info = f"Photo (ID: {media.id}, Path: {downloaded_path})"
                    log_message += f"\nТип медіа: Фото (ID: {media.id})"
                    logger.info(f"Повідомлення містить фото, ID: {media.id}")
                else:
                    # Спробуємо завантажити інші типи медіа
                    downloaded_path = await download_media(message, channel.title, message.date)
                    if downloaded_path:
                        media_info = f"Media (Path: {downloaded_path})"
                        log_message += f"\nТип медіа: Інше"
            else:
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
                logger.info("Необхідна авторизація. Введіть номер телефону:")
                client.start()
                logger.info("Успішна авторизація через номер телефону")
                
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
