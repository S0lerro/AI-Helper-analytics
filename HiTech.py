from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm

def parse_news_title(soup):
    articles = soup.find_all("h3", class_="c30ebf5669 d153213e9a ea25cccb97")
    news_text = []
    for article in articles:
        title = article.find("a",
                             class_="da2727fca3 cbde347509 e65bdf6865")
        if title:
            news_text.append(title.get_text(strip=True))
    return news_text


def parse_news_time(soup):
    articles_time = soup.find_all("div", class_="f2eee589ba fdd5bbc15b e53e657292 a7a6fb85f2")
    news_time = []
    for article_time in articles_time:
        time_info = article_time.find("time", class_="js-ago")
        if time_info:
            news_time.append(time_info.get_text(strip=True))
    return news_time


def parse_article_links(soup):
    article_links = []
    articles = soup.find_all("h3")
    for article in articles:
        link = article.find("a", href=True)
        if link:
            article_links.append(link["href"])
    return article_links


def parse_article_descriptions(urls):
    all_paragraphs = []
    for url in tqdm(urls, desc="Парсинг статей"):
        while True:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.content, "lxml")
                time_tag = soup.find("time")
                elements = soup.select(".b6a5d4949c[article-item-type=html]")
                all_paragraphs.append(" ".join([p.get_text(strip=True) for p in elements]))
                if time_tag:
                    break
            except Exception as e:
                print(e)

    return all_paragraphs


def parse_rbc_news(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при загрузке страницы: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "lxml")

    news_text = parse_news_title(soup)
    news_time = parse_news_time(soup)
    article_links = parse_article_links(soup)

    descriptions = parse_article_descriptions(article_links)


    df_final = pd.DataFrame({
        "Заголовок": news_text,
        "Время и автор публикации": news_time,
        "Описание": descriptions,
        "Ссылка": article_links
    })
    filename = "../../../Desktop/Сава/Проекты/Сбер-помощник аналатика/parsers/HiTechFrame.csv"
    df_final.to_csv(filename, index=False, encoding="utf-8")

    return filename

def main():
    url = "https://hi-tech.mail.ru/tag/neyroseti/"
    filename = parse_rbc_news(url)
    print("Парсинг завершен!")
    print(f"Данные сохранены в файл: {filename}")


if __name__ == "__main__":
    main()
