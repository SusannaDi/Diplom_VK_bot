# Главный файл, с которого запускается бот

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
from datetime import datetime


# Импортируем наши модули
import data_handler
import vk_tools
from config import VK_GROUP_TOKEN, VK_API_VERSION, GROUP_ID
import user_states
from keyboards import get_main_keyboard, get_search_keyboard, get_empty_keyboard

def main():
    """Основная функция бота"""
    print("=" * 60)
    print("ЗАПУСК БОТА ")
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Инициализация VK API
    vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN, api_version=VK_API_VERSION)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print(f"Бот запущен для группы ID: {GROUP_ID}")
    print("📝 Ожидаю сообщения от пользователей...")
    print("=" * 60)

    # Главный цикл бота
    for event in longpoll.listen():
        # Обрабатываем только новые сообщения
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            process_message(vk, event)


def process_message(vk, event):
    """Обрабатывает входящее сообщение или нажатие кнопки"""
    user_id = event.user_id
    message_text = event.text.lower().strip()

    print(f"Сообщение от {user_id}: '{message_text}'")

    # Обработка команд/кнопок
    if message_text in ['/start', 'старт', 'начать', 'привет', 'hello', 'назад', 'меню']:
        send_welcome(vk, user_id)
    elif message_text in ['/help', 'помощь', 'команды', 'помощь']:
        send_help(vk, user_id)
    elif message_text in ['поиск', 'поиск']:
        start_search(vk, user_id)
    elif message_text in ['избранное', 'избранное']:
        show_favorites(vk, user_id)

    # Кнопки поиска
    elif message_text in ['дальше', 'дальше']:
        handle_next(vk, user_id)
    elif message_text in ['добавить', 'в избранное']:
        add_current_to_favorites(vk, user_id)
    elif message_text in ['стоп', 'стоп']:
        stop_search(vk, user_id)

    else:
        send_unknown_command(vk, user_id)


def send_unknown_command(vk, user_id):
    """Отправляет сообщение о неизвестной команде с клавиатурой"""
    message = (
        "Я не понял команду.\n\n"
        "Используйте кнопки ниже или команды:\n"
        "• 'поиск' — начать поиск\n"
        "• 'избранное' — показать избранных\n"
        "• 'помощь' — показать все команды"
    )
    send_message(vk, user_id, message, keyboard=get_main_keyboard())


def send_welcome(vk, user_id):
    """Отправляет приветственное сообщение с клавиатурой"""
    message = (
        "Привет! Я бот VKinder — помогу найти интересных людей для знакомств!\n\n"
        "Используйте кнопки ниже для навигации:\n"
        "•  Поиск — начать поиск людей\n"
        "•  Избранное — показать избранных\n"
        "•  Помощь — показать все команды"
    )
    send_message(vk, user_id, message, keyboard=get_main_keyboard())


def send_help(vk, user_id):
    """Отправляет список команд с клавиатурой"""
    message = (
        "Справка по боту VKinder:\n\n"
        "Основные кнопки:\n"
        "• Поиск — найти людей для знакомств\n"
        "•️ Избранное — ваши сохранённые контакты\n\n"
        " Во время поиска:\n"
        "•️ Дальше — следующий человек\n"
        "•️ В избранное — сохранить текущего\n"
        "• Стоп — остановить поиск\n"
        "• Назад — вернуться в меню"
    )
    send_message(vk, user_id, message, keyboard=get_main_keyboard())


def send_message(vk, user_id, message, attachments=None, keyboard=None):
    """Отправляет сообщение пользователю"""
    try:
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': random.randint(1, 10 ** 7),
        }

        if attachments:
            params['attachment'] = attachments

        if keyboard:
            params['keyboard'] = keyboard

        vk.messages.send(**params)
        print(f" Отправлено сообщение пользователю {user_id}")

    except Exception as e:
        print(f" Ошибка при отправке сообщения: {e}")


# поиск людей
def start_search(vk, user_id):
    """Начинает поиск людей для пользователя"""
    print(f" Пользователь {user_id} начал поиск")

    # Сразу отправляем сообщение, что начали поиск
    message = " Получаю вашу информацию..."
    send_message(vk, user_id, message, keyboard=get_search_keyboard())

    # 1. Получаем информацию о пользователе
    user_info = vk_tools.get_user_info(user_id)

    if not user_info:
        message = " Не удалось получить вашу информацию. Проверьте, открыт ли ваш профиль."
        send_message(vk, user_id, message, keyboard=get_main_keyboard())
        return

    # Сообщаем о прогрессе
    message = f" Получена информация. Ищу людей в {user_info.get('city_title', 'вашем городе')}..."
    send_message(vk, user_id, message, keyboard=get_search_keyboard())

    # 2. Формируем параметры поиска
    search_params = {
        'vk_id': user_info['vk_id'],
        'sex': user_info['sex'],
        'age': user_info['age'],
        'city_id': user_info['city_id']
    }

    # 3. Инициализируем состояние пользователя
    user_states.init_user_state(user_id, search_params)

    # 4. Ищем людей
    found_users = vk_tools.search_users(search_params, count=10)

    if not found_users:
        message = (
            " Не найдено подходящих людей с открытыми профилями.\n"
            "Попробуйте изменить критерии поиска или попробовать позже."
        )
        send_message(vk, user_id, message, keyboard=get_main_keyboard())
        user_states.clear_user_state(user_id)
        return

    # 5. Сохраняем результаты
    user_states.set_user_results(user_id, found_users)

    # 6. Показываем первого человека
    show_next_person(vk, user_id)


# следующий человек из результата поиска
def show_next_person(vk, user_id):
    """Показывает следующего человека из результатов поиска"""
    user_data = user_states.get_next_user(user_id)

    if not user_data:
        message = (
            "🏁 Вы просмотрели всех найденных людей!\n\n"
            "Нажмите 'Поиск' чтобы начать новый поиск "
            "или 'Избранное' чтобы посмотреть сохранённых."
        )
        send_message(vk, user_id, message, keyboard=get_main_keyboard())  # ← ВЕРНУЛИ ОСНОВНУЮ КЛАВИАТУРУ
        user_states.clear_user_state(user_id)
        return

    print(f"   Показываю пользователя {user_data['vk_id']} юзеру {user_id}")

    # 1. Получаем фотографии
    photos = vk_tools.get_top_photos(user_data['vk_id'], count=3)

    # 2. Формируем сообщение
    message = (
        f"{user_data['first_name']} {user_data['last_name']}\n"
        f"{user_data['profile_url']}\n"
    )

    if user_data.get('age'):
        message += f"{user_data['age']} лет\n"

    if user_data.get('city_title'):
        message += f"{user_data['city_title']}\n"

    message += "\nИспользуйте кнопки ниже:"

    # 3. Отправляем сообщение с фото и клавиатурой поиска
    if photos:
        attachments = ','.join(photos)
        send_message(vk, user_id, message, attachments=attachments, keyboard=get_search_keyboard())
    else:
        message += "\n\n📷 Фотографии недоступны (закрытый профиль)"
        send_message(vk, user_id, message, keyboard=get_search_keyboard())


def show_favorites(vk, user_id):
    """Показывает избранных пользователей"""
    favorites = data_handler.get_favorites()

    if not favorites:
        message = "Ваш список избранных пуст.\nНапишите 'поиск' чтобы найти людей и добавить их в избранное."
        send_message(vk, user_id, message)
        return

    message = f"Ваши избранные ({len(favorites)} человек):\n\n"

    for i, user in enumerate(favorites[:10], 1):  # Показываем первые 10
        message += f"{i}. {user['first_name']} {user['last_name']}\n"
        message += f"   🔗 {user['profile_url']}\n"

        if user.get('saved_at'):
            # Преобразуем дату в читаемый формат
            date_str = user['saved_at'].replace('T', ' ')
            message += f"   Добавлен: {date_str}\n"

        message += "\n"

    if len(favorites) > 10:
        message += f"... и ещё {len(favorites) - 10} человек\n"

    message += "Напишите 'поиск' чтобы найти ещё людей."

    send_message(vk, user_id, message)


def handle_next(vk, user_id):
    """Обрабатывает команду 'дальше'"""
    # Проверяем, есть ли активный поиск
    results = user_states.get_user_results(user_id)

    if not results:
        message = "У вас нет активного поиска. Напишите 'поиск' чтобы начать."
        send_message(vk, user_id, message)
        return

    show_next_person(vk, user_id)


def add_current_to_favorites(vk, user_id):
    """Добавляет текущего пользователя в избранное"""
    results = user_states.get_user_results(user_id)
    current_idx = user_states.get_current_index(user_id)

    if not results or current_idx == 0:
        message = "Нет активного пользователя для добавления."
        send_message(vk, user_id, message)
        return

    # Берем предыдущего пользователя (потому что индекс уже увеличен)
    user_to_add = results[current_idx - 1]

    # Получаем фото для сохранения
    photos = vk_tools.get_top_photos(user_to_add['vk_id'], count=3)
    user_to_add['photos'] = photos

    # Добавляем в избранное
    success = data_handler.add_to_favorites(user_to_add)

    if success:
        message = f"{user_to_add['first_name']} добавлен(а) в избранное!"
    else:
        message = f"{user_to_add['first_name']} уже в избранном."

    send_message(vk, user_id, message)


def stop_search(vk, user_id):
    """Останавливает текущий поиск"""
    user_states.clear_user_state(user_id)
    message = "Поиск остановлен. Нажмите '🔍 Поиск' чтобы начать заново."
    send_message(vk, user_id, message, keyboard=get_main_keyboard())  # ← ВЕРНУЛИ ОСНОВНУЮ КЛАВИАТУРУ

if __name__ == "__main__":
    main()