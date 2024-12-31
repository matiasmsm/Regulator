from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json

load_dotenv()
BASE_URL = "https://www.bcn.cl/leychile/consulta/portada_ulp"

def scrape_content():
    print("Scraping Chile")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    content_list = []
    try:
        driver.get(BASE_URL)
        
        # Wait for the page to load and locate all the main elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "d-flex.align-items-stretch"))
        )
        divs = driver.find_elements(By.CLASS_NAME, "d-flex.align-items-stretch")
        
        # Collect data from the main page
        data_list = []
        for div in divs:
            try:
                date = div.find_element(By.CLASS_NAME, "card-text").text.strip()
                title_div = div.find_element(By.CLASS_NAME, "card-title.mb-3")
                title = title_div.find_element(By.TAG_NAME, "a").text.strip()
                link = title_div.find_element(By.TAG_NAME, "a").get_attribute("href")
                data_list.append((date, title, link))
            except Exception as e:
                print(f"Error extracting data from main page element: {e}")
        
        # Visit each link and extract additional details
        for date, title, link in data_list:
            try:
                driver.get(link)
                
                # Wait for the summary element to be present
                summary_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="read-norma"]'))
                )
                summary = summary_element.text.strip()
                title = driver.find_element(By.XPATH, '//*[@id="alturaResultados"]/div[2]/div/div/h1').text
                
                # Append to content list
                content_list.append({
                    'Title': title,
                    'Summary': summary,
                    'Country': "Chile",
                    'Entity': "Chile",
                    'Link': link,
                    'Timestamp': date
                })                
            except Exception as e:
                print(f"Error extracting data from link {link}: {e}")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    driver.quit()
    return content_list
