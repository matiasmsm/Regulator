from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from googletrans import Translator
from bs4 import BeautifulSoup


translator = Translator()

BASE_URL = "https://legislacao.presidencia.gov.br/"

def scrape_content():
    print("Scraping Brazil")

    driver = webdriver.Chrome(ChromeDriverManager().install())
    content_list = []
    try:
        driver.get(BASE_URL)
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "nav-link") and contains(@onclick, "pesquisaLegislacao")]'))
        )
        button.click()
        time.sleep(5)
        
        cards = driver.find_elements(By.CSS_SELECTOR, "div.card-header.p-0.col-12.border-0")
        data_list = []
        
        # Loop through each card to extract details
        for card in cards:
            try:
                # Extract the title
                title_element = card.find_element(By.CSS_SELECTOR, "h4.card-title a")
                title = title_element.text.strip()
                title = translator.translate(title, src='pt', dest='en').text if title else "No title available"

                link = title_element.get_attribute("href")

                # Extract the content
                content_element = card.find_element(By.CSS_SELECTOR, "p.card-category.text-muted.pt-0.mt-0.mb-2")
                content = content_element.text.strip()

                # Extract additional descriptive paragraph
                additional_info_element = card.find_element(By.CSS_SELECTOR, "p.pt-2")
                additional_content = additional_info_element.text.strip()

                # Extract the date
                date = None  # Add logic here to extract the date properly

                data_list.append((date, title, link))
            except Exception as e:
                print(f"Error processing card: {e}")
        
        for date, title, link in data_list:
            try:
                driver.get(link)
                summary = ""
                if link.startswith("https://www2.camara.leg.br"):
                    summary_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[2]'))
                    )
                else:
                    summary_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body'))
                    )
                summary = summary_element.text.strip() if summary_element else None
                
                # Translate only if summary exists
                if summary:
                    try:
                        summary = translator.translate(summary, src='pt', dest='en').text
                    except:
                        summary = ""

                content_list.append({
                    'Title': title,
                    'Summary': summary,
                    'Country': "Brazil",
                    'Entity': "Brazil",
                    'Link': link,
                    'Timestamp': date
                })
            except Exception as e:
                print(f"Error processing link {link}: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        driver.quit()
    return content_list
