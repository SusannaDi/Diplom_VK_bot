# тестируем вк

import vk_tools

MY_VK_ID = '4199030'

print("=== Тестирование функции get_user_info() ===")
print(f"Запрашиваем информацию для ID: {MY_VK_ID}")

user_info = vk_tools.get_user_info(MY_VK_ID)

if user_info:
    print("\n✅ Успешно получена информация:")
    print("-" * 40)
    print(f"ID: {user_info.get('vk_id')}")
    print(f"Имя: {user_info.get('first_name')}")
    print(f"Фамилия: {user_info.get('last_name')}")
    print(f"Ссылка: {user_info.get('profile_url')}")
    print(f"Возраст: {user_info.get('age')}")

    sex = user_info.get('sex')
    if sex == 1:
        sex_str = "женский"
    elif sex == 2:
        sex_str = "мужской"
    else:
        sex_str = "не указан"
    print(f"Пол: {sex} ({sex_str})")

    print(f"ID города: {user_info.get('city_id')}")
    print(f"Город: {user_info.get('city_title')}")
    print("-" * 40)

    # Проверяем, что есть все нужные данные для поиска
    missing_for_search = []
    if user_info.get('age') is None:
        missing_for_search.append("возраст")
    if user_info.get('sex') == 0:
        missing_for_search.append("пол")
    if user_info.get('city_id') is None:
        missing_for_search.append("город")

    if missing_for_search:
        print(f"\n⚠️  Внимание: не хватает данных для поиска: {', '.join(missing_for_search)}")
        print("   Бот будет работать, но поиск может быть неточным")
    else:
        print("\n✅ Все данные для поиска присутствуют!")

else:
    print("\n❌ Не удалось получить информацию о пользователе")
    print("Возможные причины:")
    print("1. Неверный ID пользователя")
    print("2. Проблемы с токеном ВК")
    print("3. Ошибка сети или API ВКонтакте")

