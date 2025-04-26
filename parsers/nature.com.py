from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

url = 'https://www.nature.com/latest-news'

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

# Scroll to load more content
for _ in range(3):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

headings_list = []
time_list = []
links_list = []

for h in soup.find_all("div", class_="c-article-item__copy"):
    headings_list.append(h.find("h3").get_text())
for t in soup.find_all("div", class_="c-article-item__footer"):
    time_list.append(t.find("span", class_="c-article-item__date").get_text())
for h in soup.find_all("div", class_="c-article-item__content c-article-item--with-image"):
    links_list.append("https://www.nature.com" + h.find("a", href=True)["href"])

driver.quit()

descriptions_list = []

driver = webdriver.Chrome(options=chrome_options)

for link in links_list:
    try:
        driver.get(link)

        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Try to find and click cookie button if it exists
        try:
            # Use CSS selector instead of CLASS_NAME for multiple classes
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            ".cc-button.cc-button--secondary.cc-button--contrast.cc-banner__button.cc-banner__button-accept"))
            )
            cookie_button.click()
            time.sleep(1)  # Wait for cookie banner to disappear
        except:
            pass  # If cookie button not found, continue

        # Get description
        paragraphs = driver.find_elements(By.CLASS_NAME, "article__teaser")
        description_text = " ".join([p.text for p in paragraphs])
        descriptions_list.append(description_text.strip())

    except Exception as e:
        print(f"Error processing {link}: {str(e)}")
        descriptions_list.append("")  # Add empty string if error occurs

driver.quit()

df = pd.DataFrame({
    "Заголовок": headings_list,
    "Время публикации": time_list,
    "Описание": descriptions_list,
    "Ссылка": links_list
})

df.to_csv("NatureFrame.csv", index=False, encoding="utf-8")