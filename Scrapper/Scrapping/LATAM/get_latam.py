from . import scrape_brazil, scrape_chile, scrape_colombia, scrape_mexico

def scrape():
    brazil_data = scrape_brazil.scrape_content()
    chile_data = scrape_chile.scrape_content()
    colombia_data = scrape_colombia.scrape_content()
    mexico_data = scrape_mexico.scrape_content()
    
    all_data = brazil_data + chile_data + colombia_data + mexico_data
    return all_data