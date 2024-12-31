from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json



US_CODE = "https://uscode.house.gov/browse/&edition=prelim"
US_LAW ="https://www.congress.gov/public-laws/118th-congress"
FEDERAL_REGISTER_FEED = "https://www.federalregister.gov/api/v1/documents.rss?"
REFULATORY_RULES = "https://www.regulations.gov/search?documentTypes=Rule&sortBy=postedDate&sortDirection=desc"



def scrape_content():
    print("Scrapping USA")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    content_list = []
    try:
        driver.get(US_LAW)
        
        # Wait for the page to load and locate all the main elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody[aria-live='polite']"))
        )
        # Locate the tbody element
        tbody = driver.find_element(By.CSS_SELECTOR, "tbody[aria-live='polite']")
        # Find all the rows within tbody
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        # Iterate through each row and extract the data
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            title = ""
            link = ""
            date = ""
            for i, cell in enumerate(cells):
                if i == 1:
                    title += cell.text + " "
                elif i == 2:
                    title += cell.text
                    link = cell.get_attribute("href")
                elif i == 3:
                    date = cell.text
                    

            content_list.append({
                'Title': title,
                'Summary': "",
                'Country': "USA",
                'Entity': "Congress",
                'Link': link,
                'Timestamp': date
            })
            print(f'{title}, {link}, {date} \n')
    except Exception as e:
        print(f"Error during scraping: {e}")
    return content_list



if __name__ == '__main__':
   content_list = scrape_content()