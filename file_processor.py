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
    def validate_file(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        if not filename:
            return False, "Имя файла не может быть пустым"
            
        if not filename.endswith(('.pdf', '.docx')):
            return False, "Поддерживаются только PDF и DOCX файлы"
            
        if len(file_content) == 0:
            return False, "Файл пустой"
            
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            return False, "Файл слишком большой (максимум 10MB)"
            
        return True, None

    def process_resume(self, file_content: bytes, filename: str, request_id: str) -> dict:
        logger.info(f"[{request_id}] Начало обработки резюме: {filename}")

        # Чтение содержимого файла
        #content = await file.read()

        # Валидация файла
        is_valid, error_message = self.validate_file(file_content, filename)
        if not is_valid:
            logger.error(f"[{request_id}] Ошибка валидации: {error_message}")
            raise ValueError(error_message)
        


        try:
            file_size = len(file_content)
            logger.info(f"[{request_id}] Файл сохранен временно: {tmp_path}, размер: {file_size} байт")
            
            # Обработка в зависимости от типа файла
            if filename.endswith('.pdf'):
                text, pages_count = self.process_pdf(tmp_path, request_id)
                file_info = {"pages": pages_count, "type": "pdf"}
            else:
                text = self.process_docx(tmp_path, request_id)
                file_info = {"type": "docx"}
            
            # Извлечение навыков
            skills = self.extract_skills(text)
            logger.info(f"[{request_id}] Навыки извлечены: {len(skills)} найдено")
            
            # Формирование результата
            result = {
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
            
        finally:
            # Очистка временного файла
            try:
                os.unlink(tmp_path)
                logger.info(f"[{request_id}] Временный файл удален: {tmp_path}")
            except Exception as e:
                logger.warning(f"[{request_id}] Не удалось удалить временный файл: {str(e)}")