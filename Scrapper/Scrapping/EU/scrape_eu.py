import json
import feedparser


BASE_URL = "https://eur-lex.europa.eu/EN/display-feed.rss?rssId=162"


def scrape_content():
    content_list = []
    try:
        url_content = feedparser.parse(BASE_URL)
        for entry in url_content.entries:
            title = entry.get('title', 'No Title')
            link = entry.get('link', 'No Link')
            published = entry.get('published', 'No Published Date')
            content_list.append({'title': title, 'link': link, 'date': published})
    except Exception as e:
        print(e)
    return content_list