# Инструкция по настройке проекта

## Шаг 1: Настройка переменных окружения

1. Создайте файл `.env` в корне проекта:
```bash
cp .env.example .env
```

2. Откройте `.env` и заполните следующие переменные:

```env
# OpenAI API (ОБЯЗАТЕЛЬНО)
# Получите ключ на https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Telegram Secret Key (сгенерируйте случайную строку)
TELEGRAM_SECRET_KEY=your_secret_key_here

# Database (можно оставить по умолчанию для разработки)
DATABASE_URL=postgresql://user:password@localhost:5432/clone_platform
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=clone_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# Backend URL
BACKEND_URL=http://localhost:8000

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Шаг 2: Создание Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте токен бота и вставьте в `.env` как `TELEGRAM_BOT_TOKEN`

## Шаг 3: Генерация секретного ключа

Сгенерируйте случайную строку для `TELEGRAM_SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Шаг 4: Запуск через Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend

# Остановка
docker-compose down
```

## Шаг 5: Применение миграций БД

После первого запуска нужно создать таблицы:

```bash
# Войдите в контейнер backend
docker-compose exec backend bash

# Создайте миграцию (первый раз)
alembic revision --autogenerate -m "Initial migration"

# Примените миграции
alembic upgrade head
```

Или создайте файл миграции вручную на основе схемы из `DATABASE_AND_AI_TRAINING.md`.

## Шаг 6: Настройка Mini App в Telegram

1. Разверните frontend на Vercel или другом хостинге
2. Получите URL вашего приложения (например: `https://your-app.vercel.app`)
3. Откройте @BotFather
4. Используйте команду `/setmenubutton` для вашего бота
5. Укажите URL вашего Mini App

## Шаг 7: Локальная разработка

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Проверка работы

1. Откройте вашего бота в Telegram
2. Нажмите кнопку меню (если настроена)
3. Должно открыться Mini App
4. Пройдите анкету
5. Создайте первый дневник

## Troubleshooting

### Ошибка подключения к БД
- Убедитесь, что PostgreSQL запущен: `docker-compose ps`
- Проверьте переменные окружения в `.env`

### Ошибка валидации Telegram
- Проверьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_SECRET_KEY`
- Убедитесь, что используете правильный формат initData

### Ошибка OpenAI API
- Проверьте `OPENAI_API_KEY` в `.env`
- Убедитесь, что на счету есть средства
