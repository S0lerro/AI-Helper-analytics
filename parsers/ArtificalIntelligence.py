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

url = 'https://www.artificialintelligence-news.com/artificial-intelligence-news/'

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")

# Создайте драйвер с использованием service и options
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

for _ in range(3):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

headings_list = [h.get_text() for h in soup.find_all("h1", class_="elementor-heading-title elementor-size-default")]
headings_list.pop(0)
time_list = [t.get_text() for t in soup.find_all("p", class_="elementor-heading-title elementor-size-default") if re.search(r'\d', t.get_text())]
links_list = [h.find("a")["href"] for h in soup.find_all("h1", class_="elementor-heading-title elementor-size-default") if h.find("a", href=True)]

driver.quit()

descriptions_list = []

# Создайте новый драйвер для получения описаний
driver = webdriver.Chrome(options=chrome_options)

for link in links_list:
    driver.get(link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    paragraphs = soup.find_all("p")
    description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    descriptions_list.append(description_text.strip())

driver.quit()

df = pd.DataFrame({
    "Заголовок": headings_list,
    "Время публикации": time_list,
    "Описание": descriptions_list,
    "Ссылка": links_list
})

df.to_csv("ArtificialIntelligenceFrame.csv", index=False, encoding="utf-8")
