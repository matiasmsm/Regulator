from . import scrape_usa

def scrape():
    usa_data = scrape_usa.scrape_content()
    
    all_data = usa_data
    return all_data