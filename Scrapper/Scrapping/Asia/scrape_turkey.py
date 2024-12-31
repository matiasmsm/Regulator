from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json
import time

load_dotenv()
BASE_URL = "https://moral.av.tr/en/legal-updates"


def scrape_content(driver):
    base_url = BASE_URL
    news_data = []

    try:
        driver.get(base_url)
        time.sleep(5)
        
        news_elements = driver.find_elements(By.CLASS_NAME, "news-padding")

        for news_element in news_elements:
            date = news_element.find_element(By.CLASS_NAME, "news-list-date").text.strip()
            
            link = news_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            content = news_element.find_element(By.CLASS_NAME, "news-list-text-explain").text.strip()
            
            news_data.append({
                "date": date,
                "link": link,
                "content": content
            })

        for item in news_data:
            print(f"Date: {item['date']}")
            print(f"Link: {item['link']}")
            print(f"Content: {item['content']}")
            print("=" * 80)
    except Exception as e:
        print(e)
    return news_data