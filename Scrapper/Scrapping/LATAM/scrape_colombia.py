from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json


BASE_URL = "http://www.secretariasenado.gov.co/leyes-de-la-republica"


def scrape_content():
    print("Scraping Colombia")

    driver = webdriver.Chrome(ChromeDriverManager().install())
    content_list = []
    try:
        driver.get(BASE_URL)
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="blockrandom"]'))
        )

        driver.switch_to.frame(iframe)

        # Locate all rows in the table
        rows = driver.find_elements(By.XPATH, '//tr[@class="odd"]')

        # Iterate through each row and extract contents
        for row in rows:
            # Extract the contents of each column (td)
            id_number = row.find_element(By.XPATH, './td[1]').text.strip()
            title = "Ley Nº " + id_number + " " + row.find_element(By.XPATH, './td[3]/h3/a').text.strip()
            entity = row.find_element(By.XPATH, '//*[@id="searchForm"]/table[2]/tbody/tr/td[2]').text.strip()
            date = row.find_element(By.XPATH, './td[3]/div[contains(text(), "Fecha de Sanción")]/b').text.strip()
            link = row.find_element(By.XPATH, './td[3]/h3/a').get_attribute('href')

            # Append to content list
            content_list.append({
                'Title': title,
                'Summary': "",
                'Country': "Colombia",
                'Entity': entity,
                'Link': link,
                'Timestamp': date
            })  

        driver.switch_to.default_content()
    except Exception as e:
        print(e)
    driver.quit()
    return content_list