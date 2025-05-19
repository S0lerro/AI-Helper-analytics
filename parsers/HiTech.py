from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm

m = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
     'декабря']


def parse_news_title(soup):
    articles = soup.find_all("h3", class_="c30ebf5669 d153213e9a adca14409f")
    news_text = []
    for article in articles:
        title = article.find("a", class_="da2727fca3 cbde347509 e65bdf6865")
        if title:
            news_text.append(title.get_text(strip=True))
    return news_text


def parse_news_time(soup):
    articles_time = soup.find_all("span", class_="f2eee589ba fdd5bbc15b e53e657292 a7a6fb85f2")
    news_time = []
    for article_time in articles_time:
        time_info = article_time.find("time", class_="js-ago")
        if time_info:
            date_str = time_info.get_text(strip=True)
            try:
                day, month_ru, year = date_str.split()  # Разделяем на части
                month_num = str(m.index(month_ru) + 1).zfill(2)  # Получаем номер месяца (04)
                formatted_date = f"{day.zfill(2)}.{month_num}.{year}"  # "18.04.2025"
                news_time.append(formatted_date)
            except (ValueError, AttributeError):
                news_time.append(date_str)  # Если не удалось разобрать, оставляем исходный формат
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
    while True:
        paragraphs = soup.find_all("p")
        description_list = []
        paragraphs_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        description_list.append(paragraphs_text.strip())
        if "b8b4d1014b d110000fb2 a57b214bb9 e8e74a6a29 d91587b71f":
            break

    news_text = parse_news_title(soup)
    news_time = parse_news_time(soup)
    article_links = parse_article_links(soup)

    descriptions = parse_article_descriptions(article_links)

    print(len(news_text), len(news_time), len(descriptions), len(article_links))
    df_final = pd.DataFrame({
        "Заголовок": news_text,
        "Время и автор публикации": news_time,
        "Описание": descriptions,
        "Ссылка": article_links
    })

    filename = "../Frames/HiTechFrame.csv"
    df_final.to_csv(filename, index=False, encoding="utf-8")

    return filename


def main():
    url = "https://hi-tech.mail.ru/news/"
    filename = parse_rbc_news(url)
    print("Парсинг завершен!")
    print(f"Данные сохранены в файл: {filename}")


if __name__ == "__main__":
    main()
