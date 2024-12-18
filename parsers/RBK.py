from bs4 import BeautifulSoup
import pandas as pd
import requests

def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def parse_news_text(soup):
    articles = soup.find_all("span", class_="search-item__link-in")
    news_text = []
    for article_text in articles:
        title = article_text.find("span", class_="search-item__title")
        if title:
            news_text.append(title.get_text(strip=True))
    return news_text


def parse_news_time(soup):
    articles_time = soup.find_all("div", class_="search-item__bottom")
    news_time = []
    for article_time in articles_time:
        time_info = article_time.find("span", class_="search-item__category")
        if time_info:
            news_time.append(time_info.get_text(strip=True))
    return news_time


def parse_article_links(soup):
    article_links = []
    articles = soup.find_all("div", class_="search-item__wrap l-col-center")
    for article in articles:
        link = article.find("a", class_="search-item__link js-search-item-link", href=True)
        if link and 'href' in link.attrs:
            article_links.append(link["href"])
    return article_links


def parse_article_descriptions(urls):
    all_paragraphs = []
    for url in urls:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "lxml")
        paragraphs = soup.find_all("p")
        paragraphs_text = [p.get_text(strip=True) for p in paragraphs]
        all_paragraphs.append(" ".join(paragraphs_text))
    return all_paragraphs


def parse_rbc_news(file_path):
    html_content = load_html(file_path)
    soup = BeautifulSoup(html_content, "lxml")

    news_text = parse_news_text(soup)
    news_time = parse_news_time(soup)
    article_links = parse_article_links(soup)

    df_initial = pd.DataFrame({"Текст": news_text, "Время и автор публикации": news_time, "Ссылка": article_links})

    descriptions = parse_article_descriptions(article_links)

    df_final = pd.DataFrame({
        "Текст": news_text,
        "Время и автор публикации": news_time,
        "Описание": descriptions,
        "Ссылка": article_links
    })

    df_final.to_csv("RBKFrame.csv", index=False, encoding="utf-8")


def main():
    file_path = "source-page.html"
    parse_rbc_news(file_path)


if __name__ == "__main__":
    main()
