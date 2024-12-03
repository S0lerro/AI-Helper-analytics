import random
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ======================================================================================================================

url = "https://hi-tech.mail.ru/tag/neyroseti/"

user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7"
    ]

user_agent = random.choice(user_agents)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"--user-agent={user_agent}")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)


# ======================================================================================================================

scrapped_text = []
wait = WebDriverWait(driver,5)
for i in range(1, 10):
    news_text = driver.find_element(By.XPATH,f"//*[@id='hitech-app-root']/div[2]/div[4]/div[1]/div/div/div/section/main/div[1]/div[{i}]/div[3]/h3/a").text
    scrapped_text.append(news_text)
scrapped_time = []
for i in range(1, 10):
    news_time = driver.find_element(By.XPATH,f"//*[@id='hitech-app-root']/div[2]/div[4]/div[1]/div/div/div/section/main/div[1]/div[{i}]/div[2]/div/time").text
    scrapped_time.append(news_time)
dict = {"Текст": scrapped_text, "Время и автор публикации": scrapped_time}
df = pd.DataFrame(dict)
df.to_csv('hi-techFrame.csv', index=False)
driver.quit()
