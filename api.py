from fastapi import FastAPI, UploadFile, HTTPException
import logging
from datetime import datetime
import uuid
import os
import tempfile
from file_processor import FileProcessor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()
file_processor = FileProcessor()

def log_request(request_id: str, action: str, user_info: str = "", additional_info: str = ""):
    """Универсальная функция для логирования запросов"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_str = f" | User: {user_info}" if user_info else ""
    info_str = f" | Info: {additional_info}" if additional_info else ""
    message = f"[{timestamp}] [{request_id}] {action}{user_str}{info_str}"
    logger.info(message)

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile):
    request_id = str(uuid.uuid4())[:8]
    
    log_request(request_id, "FILE_UPLOAD_STARTED", 
                f"Filename: {file.filename}", 
                f"Content-Type: {file.content_type}")
    
    try:
        # Чтение содержимого файла
        content = await file.read()
        # Создание временного файла
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(content)

            # Обработка файла через FileProcessor
            result = file_processor.process_resume(tmp.name, request_id)
        
        # Добавляем request_id в ответ
        result["request_id"] = request_id
        
        log_request(request_id, "REQUEST_COMPLETED", 
                   f"Skills found: {len(result['skills'])}")
        
        return result
        
    except ValueError as e:
        # Ошибки валидации
        log_request(request_id, "VALIDATION_ERROR", 
                   f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Ошибки обработки
        log_request(request_id, "PROCESSING_ERROR", 
                   f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Resume Analysis API is running"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    
    logger.info(f"[{request_id}] {request.method} {request.url} - Client: {request.client.host}")
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"[{request_id}] Completed - Status: {response.status_code} - Time: {process_time:.2f}s")
    
    response.headers["X-Request-ID"] = request_id
    return response

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)