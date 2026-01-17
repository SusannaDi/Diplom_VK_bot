# управление состояниями пользователей

user_search_data = {}  # Данные для поиска каждого пользователя
user_search_results = {}  # Найденные люди для каждого пользователя
user_current_index = {}  # Текущий индекс в результатах поиска


def init_user_state(user_id, search_params):
    """
    Инициализирует состояние пользователя для поиска.

    Args:
        user_id: ID пользователя ВК
        search_params: параметры поиска (возраст, пол, город)
    """
    user_search_data[user_id] = search_params
    user_search_results[user_id] = []
    user_current_index[user_id] = 0

    print(f" Инициализирован поиск для пользователя {user_id}")
    print(f"   Параметры: {search_params}")


def get_user_search_params(user_id):
    """Возвращает параметры поиска пользователя"""
    return user_search_data.get(user_id)


def get_user_results(user_id):
    """Возвращает результаты поиска пользователя"""
    return user_search_results.get(user_id, [])


def get_current_index(user_id):
    """Возвращает текущий индекс для пользователя"""
    return user_current_index.get(user_id, 0)


def set_user_results(user_id, results):
    """Устанавливает результаты поиска для пользователя"""
    user_search_results[user_id] = results
    user_current_index[user_id] = 0  # Сбрасываем на начало
    print(f" Сохранено {len(results)} результатов для пользователя {user_id}")


def get_next_user(user_id):
    """
    Возвращает следующего пользователя из результатов поиска.

    Returns:
        dict: данные пользователя или None, если результаты закончились
    """
    results = get_user_results(user_id)
    current_idx = get_current_index(user_id)

    if not results or current_idx >= len(results):
        return None

    user = results[current_idx]
    user_current_index[user_id] = current_idx + 1  # Увеличиваем индекс

    return user


def has_more_results(user_id):
    """Проверяет, есть ли ещё результаты для показа"""
    results = get_user_results(user_id)
    current_idx = get_current_index(user_id)
    return results and current_idx < len(results)


def clear_user_state(user_id):
    """Очищает состояние пользователя"""
    if user_id in user_search_data:
        del user_search_data[user_id]
    if user_id in user_search_results:
        del user_search_results[user_id]
    if user_id in user_current_index:
        del user_current_index[user_id]
    print(f" Очищено состояние пользователя {user_id}")