# тестовый файл

# test_favorites.py
import data_handler

# Тестовый пользователь ПО НОВОЙ СХЕМЕ
test_user = {
    "vk_id": 123456789,
    "first_name": "Анна",
    "last_name": "Смирнова",
    "profile_url": "https://vk.com/id123456789",
    "photos": [
        "photo123456789_987654321",
        "photo123456789_987654322",
        "photo123456789_987654323"
    ]
    # saved_at добавится автоматически
}

print("=== Тест 1: Добавление пользователя ===")
success = data_handler.add_to_favorites(test_user)
print(f"Успешно: {success}")

print("\n=== Тест 2: Получение избранного ===")
favorites = data_handler.get_favorites()
print(f"Всего в избранном: {len(favorites)} человек")
for user in favorites:
    print(f"- {user['first_name']} {user['last_name']} (id: {user['vk_id']})")
    print(f"  Фото: {user['photos']}")
    print(f"  Добавлен: {user['saved_at']}")

print("\n=== Тест 3: Проверка на дубликаты ===")
success2 = data_handler.add_to_favorites(test_user)  # Пробуем добавить того же
print(f"Повторное добавление: {success2} (должно быть False)")