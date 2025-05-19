from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import time
from datetime import datetime

url = 'https://www.artificialintelligence-news.com/artificial-intelligence-news/'

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

# Прокрутка для загрузки всех статей
for _ in range(5):  # Увеличил количество прокруток
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

# Получение всех заголовков (кроме первого)
headings = soup.find_all("h1", class_="elementor-heading-title elementor-size-default")
headings_list = [h.get_text(strip=True) for h in headings[1:]]  # Пропускаем первый элемент

# Получение всех дат и преобразование формата
time_elements = soup.find_all("span", class_="elementor-icon-list-text")
time_list = []
for t in time_elements:
    date_text = t.get_text(strip=True)
    if re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',
                 date_text):
        try:
            date_obj = datetime.strptime(date_text, "%B %d, %Y")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            time_list.append(formatted_date)
        except ValueError:
            time_list.append(date_text)  # Оставляем оригинал, если не удалось преобразовать

# Получение всех ссылок
links_list = []
for h in headings[1:]:  # Пропускаем первый элемент
    link = h.find("a", href=True)
    if link:
        links_list.append(link["href"])

driver.quit()

# Получение описаний
descriptions_list = []
driver = webdriver.Chrome(options=chrome_options)

for link in links_list:
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        # Более точный выбор контента статьи
        article_content = soup.find("div", class_="elementor-widget-theme-post-content")
        if article_content:
            paragraphs = article_content.find_all("p")
            description_text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            description_text = ""

        descriptions_list.append(description_text.strip())
    except Exception as e:
        print(f"Ошибка при обработке {link}: {str(e)}")
        descriptions_list.append("")

driver.quit()

# Создание DataFrame
df = pd.DataFrame({
    "Заголовок": headings_list,
    "Время публикации": time_list,
    "Описание": descriptions_list,
    "Ссылка": links_list
})

# Удаление дубликатов
df = df.drop_duplicates(subset=['Ссылка'])

# Сохранение в CSV
df.to_csv("../Frames/ArtificialIntelligenceFrame.csv", index=False, encoding="utf-8")
