from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import pandas as pd

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

headings = []
no_wrap = soup.find_all("div", class_="jsx-3664110909 cWiP4f7Z")
for heading in no_wrap:
    normal_wrap = heading.find("div", class_="jsx-3664110909 jsx-1605541728 fxLbEhKG")
    if normal_wrap:
        headings.append(heading.get_text())

times_list = []
times = soup.find_all("div", class_="jsx-3664110909 cWiP4f7Z")
for time in times:
    normal_wrap = time.find("div", class_="jsx-2175634919 texts")
    if normal_wrap:
        times_list.append(normal_wrap.get_text())

links = []
hrefs = soup.find_all("div", attrs={"data-qa" : "lb-block"})
for href in hrefs:
    finded_href = href.find("a", class_="jsx-3299022473 link", href = True)
    if finded_href:
        links.append("https://www.ferra.ru" + finded_href["href"])
links.pop()

desc_list = []
for i in range(len(links)):
    response = requests.get(links[i])
    soup = BeautifulSoup(response.content, "lxml")
    paragraphs = soup.find_all("p")
    description_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    desc_list.append(description_text.strip() if description_text else None)

print(len(headings), len(times_list), len(links), len(desc_list))

df = pd.DataFrame({
    "Заголовок": headings,
    "Время публикации": times_list,
    "Описание": desc_list,
    "Ссылка": links
})

df.to_csv("FerraFrame.csv", index=False, encoding="utf-8")


