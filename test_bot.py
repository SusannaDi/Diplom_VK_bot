# тест main.py

import main

print("Тест импорта модулей бота...")

# Проверяем, что все нужные модули импортируются
try:
    print("main.py импортируется успешно")

    # Проверяем доступность функций
    import data_handler

    print("data_handler импортируется успешно")

    import vk_tools

    print("vk_tools импортируется успешно")

    from config import VK_GROUP_TOKEN, VK_API_VERSION

    print("config импортируется успешно")

    print("\n" + "=" * 60)
    print("Все модули готовы к работе!")
    print("=" * 60)

except ImportError as e:
    print(f" Ошибка импорта: {e}")
except Exception as e:
    print(f" Другая ошибка: {e}")