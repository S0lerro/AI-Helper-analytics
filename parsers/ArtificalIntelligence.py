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
import re

url = 'https://www.artificialintelligence-news.com/artificial-intelligence-news/'

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

headings_list = []
no_wrap = soup.find_all("h1", class_="elementor-heading-title elementor-size-default")
for heading in no_wrap:
    normal_wrap = heading.find("a")
    if normal_wrap:
        headings_list.append(heading.get_text())

time_list = []
parent_time = soup.find_all("div", class_="elementor-widget-container")
for times in parent_time:
    time_element = times.find("p", class_="elementor-heading-title elementor-size-default")
    if time_element:
        time_text = time_element.get_text()
        if re.search(r'\d', time_text):
            time_list.append(time_text)
time_list.pop(0)
links_list = []
parent_link = soup.find_all("h1", class_="elementor-heading-title elementor-size-default")
for links in parent_link:
    link = links.find("a", href = True)
    if link:
        links_list.append(link["href"])

descriptions_list = []
for i in range(len(links_list)):
    response = requests.get(links_list[i])
    soup = BeautifulSoup(response.content, "lxml")
    paragraphs = soup.find_all("p")
    description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    descriptions_list.append(description_text.strip() if description_text else None)

print(len(headings_list), len(time_list), len(descriptions_list), len(links_list), time_list)

df = pd.DataFrame({
    "Заголовок": headings_list,
    "Время публикации": time_list,
    "Описание": descriptions_list,
    "Ссылка": links_list
})

df.to_csv("ArtificalIntelligenceFrame.csv", index=False, encoding="utf-8")

