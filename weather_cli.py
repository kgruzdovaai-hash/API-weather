from weather_app import get_current_weather


def weather_by_city(city_name):
    """Запрашивает погоду по названию города"""
    try:
        weather_data = get_current_weather(city=city_name)
        if weather_data:
            print(f"Погода в {weather_data['name']}: {weather_data['main']['temp']}°C, {weather_data['weather'][0]['description']}")
        else:
            print("Не удалось получить данные о погоде для указанного города.")
    except Exception as e:
        print(f"Ошибка при получении данных о погоде: {e}")


def weather_by_coordinates(lat, lon):
    """Запрашивает погоду по координатам"""
    try:
        weather_data = get_current_weather(latitude=lat, longitude=lon)
        if weather_data:
            print(f"Погода для координат ({lat}, {lon}): {weather_data['main']['temp']}°C, {weather_data['weather'][0]['description']}")
        else:
            print("Не удалось получить данные о погоде для указанных координат.")
    except Exception as e:
        print(f"Ошибка при получении данных о погоде: {e}")


def main():
    """Основное меню CLI для запроса погоды"""
    while True:
        print("\n" + "="*50)
        print("МЕНЮ ЗАПРОСА ПОГОДЫ")
        print("="*50)
        print("1 — по городу")
        print("2 — по координатам")
        print("0 — выход")
        print("-"*50)
        
        choice = input("Выберите действие (0-2): ").strip()
        
        if choice == "0":
            print("Выход из программы.")
            break
        elif choice == "1":
            city = input("Введите название города: ").strip()
            if city:
                weather_by_city(city)
            else:
                print("Название города не может быть пустым!")
        elif choice == "2":
            try:
                lat = float(input("Введите широту (например, 55.7558): "))
                lon = float(input("Введите долготу (например, 37.6176): "))
                weather_by_coordinates(lat, lon)
            except ValueError:
                print("Ошибка: введите корректные числовые значения координат")
        else:
            print("Неверный выбор! Пожалуйста, введите 0, 1 или 2.")


if __name__ == "__main__":
    main()