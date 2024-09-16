# news/management/commands/scrape_news.py

from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from news.models import VegetableMarget


class Command(BaseCommand):
    help = 'Scrape and store vegetable market data'

    def handle(self, *args, **kwargs):
        url = 'https://www.ktm2day.com/vegetables-price-in-nepali-market/'
        response = requests.get(url)
        if response.status_code == 200:
            # Clear previous records
            VegetableMarget.objects.all().delete()

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='table-striped')
            rows = table.find_all('tr')[1:]  # Skip the header row

            for row in rows:
                columns = row.find_all('td')
                name = columns[0].get_text().strip()
                min_price = columns[1].get_text().replace('Rs ', '')
                max_price = columns[2].get_text().replace('Rs ', '')
                average_price = columns[3].get_text().replace('Rs ', '')

                # Create or update VegetableMarket object
                vegetable, created = VegetableMarget.objects.get_or_create(
                    name=name,
                    defaults={
                        'min_price': min_price,
                        'max_price': max_price,
                        'average_price': average_price,
                        'created_at': timezone.now()
                    }
                )

                if not created:
                    # Update existing VegetableMarket object
                    vegetable.min_price = min_price
                    vegetable.max_price = max_price
                    vegetable.average_price = average_price
                    vegetable.updated_at = timezone.now()
                    vegetable.save()

                print(f"Data for {name} has been scraped and stored.")

        else:
            self.stdout.write(self.style.ERROR('Failed to fetch news data from the website'))
