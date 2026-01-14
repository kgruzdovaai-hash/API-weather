import json
import os
from datetime import datetime, timedelta
import time
import requests


class WeatherCache:
    def __init__(self, cache_file="weather_cache.json"):
        self.cache_file = cache_file

    def save_to_cache(self, data, city=None, lat=None, lon=None):
        """Сохраняет данные в кэш с метаданными"""
        cache_data = {
            "data": data,
            "city": city,
            "lat": lat,
            "lon": lon,
            "fetched_at": datetime.now().isoformat()
        }
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении в кэш: {e}")

    def load_from_cache(self):
        """Загружает данные из кэша"""
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def is_cache_fresh(self, hours=3):
        """Проверяет, не устарел ли кэш (по умолчанию за последние 3 часа)"""
        cache_data = self.load_from_cache()
        if not cache_data or "fetched_at" not in cache_data:
            return False

        fetched_at = datetime.fromisoformat(cache_data["fetched_at"])
        return datetime.now() - fetched_at < timedelta(hours=hours)

    def get_cached_weather(self):
        """Возвращает кэшированные данные о погоде"""
        cache_data = self.load_from_cache()
        if cache_data and "data" in cache_data:
            return cache_data["data"]
        return None


def retry_request(func, max_retries=3, base_delay=1):
    """Декоратор для повторных попыток запроса с экспоненциальной задержкой"""
    def wrapper(*args, **kwargs):
        delay = base_delay
        for attempt in range(max_retries):
            try:
                response = func(*args, **kwargs)
                # Проверяем, является ли ответ успешным
                if hasattr(response, 'status_code'):
                    if response.status_code == 429:
                        print(f"Получен код 429 (Too Many Requests), попытка {attempt + 1} из {max_retries}")
                        if attempt < max_retries - 1:  # Не ждем после последней попытки
                            time.sleep(delay)
                            delay *= 2  # Увеличиваем задержку экспоненциально
                        continue
                    elif 400 <= response.status_code < 600:
                        print(f"Ошибка HTTP: {response.status_code}, попытка {attempt + 1} из {max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                            delay *= 2
                        continue
                
                # Если это не response объект, а результат напрямую
                return response
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка подключения: {e}, попытка {attempt + 1} из {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
            except requests.exceptions.Timeout as e:
                print(f"Таймаут запроса: {e}, попытка {attempt + 1} из {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
            except requests.exceptions.RequestException as e:
                print(f"Ошибка запроса: {e}, попытка {attempt + 1} из {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
        
        # Если все попытки исчерпаны, возвращаем None
        print("Все попытки запроса исчерпаны")
        return None
    
    return wrapper