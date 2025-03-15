from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://hi-tech.mail.ru/news/')

html = driver.page_source
soup = BeautifulSoup(html, "lxml")
headings_list = [h.get_text() for h in soup.find_all("a", class_="da2727fca3 cbde347509 e65bdf6865")]
time_list = [t.get_text() for t in soup.find_all("span", class_="f2eee589ba fdd5bbc15b e53e657292 a7a6fb85f2")]
links_list = [l.find("a")["href"] for l in soup.find_all("h3", class_="c30ebf5669 d153213e9a adca14409f") if l.find('a', href=True)]
description_list = []
for description in links_list:
    response = requests.get(description)
    soup = BeautifulSoup(response.content, "lxml")
    while True:
        paragraphs = soup.find_all("p")
        paragraphs_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        description_list.append(paragraphs_text.strip())
        if "b8b4d1014b d110000fb2 a57b214bb9 e8e74a6a29 d91587b71f":
            break
print(headings_list, time_list, links_list, description_list)
print(len(headings_list), len(time_list), len(links_list), len(description_list))

df = pd.DataFrame({
    "Заголовок": headings_list,
    "Время публикации": time_list,
    "Описание": description_list,
    "Ссылка": links_list
})

df.to_csv("HiTechFrame.csv", index=False, encoding="utf-8")
