# модуль клавиатуры

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_main_keyboard():
    """Основная клавиатура (главное меню)"""
    keyboard = VkKeyboard(one_time=False)  # one_time=False - клавиатура остаётся

    # Первый ряд
    keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)

    # Второй ряд
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Помощь', color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def get_search_keyboard():
    """Клавиатура во время поиска"""
    keyboard = VkKeyboard(one_time=False)

    # Первый ряд
    keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('В избранное', color=VkKeyboardColor.PRIMARY)

    # Второй ряд
    keyboard.add_line()
    keyboard.add_button('Стоп', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Помощь', color=VkKeyboardColor.SECONDARY)

    # Третий ряд
    keyboard.add_line()
    keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def get_empty_keyboard():
    """Пустая клавиатура (скрывает кнопки)"""
    keyboard = VkKeyboard.get_empty_keyboard()
    return keyboard