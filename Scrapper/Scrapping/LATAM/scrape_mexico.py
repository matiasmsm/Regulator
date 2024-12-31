import requests
from bs4 import BeautifulSoup
import json
from googletrans import Translator


translator = Translator()

BASE_URL = "https://www.diputados.gob.mx/LeyesBiblio/actual/ultima.htm"

def scrape_content():
    print("Scraping Mexico")
    content_list = []
    
    try:
        response = requests.get(BASE_URL, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table', {'id': 'table2'})

        # Extract all rows (tr elements) from the table
        rows = table.find_all('tr')

        for row in rows:
            date_td = row.find_all('td', valign='top')[0]
            date = date_td.get_text(strip=True)

            content_td = row.find_all('td', valign='top')[1]
            
            title_tag = content_td.find('a', href=True)
            title = title_tag.get_text(separator=' ', strip=True)
            link = title_tag['href'] if title_tag else "No title"

            summary = content_td.get_text(strip=True).replace(title, '').replace(link, '').strip()

            content_list.append({'Title': title, 'Summary': summary, 'Country': "Mexico", 'Entity': "Mexico", 'Link': link, 'Timestamp': date})
            
    except Exception as e:
        print(f"Error: {e}")
    
    return content_list