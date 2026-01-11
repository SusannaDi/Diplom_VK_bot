# тестируем поиск
import vk_tools


MY_VK_ID = 4199030

# Тест на твоих данных
my_info = {
    'vk_id': MY_VK_ID,
    'sex': 1,  # женский
    'age': None,  # не указан
    'city_id': 57,  # Иркутск
}

print("=" * 60)
print("ТЕСТ ПОИСКА ПОЛЬЗОВАТЕЛЕЙ (с настройками из config)")
print("=" * 60)
print(f"Мои данные для поиска:")
print(f"  ID: {my_info['vk_id']}")
print(f"  Пол: {my_info['sex']} ({'женский' if my_info['sex'] == 1 else 'мужской'})")
print(f"  Возраст: {my_info['age'] or 'не указан'}")
print(f"  Город ID: {my_info['city_id']} (Иркутск)")

# Проверяем настройки из config
from config import DEFAULT_AGE_FROM, DEFAULT_AGE_TO

print(f"  Диапазон поиска (из config): {DEFAULT_AGE_FROM}-{DEFAULT_AGE_TO} лет")
print("=" * 60)

# Ищем пользователей
print("\n🔍 Ищем подходящих пользователей...")
found_users = vk_tools.search_users(my_info, count=3)

if found_users:
    print(f"\n✅ Найдено {len(found_users)} пользователей:\n")

    for i, user in enumerate(found_users, 1):
        print(f"{i}. {user['first_name']} {user['last_name']}")
        print(f"   ID: {user['vk_id']}")
        print(f"   Ссылка: {user['profile_url']}")

        sex_str = "женский" if user['sex'] == 1 else "мужской" if user['sex'] == 2 else "не указан"
        print(f"   Пол: {user['sex']} ({sex_str})")

        print(f"   Возраст: {user.get('age', 'не указан')}")
        print(f"   Город: {user.get('city_title', 'не указан')}")
        print()
else:
    print("\n❌ Не найдено подходящих пользователей")

print("=" * 60)