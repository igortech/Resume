from datetime import datetime
import docx2txt
import PyPDF2
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class FileProcessor:
    """Класс для обработки файлов резюме"""
    
    @staticmethod
    def extract_skills(text: str) -> list:
        skills = ["Python", "SQL", "FastAPI", "Docker", "JavaScript", 
                 "React", "PostgreSQL", "Git", "MongoDB", "Redis",
                 "AWS", "Linux", "Django", "Flask", "HTML", "CSS"]
        found_skills = [skill for skill in skills if skill.lower() in text.lower()]
        return found_skills[:5]

    @staticmethod
    def process_pdf(file_path: str, request_id: str) -> Tuple[str, int]:
        logger.info(f"[{request_id}] Начало обработки PDF")
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages])
            pages_count = len(reader.pages)
            
        logger.info(f"[{request_id}] PDF обработан - страниц: {pages_count}, символов: {len(text)}")
        return text, pages_count

    @staticmethod
    def process_docx(file_path: str, request_id: str) -> str:
        logger.info(f"[{request_id}] Начало обработки DOCX")
        
        text = docx2txt.process(file_path)
        
        logger.info(f"[{request_id}] DOCX обработан - символов: {len(text)}")
        return text

    @staticmethod
    def validate_file(file_length: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        if not filename:
            return False, "Имя файла не может быть пустым"
            
        if not filename.endswith(('.pdf', '.docx')):
            return False, "Поддерживаются только PDF и DOCX файлы"
            
        if file_length == 0:
            return False, "Файл пустой"
            
        if file_length > 10 * 1024 * 1024:  # 10MB
            return False, "Файл слишком большой (максимум 10MB)"
            
        return True, None

    def process_resume(self, filename: str, request_id: str) -> dict:
        logger.info(f"[{request_id}] Начало обработки резюме: {filename}")

        # Чтение содержимого файла
        #content = await file.read()

        # Валидация файла
        file_size = os.path.getsize(filename)
        is_valid, error_message = self.validate_file(file_size, filename)
        if not is_valid:
            logger.error(f"[{request_id}] Ошибка валидации: {error_message}")
            raise ValueError(error_message)
        
        try:

            
            # Обработка в зависимости от типа файла
            if filename.endswith('.pdf'):
                text, pages_count = self.process_pdf(filename, request_id)
                file_info = {"pages": pages_count, "type": "pdf"}
            else:
                text = self.process_docx(filename, request_id)
                file_info = {"type": "docx"}
            
            # Извлечение навыков
            skills = self.extract_skills(text)
            logger.info(f"[{request_id}] Навыки извлечены: {len(skills)} найдено")
            
            # Обрезаем текст если он слишком длинный
            text_length = len(text)
            if text_length > 4000:
                text = text[:4000] + "..."
                log_action("TEXT_TRIMMED", request_id, f"Original: {text_length} chars")
                
            log_action("TEXT_EXTRACTED", request_id, f"Chars: {min(text_length, 4000)}")

            # Формирование результата
            result = {
                "text": text,
                "skills": skills,
                "text_length": len(text),
                "file_info": file_info,
                "filename": filename,
                "file_size": file_size
            }
            
            logger.info(f"[{request_id}] Обработка резюме завершена успешно")
            return result
            
        except PyPDF2.PdfReadError as e:
            logger.error(f"[{request_id}] Ошибка чтения PDF: {str(e)}")
            raise Exception(f"Ошибка чтения PDF файла: {str(e)}")
            
        except Exception as e:
            logger.error(f"[{request_id}] Ошибка обработки файла: {str(e)}")
            raise Exception(f"Ошибка обработки файла: {str(e)}")

def log_action(action: str, request_id: int, additional_info: str = ""):
    """Логирование действий"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"ID:{request_id}"
    info = f" | {additional_info}" if additional_info else ""
    message = f"[{timestamp}] {action} | User: {user_info}{info}"
    logger.info(message)