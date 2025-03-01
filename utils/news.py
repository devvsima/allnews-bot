import re

import feedparser
import requests
from rss_parser import RSSParser


def get_rss_data(feed_url: str):
    response = requests.get(feed_url)
    rss = RSSParser.parse(response.text)
    data = list()
    for item in rss.channel.items:
        data.append(
            dict(
                title=item.title.content,
                link=item.link.content,
            )
        )
    return data


def get_feed_data(feed_url: str) -> list[dict]:
    feed = feedparser.parse(feed_url)
    data = [
        {
            "title": x["title"],
            "link": x["link"],
            "content": x["content"][0]["value"] if x.get("content") else "",
            "category": "/".join([t["term"] for t in x["tags"]]) if x.get("tags") else "",
        }
        for x in feed["entries"]
    ]
    return data


def get_news_tsn(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="https://tsn.ua/rss")
    for cat in categories:
        if cat in ["Політика 🏛️", "Спорт ⚽", "Економіка 💰"]:
            news.extend(
                [
                    {
                        "title": entry["title"],
                        "link": entry["link"],
                        "source": source,
                        "category": cat,
                    }
                    for entry in feed_data
                    if entry["category"] == cat.split()[0]
                ]
            )
        elif cat in ["Технології 💻"]:
            news.extend(
                [
                    {
                        "title": entry["title"],
                        "link": entry["link"],
                        "source": source,
                        "category": cat,
                    }
                    for entry in feed_data
                    if entry["category"] == "Технологія"
                ]
            )
    return news


def get_news_radiosvoboda(source: str, categories: list[str]):
    news = list()
    for cat in categories:
        if cat == "Політика 🏛️":
            feed_url = "https://www.radiosvoboda.org/api/ziqioejuip"
        elif cat in ["Економіка 💰"]:
            feed_url = "https://www.radiosvoboda.org/api/zpyp_e-rm_"
        elif cat in ["Спорт ⚽"]:
            feed_url = "https://www.radiosvoboda.org/api/ztpmmyei-mmy"
        else:
            continue
        feed = feedparser.parse(feed_url)
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed["entries"]
            ]
        )
    return news


def get_news_nv(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="https://nv.ua/ukr/rss/all.xml")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = re.compile("Політика|Геополітика")
        elif cat == "Технології 💻":
            regexp = re.compile("Техно|Гаджети")
        elif cat == "Спорт ⚽":
            regexp = "Спорт"
        elif cat == "Економіка 💰":
            regexp = re.compile("Економіка|Фінанси")
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["cat"])
            ]
        )
    return news


def get_news_nytimes(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = "politics"
        elif cat == "Технології 💻":
            regexp = "technology"
        elif cat == "Спорт ⚽":
            regexp = "athletic"
        elif cat == "Економіка 💰":
            regexp = "econom"
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["link"])
            ]
        )
    return news


def get_news_cnn(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="http://rss.cnn.com/rss/edition.rss")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = "politics"
        elif cat == "Технології 💻":
            regexp = "tech"
        elif cat == "Спорт ⚽":
            regexp = "sport"
        elif cat == "Економіка 💰":
            regexp = "business"
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["link"])
            ]
        )
    return news


def get_news_bbc(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="http://feeds.bbci.co.uk/news/rss.xml")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = "politics"
        elif cat == "Спорт ⚽":
            regexp = "sport"
        elif cat == "Економіка 💰":
            regexp = "business"
        else:
            continue
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["link"])
            ]
        )
    return news


def get_news_guardian(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="https://www.theguardian.com/international/rss")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = "politics"
        elif cat == "Спорт ⚽":
            regexp = "sport"
        elif cat == "Технології 💻":
            regexp = "technology"
        else:
            continue
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["category"].lower())
            ]
        )
    return news


def get_news_unian(source: str, categories: list[str]):
    news = list()
    feed_data = get_feed_data(feed_url="https://rss.unian.net/site/news_ukr.rss")
    for cat in categories:
        if cat == "Політика 🏛️":
            regexp = "politics"
        elif cat == "Спорт ⚽":
            regexp = "sport"
        elif cat == "Технології 💻":
            regexp = "techno"
        elif cat == "Економіка 💰":
            regexp = "economics"
        else:
            continue
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in feed_data
                if re.findall(regexp, entry["link"])
            ]
        )
    return news


def get_news_wp(source: str, categories: list[str]):
    news = list()
    for cat in categories:
        if cat == "Політика 🏛️":
            feed_url = "https://feeds.washingtonpost.com/rss/politics"
        elif cat == "Економіка 💰":
            feed_url = "https://feeds.washingtonpost.com/rss/business"
        elif cat == "Спорт ⚽":
            feed_url = "https://feeds.washingtonpost.com/rss/sports"
        elif cat == "Технології 💻":
            feed_url = "http://feeds.washingtonpost.com/rss/business/technology"
        data = get_rss_data(feed_url)
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in data
            ]
        )
    return news


def get_news_korrespondent(source: str, categories: list[str]):
    news = list()
    for cat in categories:
        if cat == "Політика 🏛️":
            feed_url = "http://k.img.com.ua/rss/ua/politics.xml"
        elif cat == "Економіка 💰":
            feed_url = "http://k.img.com.ua/rss/ua/economics.xml"
        elif cat == "Спорт ⚽":
            feed_url = "http://k.img.com.ua/rss/ua/sport.xml"
        elif cat == "Технології 💻":
            feed_url = "http://k.img.com.ua/rss/ua/technews.xml"
        data = get_feed_data(feed_url)
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in data
            ]
        )
    return news


def get_news_liga(source: str, categories: list[str]):
    news = list()
    for cat in categories:
        if cat == "Політика 🏛️":
            feed_url = "https://www.liga.net/news/politics/rss.xml"
        elif cat == "Економіка 💰":
            feed_url = "https://www.liga.net/news/economics/rss.xml"
        elif cat == "Спорт ⚽":
            feed_url = "https://www.liga.net/news/sport/rss.xml"
        elif cat == "Технології 💻":
            feed_url = "https://www.liga.net/tech/all/rss.xml"
        data = get_feed_data(feed_url)
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in data
            ]
        )
    return news


def get_news_rbc(source: str, categories: list[str]):
    news = list()
    for cat in categories:
        if cat == "Політика 🏛️":
            feed_url = "https://www.rbc.ua/static/rss/ukrnet.politics.ukr.rss.xml"
        elif cat == "Економіка 💰":
            feed_url = "https://www.rbc.ua/static/rss/ukrnet.economic.ukr.rss.xml"
        elif cat == "Спорт ⚽":
            feed_url = "https://www.rbc.ua/static/rss/ukrnet.sport.ukr.rss.xml"
        else:
            continue
        data = get_feed_data(feed_url)
        news.extend(
            [
                {"title": entry["title"], "link": entry["link"], "source": source, "category": cat}
                for entry in data
            ]
        )
    return news


def get_news(categories: list[str], sources: list[str], limit=5):
    news_list = []
    for s in sources:
        if s == "ТСН":
            source_news: list[dict] = get_news_tsn(s, categories)
        elif s == "Радіо Свобода":
            source_news: list[dict] = get_news_radiosvoboda(s, categories)
        elif s == "Новое Время":
            source_news: list[dict] = get_news_nv(s, categories)
        elif s == "The New York Times":
            source_news: list[dict] = get_news_nytimes(s, categories)
        elif s == "CNN":
            source_news: list[dict] = get_news_cnn(s, categories)
        elif s == "The Washington Post":
            source_news: list[dict] = get_news_wp(s, categories)
        elif s == "BBC News":
            source_news: list[dict] = get_news_bbc(s, categories)
        elif s == "The Guardian":
            source_news: list[dict] = get_news_guardian(s, categories)
        elif s == "УНІАН":
            source_news: list[dict] = get_news_unian(s, categories)
        elif s == "Кореспондент.net":
            source_news: list[dict] = get_news_korrespondent(s, categories)
        elif s == "ЛІГА.net":
            source_news: list[dict] = get_news_liga(s, categories)
        elif s == "РБК Україна":
            source_news: list[dict] = get_news_rbc(s, categories)
        news_list.extend(source_news[:limit])

    return news_list


if __name__ == "__main__":
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    sources = ["УНІАН"]
    get_news(categories, sources)
