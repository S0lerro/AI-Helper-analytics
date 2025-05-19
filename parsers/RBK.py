from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import requests
import pandas as pd

# Словарь для преобразования русских названий месяцев в числа
month_mapping = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

url = 'https://rbc.ru/'

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

scroll_count = 3
for i in range(scroll_count):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

timeout = 10
try:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
except:
    print("Превышено время ожидания загрузки страницы.")

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

driver.quit()

headings = []
no_wrap = soup.find_all("span", class_="no-wrap")
for heading in no_wrap:
    normal_wrap = heading.find("span", class_="normal-wrap")
    if normal_wrap:
        headings.append(heading.get_text())

links = []
hrefs = soup.find_all("div", class_="item__wrap l-col-center")
for href in hrefs:
    finded_href = href.find("a", attrs={"data-yandex-name": "from_center"}, href=True)
    if finded_href:
        links.append(finded_href["href"])

times_list = []
desc_list = []
for i in range(len(links)):
    response = requests.get(links[i])
    soup = BeautifulSoup(response.content, "lxml")
    time_element = soup.find("time", class_="article__header__date")

    if time_element:
        date_text = time_element.get_text(strip=True)
        try:
            # Отделяем дату от времени
            date_part = date_text.split(',')[0].strip()
            day, month_ru = date_part.split()

            # Получаем числовой месяц из словаря
            month = month_mapping.get(month_ru.lower(), '00')

            # Получаем текущий год
            current_year = datetime.now().year

            # Форматируем дату в нужный формат
            formatted_date = f"{day.zfill(2)}.{month}.{current_year}"
            times_list.append(formatted_date)
        except Exception as e:
            print(f"Ошибка при обработке даты '{date_text}': {e}")
            times_list.append(date_text)  # Оставляем оригинальный текст при ошибке
    else:
        times_list.append(None)

    paragraphs = soup.find_all("p")
    description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    desc_list.append(description_text.strip() if description_text else None)

df = pd.DataFrame({
    "Заголовок": headings,
    "Время публикации": times_list,
    "Описание": desc_list,
    "Ссылка": links
})

df.to_csv("../Frames/RBCFrame.csv", index=False, encoding="utf-8")
