from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json

load_dotenv()
BASE_URL = "https://lawlibrary.org.za/legislation/?q=&sort=-date"


def read_json():
    with open("chile.json", "r") as json_file:
        loaded_data = json.load(json_file)
        return loaded_data
        
def write_json(dict):
    with open("chile.json", "w") as json_file:
        json.dump(dict, json_file, indent=4)

def scrape_content(driver):
    base_url = BASE_URL
    content_dict = read_json()
    try:
        driver.get(base_url)
        # Wait for the page to load and the elements to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "d-flex.align-items-stretch"))
        )
        
        # Find all matching div elements
        divs = driver.find_elements(By.CLASS_NAME, "d-flex.align-items-stretch")
        
        for div in divs:
            # Extract the date
            date = div.find_element(By.CLASS_NAME, "card-text").text.strip()
            
            # Extract the title and link
            title_div = div.find_element(By.CLASS_NAME, "card-title.mb-3")
            title = title_div.find_element(By.TAG_NAME, "a").text.strip()
            link = title_div.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            # Print the extracted information
            print(f"Date: {date}")
            print(f"Title: {title}")
            print(f"Link: {link}")
            content_dict[title] = {'Date': date, 'Link': link}
        write_json(content_dict)
    except Exception as e:
        print(e)
    return content_dict



if __name__ == '__main__':
    driver = webdriver.Chrome(ChromeDriverManager().install())
    content_dict = scrape_content(driver)
    for key, content in content_dict.items():
        driver.get(content["Link"])
        h1_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="alturaResultados"]/div[2]/div/div/h1'))
        )
        title = h1_element.text
        content_dict[key]["Title"] = title
        
        themes = driver.find_element(By.XPATH, '//*[@id="alturaResultados"]/div[2]/div/div/div[3]/p[4]').text
        content_dict[key]["Themes"] = themes
        
        content = driver.find_element(By.XPATH, '//*[@id="alturaResultados"]/div[2]/div/div/div[3]/p[5]').text
        content_dict[key]["Content"] = content
    write_json(content_dict)