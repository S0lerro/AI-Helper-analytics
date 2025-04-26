from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
import pandas as pd

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
    finded_href = href.find("a", attrs={"data-yandex-name": "from_center"}, href = True)
    if finded_href:
        links.append(finded_href["href"])

times_list = []
desc_list = []
for i in range(len(links)):
    response = requests.get(links[i])
    soup = BeautifulSoup(response.content, "lxml")
    time_element = soup.find("time", class_="article__header__date")
    times_list.append(time_element.get_text(strip=True) if time_element else None)

    paragraphs = soup.find_all("p")
    description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    desc_list.append(description_text.strip() if description_text else None)

print(len(headings), len(times_list), len(desc_list), len(links))

df = pd.DataFrame({
    "Заголовок": headings,
    "Время публикации": times_list,
    "Описание": desc_list,
    "Ссылка": links
})

df.to_csv("RBCFrame.csv", index=False, encoding="utf-8")


