# тестируем фото
import vk_tools


TEST_USER_ID = 4199030



photos = vk_tools.get_top_photos(TEST_USER_ID, count=3)

if photos:
    print(f"\n Получено {len(photos)} фото:")
    for i, photo in enumerate(photos, 1):
        print(f"{i}. {photo}")

    print("\nПример для бота:")
    print(f'attachments = "{",".join(photos)}"')
else:
    print("\ Фото не получены")

