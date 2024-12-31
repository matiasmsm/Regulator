from . import scrape_china, scrape_japan, scrape_turkey

def scrape():
    china_data = scrape_china.scrape_content()
    japan_data = scrape_japan.scrape_content()
    #turkey_data = scrape_turkey.scrape_content()
    
    #Merge the data
    all_data = china_data + japan_data
    return all_data
