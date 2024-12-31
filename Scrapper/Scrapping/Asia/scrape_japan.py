import requests
from bs4 import BeautifulSoup
import json
from googletrans import Translator

translator = Translator()

BASE_URL = "https://www.japaneselawtranslation.go.jp/en/news"

def scrape_content():
    print("Scraping Japan")
    content_list = []
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        tr_tags = soup.find_all('tr', limit=15)
        
        for tr_tag in tr_tags:
            date_tag = tr_tag.find('td', class_='date')
            date = date_tag.get_text(strip=True) if date_tag else "No date found"
            
            info_tag = tr_tag.find('td', class_='info')
            if info_tag:
                link_tag = info_tag.find('a')
                link = link_tag.get('href') if link_tag else "No link found"
                title = link_tag.get_text(strip=True) if link_tag else "No content found"                
            else:
                link = title = "No info found"
            
            summary = ""
            if link and not link.endswith('pdf'):  # Avoid PDF links
                try:
                    response_summary = requests.get(link, timeout=10)
                    response_summary.raise_for_status()
                    soup_summary = BeautifulSoup(response_summary.text, "html.parser")
                    summary_div = soup_summary.find('div', class_='anchor')
                    if summary_div:
                        summary = summary_div.get_text(separator="\n", strip=True)
                except Exception as e:
                    print(f"Error fetching summary for {link}: {e}")
                    summary = "Failed to fetch summary."
    
            content_list.append({
                'Title': title,
                'Summary': summary,
                'Country': "Japan",
                'Entity': "Japan",
                'Link': link,
                'Timestamp': date
            })
    
    except Exception as e:
        print(f"Error: {e}")
    
    return content_list