import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from weather_cache import WeatherCache, retry_request

load_dotenv()
API_KEY = os.getenv("API_KEY")
cache = WeatherCache()

def get_current_weather(city: str=None, latitude: float=None, longitude: float=None) -> dict:
    if city:
        print(f"\nПолучаем погоду для города: {city}")
        try:
            latitude, longitude = get_coordinates(city)
            if latitude is None or longitude is None:
                print("Не удалось получить координаты для указанного города.")
                # Проверяем, есть ли кэшированные данные для этого города
                cached_data = cache.load_from_cache()
                if cached_data and cached_data.get("city") == city and cache.is_cache_fresh():
                    print("Используем кэшированные данные из-за ошибки получения новых.")
                    return cache.get_cached_weather()
                return None
            
            weather = get_weather_by_coordinates(latitude, longitude)
            if weather:
                # Сохраняем в кэш при успешном получении
                cache.save_to_cache(weather, city=city, lat=latitude, lon=longitude)
            else:
                # Если не удалось получить новые данные, пробуем использовать кэш
                cached_data = cache.load_from_cache()
                if cached_data and cached_data.get("city") == city and cache.is_cache_fresh():
                    print("Используем кэшированные данные из-за ошибки получения новых.")
                    return cache.get_cached_weather()
            return weather
        except Exception as e:
            print(f"Ошибка при получении погоды для города: {e}")
            # Если произошла ошибка, проверяем кэш
            cached_data = cache.load_from_cache()
            if cached_data and cached_data.get("city") == city and cache.is_cache_fresh():
                print("Используем кэшированные данные из-за ошибки получения новых.")
                return cache.get_cached_weather()
            return None

    if latitude and longitude:
        print(f"\nПолучаем погоду для координат: {latitude}, {longitude}")
        weather = get_weather_by_coordinates(latitude, longitude)
        if weather:
            # Сохраняем в кэш при успешном получении
            cache.save_to_cache(weather, lat=latitude, lon=longitude)
        else:
            # Если не удалось получить новые данные, пробуем использовать кэш
            cached_data = cache.load_from_cache()
            if cached_data and cached_data.get("lat") == latitude and cached_data.get("lon") == longitude and cache.is_cache_fresh():
                print("Используем кэшированные данные из-за ошибки получения новых.")
                return cache.get_cached_weather()
        return weather

@retry_request
def get_coordinates_with_retry(city: str):
    """Внутренняя функция для получения координат с ретраями"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    return requests.get(url)

def get_coordinates(city: str) -> tuple:
    response = get_coordinates_with_retry(city)
    if response and response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            return data[0]['lat'], data[0]['lon']
        else:
            print("Город не найден в геокодере.")
            return None, None
    else:
        print(f"Ошибка при получении координат: {response.status_code if response else 'No response'}")
        return None, None

@retry_request
def get_weather_by_coordinates_with_retry(latitude: float, longitude: float):
    """Внутренняя функция для получения погоды по координатам с ретраями"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
    return requests.get(url)

def get_weather_by_coordinates(latitude: float, longitude: float) -> dict:
    response = get_weather_by_coordinates_with_retry(latitude, longitude)
    if response and response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении погоды: {response.status_code if response else 'No response'}")
        return None
    
    
if __name__ == "__main__":
    weather = get_current_weather("Moscow")
    if weather:
        print(f"Погода в {weather['name']}: {weather['main']['temp']}°C, {weather['weather'][0]['description']}")
    else:
        print("Не удалось получить данные о погоде.")