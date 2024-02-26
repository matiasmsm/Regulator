import json
import feedparser

"""with Controller.from_port(port = 9051) as controller:
    controller.authenticate(password='your password set for tor controller port in torrc')
    print("Success!")
    controller.signal(Signal.NEWNYM)
    print("New Tor connection processed")"""



def get_urls_dict():
    with open("Archivos Json/fuentes_rss.json", 'r', encoding="utf-8") as fuentes_file:
        diccionario_fuentes = json.load(fuentes_file)
        return diccionario_fuentes

def crawl_regulatory_agencies():
    regulations_dict = get_urls_dict()
    for name, url  in regulations_dict.items():
        print(name)
        url_content = feedparser.parse(url)
        #dict_keys(['bozo', 'entries', 'feed', 'headers', 'href', 'status', 'encoding', 'version', 'namespaces'])
        for entry in url_content['entries']:
            title = entry['title']
            #dict_keys(['title', 'title_detail', 'summary', 'summary_detail', 'links', 'link', 'id', 'guidislink', 'tags', 'published', 'published_parsed', 'authors', 'author', 'author_detail'])
            serial_num = title[6:].split(':', 1)[0]
            #print(serial_num)
            if 'R' in serial_num:
                print(title)


crawl_regulatory_agencies()