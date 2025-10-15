import subprocess
import sys
import time
import os

def run_services():
    print("Запуск всех сервисов...")
    print(f"Рабочая директория: {os.getcwd()}")
    
    # Проверяем существование файлов
    if not os.path.exists("app.py"):
        print("Файл app.py не найден!")
        return
    if not os.path.exists("api.py"):
        print("Файл api.py не найден!")
        return
    
    # Запуск app.py
    print("Запуск app.py (бот)...")
    app_process = subprocess.Popen([sys.executable, "app.py"])
    
    # Задержка для уверенности
    time.sleep(3)
    
    # Запуск api.py
    print("Запуск api.py (API сервер)...")
    api_process = subprocess.Popen([sys.executable, "api.py"])
    
    print("Оба сервиса запущены!")
    print("Для остановки нажмите Ctrl+C\n")
    
    try:
        # Ожидаем завершения процессов
        app_process.wait()
        api_process.wait()
    except KeyboardInterrupt:
        print("Остановка сервисов...")
        app_process.terminate()
        api_process.terminate()
        app_process.wait()
        api_process.wait()
        print("Все сервисы остановлены")

if __name__ == "__main__":
    run_services()