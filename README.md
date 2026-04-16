# Resume Analysis System

Система для анализа резюме с помощью Telegram бота и REST API.

## Описание

Проект состоит из двух основных компонентов:
- **Telegram бот** - позволяет пользователям загружать резюме в формате PDF или DOCX и получать извлеченный текст и навыки
- **FastAPI сервер** - предоставляет REST API для программной обработки резюме

## Возможности

- Извлечение текста из PDF и DOCX файлов
- Автоматическое определение навыков (skills) из резюме
- Telegram бот с командами `/start`, `/resume`, `/search`
- REST API для интеграции с другими системами
- Логирование всех операций
- Валидация файлов (размер, формат)

## Технологии

- Python 3.x
- aiogram - Telegram бот
- FastAPI - веб фреймворк
- PyPDF2 - чтение PDF файлов
- docx2txt - чтение DOCX файлов
- uvicorn - ASGI сервер

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd Resume
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `requirements.txt` (если отсутствует):
```
aiogram
fastapi
uvicorn
python-multipart
PyPDF2
docx2txt
```

## Настройка

### Telegram Bot

Для работы бота необходимо установить токен в файле `app.py`:
```python
bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN")
```

Получить токен можно у [@BotFather](https://t.me/botfather) в Telegram.

## Использование

### Запуск обоих сервисов

Для одновременного запуска бота и API сервера:

```bash
python run.py
```

### Запуск только Telegram бота

```bash
python app.py
```

### Запуск только API сервера

```bash
python api.py
```

Или с использованием uvicorn:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Telegram Bot Команды

- `/start` - Начало работы с ботом
- `/resume` - Загрузка резюме
- `/search` - Поиск вакансий (демо)

## API Эндпоинты

### POST /analyze-resume

Загрузка и анализ резюме.

**Запрос:**
- Method: POST
- Content-Type: multipart/form-data
- Body: файл с именем `file`

**Пример с curl:**
```bash
curl -X POST "http://localhost:8000/analyze-resume" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

**Ответ:**
```json
{
  "text": "Извлеченный текст резюме...",
  "skills": ["Python", "SQL", "FastAPI"],
  "text_length": 1234,
  "file_info": {
    "pages": 2,
    "type": "pdf"
  },
  "filename": "resume.pdf",
  "file_size": 45678,
  "request_id": "abc12345"
}
```

### GET /

Проверка работы API.

**Ответ:**
```json
{
  "message": "Resume Analysis API is running"
}
```

### GET /health

Проверка здоровья сервиса.

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Структура проекта

```
Resume/
├── app.py              # Telegram бот
├── api.py              # FastAPI сервер
├── file_processor.py   # Обработка файлов
├── run.py              # Скрипт запуска сервисов
├── requirements.txt    # Зависимости
└── README.md          # Документация
```

## Определяемые навыки

Система автоматически определяет следующие навыки:
- Python, SQL, FastAPI, Docker
- JavaScript, React, PostgreSQL
- Git, MongoDB, Redis
- AWS, Linux, Django, Flask
- HTML, CSS

## Логирование

Все операции логируются в:
- Консоль
- Файл `api.log` (для API)

## Ограничения

- Максимальный размер файла: 10 MB
- Поддерживаемые форматы: PDF, DOCX
- Максимальная длина извлеченного текста: 4000 символов

