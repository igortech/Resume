import os
import tempfile
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import docx2txt
import PyPDF2
from datetime import datetime
from file_processor import FileProcessor

bot = Bot(token="5846524648:AAHHUAFkJxHWCNMvqp_FlVNk5iWxnQeR3_M")
dp = Dispatcher()
file_processor = FileProcessor()

#bot.send_message(5846524648, "Бот запущен!")


def log_action(action: str, user_id: int, username: str = "", additional_info: str = ""):
    """Логирование действий бота"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"@{username}" if username else f"ID:{user_id}"
    info = f" | {additional_info}" if additional_info else ""
    print(f"[{timestamp}] {action} | User: {user_info}{info}")

# Обработчик команды /start
@dp.message(Command("start"))
async def handle_start(message: types.Message):
    log_action("START", message.from_user.id, message.from_user.username)
    await message.answer("Добро пожаловать! Отправьте файл резюме или используйте команды /resume или /search")

# Обработчик команды /resume
@dp.message(Command("resume"))
async def handle_resume(message: types.Message):
    log_action("RESUME_COMMAND", message.from_user.id, message.from_user.username)
    await message.answer("Пожалуйста, отправьте файл в формате PDF или DOCX")

# Обработчик для документов (файлов)
@dp.message(F.document)
async def handle_document(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    file_name = message.document.file_name
    file_size = message.document.file_size
    
    log_action("FILE_RECEIVED", user_id, username, f"File: {file_name} ({file_size} bytes)")
    
    if not message.document.file_name.endswith(('.pdf', '.docx')):
        log_action("UNSUPPORTED_FILE", user_id, username, f"File: {file_name}")
        return await message.answer("Поддерживаются только PDF и DOCX файлы")

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, message.document.file_name)
        await bot.download(message.document, destination=file_path)
        log_action("FILE_DOWNLOADED", user_id, username, f"Path: {file_path}")
        
        try:
            file_processor()
            if message.document.file_name.endswith('.pdf'):
                log_action("PROCESSING_PDF", user_id, username, f"File: {file_name}")
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join([page.extract_text() for page in reader.pages])
                    pages_count = len(reader.pages)
                    log_action("PDF_PROCESSED", user_id, username, f"Pages: {pages_count}")
            else:
                log_action("PROCESSING_DOCX", user_id, username, f"File: {file_name}")
                text = docx2txt.process(file_path)
                log_action("DOCX_PROCESSED", user_id, username, f"File: {file_name}")
            
            # Обрезаем текст если он слишком длинный
            text_length = len(text)
            if text_length > 4000:
                text = text[:4000] + "..."
                log_action("TEXT_TRIMMED", user_id, username, f"Original: {text_length} chars")
                
            log_action("TEXT_EXTRACTED", user_id, username, f"Chars: {min(text_length, 4000)}")
            await message.answer(f"Текст резюме:\n\n{text}")
            log_action("RESPONSE_SENT", user_id, username, "Text extraction successful")
            
        except Exception as e:
            error_msg = f"Ошибка при обработке файла: {str(e)}"
            log_action("PROCESSING_ERROR", user_id, username, f"Error: {str(e)}")
            await message.answer(error_msg)

# Заглушки вакансий
VACANCIES = [
    {"title": "Python разработчик", "company": "TechCorp"},
    {"title": "Data Scientist", "company": "DataLab"},
    {"title": "Backend Engineer", "company": "FastAPI Inc"}
]

# Обработчик /search
@dp.message(Command("search"))
async def handle_search(message: types.Message):
    log_action("SEARCH_COMMAND", message.from_user.id, message.from_user.username)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{v['title']} @ {v['company']}", callback_data=f"vacancy_{i}")]
        for i, v in enumerate(VACANCIES)
    ])
    await message.answer("Найденные вакансии:", reply_markup=keyboard)
    log_action("VACANCIES_SENT", message.from_user.id, message.from_user.username, f"Count: {len(VACANCIES)}")

# Обработчик callback запросов от кнопок вакансий
@dp.callback_query(F.data.startswith("vacancy_"))
async def handle_vacancy_callback(callback: types.CallbackQuery):
    vacancy_id = int(callback.data.split("_")[1])
    vacancy = VACANCIES[vacancy_id]
    log_action("VACANCY_SELECTED", callback.from_user.id, callback.from_user.username, 
               f"Vacancy: {vacancy['title']}")
    await callback.answer(f"Вы выбрали: {vacancy['title']} в {vacancy['company']}", show_alert=True)

# Обработчик любых текстовых сообщений
@dp.message()
async def handle_other_messages(message: types.Message):
    log_action("TEXT_MESSAGE", message.from_user.id, message.from_user.username, 
               f"Text: {message.text[:50]}{'...' if len(message.text) > 50 else ''}")
    await message.answer("Используйте команды:\n/resume - для загрузки резюме\n/search - для поиска вакансий")

if __name__ == "__main__":
    print("=" * 50)
    print("Бот запущен и готов к работе...")
    print("Ожидание сообщений от пользователей")
    print("=" * 50)
    dp.run_polling(bot)