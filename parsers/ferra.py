from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import pandas as pd
import time

url = 'https://www.ferra.ru/news'

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

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

data = []

articles = soup.find_all("div", attrs={"data-qa": "lb-block"})

for article in articles:
    # Заголовок
    heading_tag = article.find("div", class_="jsx-4218023674 cACyR5DR")
    if heading_tag:
        heading_inner = heading_tag.find("div", class_="jsx-4218023674 jsx-3899589917 yLcXQQvt")
        heading = heading_inner.get_text(strip=True) if heading_inner else heading_tag.get_text(strip=True)
    else:
        heading = "None"

    # Время публикации
    time_tag = article.find("div", class_="jsx-4218023674 AIJ5ijeB")
    if time_tag:
        time_inner = time_tag.find("div", class_="jsx-2175634919 texts")
        pub_time = time_inner.get_text(strip=True) if time_inner else "Не указано."
    else:
        pub_time = "Не указано."

    link_tag = article.find("a", class_="jsx-3299022473 link", href=True)
    if link_tag:
        link = "https://www.ferra.ru" + link_tag["href"]

    if link:
        response = requests.get(link, timeout=10)
        soup_desc = BeautifulSoup(response.content, "lxml")
        paragraphs = soup_desc.find_all("p")
        description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        description = description_text.strip() if description_text else None

    if heading and link:
        data.append({
            "Заголовок": heading,
            "Время публикации": pub_time,
            "Описание": description,
            "Ссылка": link
        })

df = pd.DataFrame(data)
df = df.drop_duplicates(subset='Описание').reset_index(drop=True)

df.to_csv("FerraFrame.csv", index=False, encoding="utf-8")
