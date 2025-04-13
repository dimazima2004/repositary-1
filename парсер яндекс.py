from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Автоматическая установка ChromeDriver
# driver = webdriver.Chrome(ChromeDriverManager().install())

# Словарь для замены русских названий месяцев на английские
month_mapping = {
    'января': 'January', 'февраля': 'February', 'марта': 'March',
    'апреля': 'April', 'мая': 'May', 'июня': 'June',
    'июля': 'July', 'августа': 'August', 'сентября': 'September',
    'октября': 'October', 'ноября': 'November', 'декабря': 'December'
}

def translate_date(date_str):
    """Переводит дату с русскими месяцами в формат datetime."""
    for ru_month, en_month in month_mapping.items():
        if ru_month in date_str:
            date_str = date_str.replace(ru_month, en_month)
            break
    try:
        return datetime.strptime(date_str, '%d %B %Y')
    except ValueError:
        return None

# Инициализация веб-драйвера
driver = webdriver.Chrome() 
#Яндекс карты
# url = 'https://yandex.ru/maps/org/cdek/192209668223/reviews/?ll=37.255498%2C55.906320&utm_source=share&z=16'#YURL6
# url = 'https://yandex.ru/maps/org/cdek/102499689089/reviews/?indoorLevel=1&ll=37.354330%2C55.843566&utm_source=share&z=16' #MTN69
# url = 'https://yandex.ru/maps/org/cdek/135766037869/reviews/?ll=37.891801%2C55.715084&utm_source=share&z=16' #MSK2327
# url = 'https://yandex.ru/maps/org/cdek/110043210214/reviews/?ll=37.537218%2C55.538473&utm_source=share&z=16' #BTV65
url = 'https://yandex.ru/maps/org/cdek/230349162247/reviews/?ll=37.332959%2C55.845294&utm_source=share&z=12' #KRN10

driver.get(url)
input("Пройдите капчу и нажмите Enter, чтобы продолжить...")
# Функция скроллинга страницы
def scroll():
    elements = driver.find_elements(By.CLASS_NAME, 'business-reviews-card-view__review')
    count_el = len(elements)
    count_el2 = 0
    while count_el != count_el2:
        count_el = len(elements)
        last_element = elements[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", last_element)
        sleep(4)  # Даем время для загрузки новых элементов
        elements = driver.find_elements(By.CLASS_NAME, 'business-reviews-card-view__review')
        count_el2 = len(elements)
    return count_el2

# Выполняем скроллинг
scroll()
print("Скроллинг завершен!")

# Получаем HTML код страницы
data = driver.page_source

# Разбираем HTML с помощью BeautifulSoup
soup = BeautifulSoup(data, 'html.parser')

# Находим все блоки отзывов
information_block = soup.find_all(class_='business-review-view__info')

# Инициализация структуры данных
keys = {'№': [], 'Имя': [], 'Уровень': [], 'Рейтинг': [], 'Дата': [], 'Комментарий': []}

# Парсим данные из каждого блока
for idx, block in enumerate(information_block, start=1):
    keys['№'].append(idx)  # Номер отзыва

    # Имя комментатора
    name = block.find('span', {'dir': 'auto', 'itemprop': 'name'})
    keys['Имя'].append(name.text if name else 'Ошибка')

    # Уровень комментатора
    level = block.find(class_='business-review-view__author-caption')
    keys['Уровень'].append(level.text if level else 'Ошибка')

    # Рейтинг
    try:
        ratings = block.find('span', itemprop='reviewRating', itemtype='http://schema.org/Rating')
        rating = ratings.find_all('meta') if ratings else []
        keys['Рейтинг'].append(rating[2]['content'] if len(rating) > 2 else 'Ошибка')
    except:
        keys['Рейтинг'].append('Ошибка')

    # Дата отзыва
    review_date = block.find('span', {'class': 'business-review-view__date'})
    keys['Дата'].append(review_date.text if review_date else 'Ошибка')

    # Текст отзыва
    comment = block.find('span', {'class': 'business-review-view__body-text'})
    keys['Комментарий'].append(comment.text if comment else 'Ошибка')

# Закрываем браузер
driver.quit()

# Проверяем длины всех списков и синхронизируем их
max_length = max(len(keys[col]) for col in keys)
for col in keys:
    while len(keys[col]) < max_length:
        keys[col].append('Ошибка')

# Создаем DataFrame
df = pd.DataFrame(keys)
df.to_excel('data.xlsx', index=False)
print("Все отзывы успешно сохранены!")

# # Выгрузка в CSV для того, чтобы выгрузить в google sheets
# df.to_excel('yandex_reviews.xlsx', index=False, encoding='utf-8')
# print("Данные сохранены в файл yandex_reviews.xlsx")

# df['Дата'] = df['Дата'].apply(lambda x: translate_date(x) if isinstance(x, str) else None)
# df['Дата'] = df['Дата'].dt.date
# # Укажите параметры фильтрации
# start_date = datetime(2025, 2, 1).date()  # Начальная дата
# end_date = datetime(2025, 2, 28).date()  # Конечная дата

# Фильтрация по дате
# filtered_df = df[(df['Дата'] >= start_date) & (df['Дата'] <= end_date)]
# print("Отфильтрованные данные:\n", filtered_df)

# Сохраняем отфильтрованные данные
# filtered_df.to_excel('filtered_reviews.xlsx', index=False)
# print("Фильтрованные отзывы сохранены в файл filtered_reviews.xlsx!")