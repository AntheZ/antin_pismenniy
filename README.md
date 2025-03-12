# Telegram Channel Monitor

Скрипт для моніторингу та збереження повідомлень з Telegram каналів, включаючи текст та медіафайли.

## Функціонал

- Моніторинг декількох Telegram каналів одночасно
- Збереження текстових повідомлень у файли
- Автоматичне завантаження медіафайлів (фото та інші типи медіа)
- Детальне логування всіх подій
- Підтримка Unicode (емодзі, кирилиця тощо)

## Структура проекту

```
project/
├── logs/              # Логи роботи скрипта
├── messages/          # Текстові повідомлення
│   └── channel_name_date.txt
├── media/            # Медіафайли
│   └── channel_name/
│       └── date_messageid.*
├── antin.py          # Основний скрипт
├── config.py         # Конфігурація (API креди)
├── channels.txt      # Список каналів для моніторингу
└── README.md
```

## Налаштування

1. Створіть додаток на https://my.telegram.org/apps
2. Скопіюйте `config.py.example` в `config.py` та додайте свої API креди:
   ```python
   api_id = 'YOUR_API_ID'
   api_hash = 'YOUR_API_HASH'
   ```
3. Створіть файл `channels.txt` зі списком каналів для моніторингу:
   ```
   @channel_name
   https://t.me/channel_name
   ```

## Встановлення

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/AntheZ/antin_pismenniy.git
   cd antin_pismenniy
   ```

2. Встановіть залежності:
   ```bash
   pip install telethon
   ```

## Використання

1. Запустіть скрипт:
   ```bash
   python antin.py
   ```

2. При першому запуску введіть свій номер телефону та код підтвердження
3. Скрипт почне моніторити вказані канали та зберігати повідомлення

## Формат збереження даних

### Текстові повідомлення
- Зберігаються в папці `messages/`
- Окремий файл для кожного каналу з датою
- Формат: `channel_name_YYYYMMDD.txt`

### Медіафайли
- Зберігаються в папці `media/channel_name/`
- Назва файлу містить дату та ID повідомлення
- Формат: `YYYYMMDD_HHMMSS_messageid.extension`

### Логи
- Зберігаються в папці `logs/`
- Окремий файл для кожного дня
- Формат: `telegram_bot_YYYYMMDD.log`

## Безпека
- API креди зберігаються в окремому конфігураційному файлі
- Файл `config.py` додано до `.gitignore`
- Дані сесії зберігаються локально в зашифрованому вигляді
