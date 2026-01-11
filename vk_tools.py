# Здесь функции для работы с API VK

import vk_api
from vk_api.exceptions import VkApiError
from config import VK_GROUP_TOKEN, VK_USER_TOKEN, VK_API_VERSION
import random
from datetime import datetime

# Две сессии VK API:
# 1. Для работы бота (групповой токен)
vk_session_group = vk_api.VkApi(token=VK_GROUP_TOKEN, api_version=VK_API_VERSION)
vk_group = vk_session_group.get_api()

# 2. Для поиска пользователей (пользовательский токен)
vk_session_user = vk_api.VkApi(token=VK_USER_TOKEN, api_version=VK_API_VERSION)
vk_user = vk_session_user.get_api()

# В функции get_user_info используем vk_group (может работать с групповым)
# В функции search_users используем vk_user (нужен пользовательский)
def get_user_info(user_id):
    """
    Получает информацию о пользователе для поиска.
    """
    try:
        response = vk.users.get(
            user_ids=user_id,
            fields='sex,bdate,city,first_name,last_name'
        )

        if not response:
            return None

        user = response[0]
        info = {}

        # Базовые данные для сохранения
        info['vk_id'] = int(user_id)
        info['first_name'] = user.get('first_name', '')
        info['last_name'] = user.get('last_name', '')
        info['profile_url'] = f"https://vk.com/id{user_id}"

        # Данные для поиска (возраст, пол, город)
        info['sex'] = user.get('sex', 0)

        # ВОЗРАСТ - ИСПРАВЛЕННАЯ ЛОГИКА
        bdate = user.get('bdate', '')
        info['age'] = None  # По умолчанию

        if bdate:
            parts = bdate.split('.')
            # Проверяем, что есть год (3 части) и год - число
            if len(parts) == 3 and parts[2].isdigit():
                birth_year = int(parts[2])
                current_year = datetime.now().year
                age = current_year - birth_year
                # Проверяем, что возраст реалистичный
                if 10 <= age <= 100:
                    info['age'] = age
                    print(f"Возраст определён: {age} лет")
                else:
                    print(f"Нереалистичный возраст: {age} лет")
            else:
                print(f"Дата рождения без года или неполная: {bdate}")
        else:
            print("Дата рождения не указана")

        # Город
        if 'city' in user:
            info['city_id'] = user['city']['id']
            info['city_title'] = user['city']['title']
            print(f"Город: {info['city_title']} (ID: {info['city_id']})")
        else:
            info['city_id'] = None
            info['city_title'] = None
            print("Город не указан")

        print(f"Пол: {info['sex']} (1-жен, 2-муж, 0-не указан)")
        return info

    except Exception as e:
        print(f"Ошибка в get_user_info: {e}")
        return None


def search_users(params, count=None):
    """
    Ищет пользователей ВКонтакте по критериям.

    Args:
        params (dict): словарь с параметрами:
            - vk_id (int): ID пользователя, который ищет
            - sex (int): 1-жен, 2-муж (пол того, кто ищет)
            - age (int или None): возраст
            - city_id (int или None): ID города
        count (int или None): сколько пользователей искать

    Returns:
        list: список словарей с информацией о найденных пользователях
    """
    try:
        # Импортируем настройки из config
        from config import DEFAULT_AGE_FROM, DEFAULT_AGE_TO, AGE_DELTA, SEARCH_COUNT

        # Если count не указан, используем значение по умолчанию из config
        if count is None:
            count = SEARCH_COUNT

        # Параметры для поиска
        search_params = {
            'count': min(count, 1000),  # VK ограничивает 1000 результатов
            'fields': 'sex,city,bdate,is_closed,can_access_closed,has_photo',
            'has_photo': 1,  # только с фотографией
            'status': 1,  # не женат/не замужем
        }

        # 1. ПОЛ: ищем противоположный пол
        user_sex = params.get('sex')
        if user_sex == 1:  # если ищущий - девушка
            search_params['sex'] = 2  # ищем мужчин
        elif user_sex == 2:  # если ищущий - мужчина
            search_params['sex'] = 1  # ищем девушек

        # 2. ВОЗРАСТ: если возраст известен, ищем ±AGE_DELTA лет
        user_age = params.get('age')
        if user_age and isinstance(user_age, int):
            search_params['age_from'] = max(DEFAULT_AGE_FROM, user_age - AGE_DELTA)
            search_params['age_to'] = min(DEFAULT_AGE_TO, user_age + AGE_DELTA)
        else:
            search_params['age_from'] = DEFAULT_AGE_FROM
            search_params['age_to'] = DEFAULT_AGE_TO

        # 3. ГОРОД: если город известен, ищем в нём
        city_id = params.get('city_id')
        if city_id:
            search_params['city'] = city_id

        print(f"🔍 Параметры поиска: возраст {search_params.get('age_from')}-{search_params.get('age_to')}, "
              f"пол {search_params.get('sex', 'любой')}, город ID {city_id or 'любой'}")

        # Выполняем поиск
        response = vk_user.users.search(**search_params)

        if not response or 'items' not in response:
            print("❌ Не удалось выполнить поиск")
            return []

        users = response['items']
        print(f"📊 Найдено {len(users)} пользователей")

        # Фильтруем результаты
        filtered_users = []
        for user in users:
            # Пропускаем закрытые профили
            if user.get('is_closed', True):
                if not user.get('can_access_closed', False):
                    continue

            # Пропускаем без фото
            if not user.get('has_photo', 0):
                continue

            # Пропускаем себя
            user_vk_id = params.get('vk_id')
            if user_vk_id and str(user.get('id')) == str(user_vk_id):
                continue

            # Формируем информацию о пользователе
            user_info = {
                'vk_id': user['id'],
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'profile_url': f"https://vk.com/id{user['id']}",
                'sex': user.get('sex', 0),
                'age': None,
                'city_id': None,
                'city_title': None,
            }

            # Определяем возраст
            bdate = user.get('bdate', '')
            if bdate and len(bdate.split('.')) == 3:
                parts = bdate.split('.')
                if parts[2].isdigit():
                    birth_year = int(parts[2])
                    user_info['age'] = datetime.now().year - birth_year

            # Определяем город
            if 'city' in user:
                user_info['city_id'] = user['city']['id']
                user_info['city_title'] = user['city']['title']

            filtered_users.append(user_info)

        print(f"✅ После фильтрации осталось {len(filtered_users)} пользователей")

        # Перемешиваем список для разнообразия
        random.shuffle(filtered_users)

        return filtered_users[:count]

    except Exception as e:
        print(f"❌ Ошибка при поиске пользователей: {e}")
        return []


def get_top_photos(user_id, count=3):
    """
    Получает самые популярные фотографии пользователя.

    Args:
        user_id (int): ID пользователя ВКонтакте
        count (int): сколько фотографий возвращать

    Returns:
        list: список фотографий в формате для attachments:
            ['photo{owner_id}_{photo_id}', ...]
    """
    try:
        # Используем настройку из config
        from config import PHOTOS_COUNT
        if count is None:
            count = PHOTOS_COUNT

        print(f"📸 Запрашиваем {count} фото пользователя {user_id}...")

        response = vk_user.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1,
            count=100,
            rev=1
        )

        if not response or 'items' not in response:
            print(f"   У пользователя {user_id} нет фотографий")
            return []

        photos = response['items']
        print(f"   Найдено {len(photos)} фотографий")

        # Сортируем по лайкам
        photos_sorted = sorted(
            photos,
            key=lambda x: x.get('likes', {}).get('count', 0),
            reverse=True
        )

        # Берем топ-N
        top_photos = photos_sorted[:count]

        # Формируем attachments
        attachments = []
        for photo in top_photos:
            attachment_str = f"photo{photo['owner_id']}_{photo['id']}"
            attachments.append(attachment_str)

            likes = photo.get('likes', {}).get('count', 0)
            print(f"   Фото {photo['id']}: {likes} лайков")

        print(f"✅ Отобрано {len(attachments)} самых популярных фотографий")
        return attachments

    except vk_api.exceptions.VkApiError as e:
        if 'Access denied' in str(e):
            print(f"   Профиль пользователя {user_id} закрыт")
        else:
            print(f"   Ошибка VK API: {e}")
        return []
    except Exception as e:
        print(f"   Ошибка при получении фото: {e}")
        return []