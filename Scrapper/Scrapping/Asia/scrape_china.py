import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import chardet

translator = Translator()

BASE_URL = "http://www.npc.gov.cn/npc/c2/c183"

def scrape_content():
    print("Scraping China")
    content_list = []
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()

        # Detect encoding using chardet
        result = chardet.detect(response.content)
        encoding = result['encoding']

        # Set the correct encoding for the response
        response.encoding = encoding
        
        # Now parse the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        a_tags = soup.select('ul li a')
        
        for idx, a_tag in enumerate(a_tags):
            link = BASE_URL[:-5] + a_tag.get('href')[2:]
            
            title = a_tag.get_text(strip=True)
            
            # Translate the title without manual encoding/decoding
            title = translator.translate(title, src='zh-cn', dest='en').text
            
            date_tag = a_tag.find_next('span')
            date = date_tag.get_text(strip=True)
                        
            response_summary = requests.get(link, timeout=10)
            response_summary.encoding = encoding  # Ensure correct encoding for the summary page
            soup_summary = BeautifulSoup(response_summary.text, "html.parser")
            summary_div = soup_summary.find('div', class_='TRS_Editor')
            
            # Ensure summary text is extracted and translated properly
            summary = summary_div.get_text(separator="\n", strip=True)
            
            # Translate the summary without manual encoding/decoding
            summary = translator.translate(summary, src='zh-cn', dest='en').text

            content_list.append({'Title': title, 'Summary': summary, 'Country': "China", 'Entity': "China", 'Link': link, 'Timestamp': date})
            
    except Exception as e:
        print(f"Error: {e}")
    
    return content_list