from . import scrape_eu

def scrape():
    eu_data = scrape_eu.scrape_content()
    return eu_data