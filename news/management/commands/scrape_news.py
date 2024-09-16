# news/management/commands/scrape_news.py

from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from news.models import News


class Command(BaseCommand):
    help = 'Scrape and store news data'

    def handle(self, *args, **kwargs):
        url = 'https://www.onlinekhabar.com/?search_keyword=agriculture'
        response = requests.get(url)
        if response.status_code == 200:
            # Clear previous records
            News.objects.filter(source='online_khabar').delete()

            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract and store news data
            news_posts = soup.find_all('div', class_='ok-news-post')
            for post in news_posts:
                title = post.find('h2', class_='ok-news-title-txt').text.strip()
                content_tag = post.find('div', class_='ok-title-info')
                content = content_tag.find('p').text.strip() if content_tag else ''
                source = 'online_khabar'
                link_tag = post.find('a')
                link = link_tag['href'] if link_tag else ''
                image_tag = post.find('img')
                img = image_tag['src'] if image_tag else ''

                News.objects.create(title=title, content=content, source=source, link=link, image=img)
            self.stdout.write(self.style.SUCCESS('News data scraped and stored successfully'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch news data from the website'))
