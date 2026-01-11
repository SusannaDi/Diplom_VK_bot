# Здесь функции для работы с JSON-файлами

import json
import os
from datetime import datetime

# Имя файла для хранения данных
FAVORITES_FILE = 'favorites.json'

def load_favorites(): # Загружаем данные из файла favorites.json
    if not os.path.exists(FAVORITES_FILE):
        return [] # возвращаем пустой список

    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []


def save_favorites(data): # Сохраняем данные в файл favorites.json
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_to_favorites(user_data):
    # Добавляем пользователя в избранное

    favorites = load_favorites()   # 1. Загружаем текущий список


    user_id = user_data.get('vk_id') # 2. Проверяем, нет ли уже такого пользователя по vk_id
    if not user_id:
        print("Ошибка: у пользователя нет vk_id!")
        return False

    # Проверяем дубликаты
    for user in favorites:
        if user.get('vk_id') == user_id:
            print(f"Пользователь с vk_id {user_id} уже в избранном")
            return False

    # 3. Убедимся, что есть поле saved_at с правильным форматом
    if 'saved_at' not in user_data:
        user_data['saved_at'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # 4. Добавляем в список
    favorites.append(user_data)

    # 5. Сохраняем
    if save_favorites(favorites):
        print(f"Пользователь {user_data['first_name']} добавлен в избранное")
        return True
    return False


def get_favorites():
    # Возвращает список избранных пользователей
    return load_favorites()