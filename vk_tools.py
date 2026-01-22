# Здесь функции для работы с API VK

import vk_api
from vk_api.exceptions import VkApiError
from config import (
    VK_GROUP_TOKEN,
    VK_USER_TOKEN,
    VK_API_VERSION,
    DEFAULT_AGE_FROM,
    DEFAULT_AGE_TO,
    AGE_DELTA,
    SEARCH_COUNT,
    PHOTOS_COUNT
)
import random
from datetime import datetime

import requests
import socket

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

    Returns:
        dict: {
            'vk_id': int,
            'first_name': str,
            'last_name': str,
            'profile_url': str,
            'age': int или None,
            'sex': int (1-жен, 2-муж, 0-не указан),
            'city_id': int или None,
            'city_title': str или None
        }
    """
    try:
        response = vk_user.users.get(
            user_ids=user_id,
            fields='sex,bdate,city,first_name,last_name'
        )

        if not response:
            print(f"   Пользователь с ID {user_id} не найден")
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

        # Возраст
        bdate = user.get('bdate', '')
        info['age'] = None

        if bdate:
            parts = bdate.split('.')
            if len(parts) == 3 and parts[2].isdigit():
                birth_year = int(parts[2])
                current_year = datetime.now().year
                age = current_year - birth_year
                if 10 <= age <= 100:
                    info['age'] = age
                    print(f"Возраст определён: {age} лет")
                else:
                    print(f"Нереалистичный возраст в профиле: {age} лет")
            else:
                print(f"Дата рождения указана без года: '{bdate}'")
        else:
            print(f"Дата рождения не указана в профиле")

        # Город
        if 'city' in user:
            info['city_id'] = user['city']['id']
            info['city_title'] = user['city']['title']
        else:
            info['city_id'] = None
            info['city_title'] = None

        print(f" Получена информация о пользователе {user_id}")
        return info


    except vk_api.exceptions.VkApiError as e:
        print(f"Ошибка VK API [{e.code}]: {e.message}")
        return None
    except requests.exceptions.Timeout:
        print("Таймаут при запросе к VK API (слишком долгий ответ)")
        return None
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения с VK API (проверьте интернет)")
        return None
    except socket.error as e:
        print(f"Сетевая ошибка: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при получении информации: {e}")
        return None


def search_users(params, count=None):
    """
    Ищет пользователей ВКонтакте по критериям.
    """
    try:

        if count is None:
            count = SEARCH_COUNT

        search_params = {
            'count': min(count * 3, 1000),  # Ищем больше, потом отфильтруем
            'fields': 'sex,city,bdate,is_closed,can_access_closed,has_photo',
            'has_photo': 1,
            'status': 1,
        }

        # 1. ПОЛ: ищем противоположный пол
        user_sex = params.get('sex')
        if user_sex == 1:  # если ищущий - девушка
            search_params['sex'] = 2  # ищем мужчин
        elif user_sex == 2:  # если ищущий - мужчина
            search_params['sex'] = 1  # ищем девушек

        # 2. ВОЗРАСТ: если возраст известен, ищем ±AGE_DELTA лет
        user_age = params.get('age')

        if user_age is None:
            print(f"Возраст пользователя не указан, использую диапазон по умолчанию: {DEFAULT_AGE_FROM}-{DEFAULT_AGE_TO} лет")
            search_params['age_from'] = DEFAULT_AGE_FROM
            search_params['age_to'] = DEFAULT_AGE_TO
        elif isinstance(user_age, int):
            print(f"Возраст пользователя: {user_age} лет, ищем ±{AGE_DELTA} лет")
            search_params['age_from'] = max(DEFAULT_AGE_FROM, user_age - AGE_DELTA)
            search_params['age_to'] = min(DEFAULT_AGE_TO, user_age + AGE_DELTA)
        else:
            print(f"Некорректный возраст: {user_age}, использую диапазон по умолчанию")
            search_params['age_from'] = DEFAULT_AGE_FROM
            search_params['age_to'] = DEFAULT_AGE_TO


        if user_age and isinstance(user_age, int):
            search_params['age_from'] = max(DEFAULT_AGE_FROM, user_age - AGE_DELTA)
            search_params['age_to'] = min(DEFAULT_AGE_TO, user_age + AGE_DELTA)
        else:
            search_params['age_from'] = DEFAULT_AGE_FROM
            search_params['age_to'] = DEFAULT_AGE_TO

        city_id = params.get('city_id')

        print(f"🔍 Ищем пользователей...")

        # Выполняем поиск
        response = vk_user.users.search(**search_params)

        if not response or 'items' not in response:
            print("    Не удалось выполнить поиск")
            return []

        users = response['items']
        print(f"    Найдено {len(users)} пользователей")

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

            # ФИЛЬТРАЦИЯ ПО ГОРОДУ (если город указан)
            if city_id:
                user_city = user.get('city', {}).get('id')
                if user_city != city_id:
                    continue  # Пропускаем, если город не совпадает

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

        print(f"    После фильтрации: {len(filtered_users)} пользователей")
        if city_id:
            print(f"      (только город ID: {city_id})")

        # Перемешиваем список
        random.shuffle(filtered_users)

        return filtered_users[:count]

    except Exception as e:  # ← ВАЖНО: закрываем try блок
        print(f" Ошибка при поиске пользователей: {e}")
        return []


def get_top_photos(user_id, count=3):
    """
    Получает самые популярные фотографии пользователя.
    """
    try:
        if count is None:
            count = PHOTOS_COUNT
        print(f"    Запрашиваем фото пользователя {user_id}...")
        response = vk_user.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1,
            count=100,
            rev=1
        )
        if not response or 'items' not in response:
            print(f"      У пользователя {user_id} нет фотографий в профиле")
            return []
        photos = response['items']
        if not photos:
            return []
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
        print(f"       Отобрано {len(attachments)} фото")
        return attachments

    except vk_api.exceptions.VkApiError as e:
        # Специфические ошибки VK API для фото
        if 'Access denied' in str(e) or 'Privacy' in str(e):
            print(f"Профиль пользователя {user_id} закрыт")
        elif e.code == 6 or e.code == 9:
            print(f"Лимит запросов фото. Пропускаем.")
        else:
            print(f"Ошибка VK API при получении фото [{e.code}]: {e.message}")
        return []
    except requests.exceptions.Timeout:
        print(f"Таймаут при получении фото пользователя {user_id}")
        return []
    except requests.exceptions.ConnectionError:
        print(f"Ошибка соединения при получении фото")
        return []
    except socket.error as e:
        print(f"Сетевая ошибка при получении фото: {e}")
        return []
    except Exception as e:
        print(f"Неизвестная ошибка при получении фото: {e}")
        return []