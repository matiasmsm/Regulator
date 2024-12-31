import fitz  # PyMuPDF
import re
import json

"""
    1. Download data

    2. Divide in subsections:
    return a flattened list of all nested subsections.
    Each subsection is a tuple, where:
    - the first element is a list of parent subtitles, starting with the page title
    - the second element is the text of the subsection (but not any children)

    3. Clean data --> empty spaces, html, etc...
    
    E.j: ['Concerns and controversies at the 2022 Winter Olympics']
    '{{Short description|Overview of concerns and controversies surrounding the Ga...'
    ['Concerns and controversies at the 2022 Winter Olympics', '==Criticism of host selection==']
    'American sportscaster [[Bob Costas]] criticized the [[International Olympic C...'
    ['Concerns and controversies at the 2022 Winter Olympics', '==Organizing concerns and controversies==', '===Cost and climate===']
    'Several cities withdrew their applications during [[Bids for the 2022 Winter ...'
    ['Concerns and controversies at the 2022 Winter Olympics', '==Organizing concerns and controversies==', '===Promotional song===']
    'Some commentators alleged that one of the early promotional songs for the [[2...'
    ['Concerns and controversies at the 2022 Winter Olympics', '== Diplomatic boycotts or non-attendance ==']
    
"""

"""
    Codigo Civil: Se divide en:
        - Mensaje
        
        - Título preliminar:
            - 53 artículos
            
        - Cuatro libros
            - Libro primero: 511 artículos
            - Libro segundo: 386 artículos
            - Libro tercero: 486 artículos
            - Libro cuarto: 1088 artículos 
            
        - Titulo final de un solo articulo

    E.j:s

        LIBRO TERCERO
        DE LA SUCESION POR CAUSA DE MUERTE, Y DE LAS DONACIONES
        ENTRE VIVOS
        
        Título I
        DEFINICIONES Y REGLAS GENERALES
        
        Art. 1.  ........
        
        Título II
        ...
        ...
        ...
        
        LIBRO CUARTO
        ...
        
        ......
        
        
"""

def get_articles():
    # Open the PDF file
    pdf_document = fitz.open("../../Documents/Chile/Código Civil.pdf")

    # Regex patterns to match libros, titulos y acrticulos   
    titulo_preliminar_pattern = r"TITULO PRELIMINAR"
    libro_pattern = r"LIBRO\s+[A-Z]+"
    titulo_pattern = r"Título\s+[IVXLCDM]+"
    articles_pattern = r"Art\. (\d+)[°o]?\.?([\s\S]*?)(?=Art\. \d+[°o]?\.?|$)"

    content_structure = {}
    current_libro = None
    current_titulo = None
    
    libros = ["TITULO PRELIMINAR", "LIBRO PRIMERO", "LIBRO SEGUNDO", "LIBRO TERCERO", "LIBRO CUARTO"]
    
    last_titulo = ""
    last_article = ""
    
    # Loop through each page of the PDF
    for page_num in range(len(pdf_document)-490):
        page = pdf_document[page_num]
        text = page.get_text("text")

        # Check for TITULO PRELIMINAR
        titulo_preliminar_match = re.search(titulo_preliminar_pattern, text)
        
        # Check for "LIBRO ..."
        libro_match = re.search(libro_pattern, text)
        
        # If the section is TITULO PRELIMINAR
        if titulo_preliminar_match:
            current_libro = titulo_preliminar_match.group(0).strip()
            if current_libro not in content_structure:
                content_structure[current_libro] = {}
                content_structure[current_libro]["articles"] = []
                content_structure[current_libro]["text"] = ""
                
        # If the section is LIBRO ...
        elif libro_match:
            current_libro = libro_match.group(0).strip()
            if current_libro not in content_structure:
                content_structure[current_libro] = {}

        if current_libro != "TITULO PRELIMINAR":
             # Check for "Título" subsection for LIBRO .. section
            matches = list(re.finditer(titulo_pattern, text))
            #print(text)
            print("\n\n")
            if len(matches) > 0:
                for i, titulo_match in enumerate(matches):
                    print(titulo_match)
                    # Get the start position of the match
                    match_start = titulo_match.start()
                    match_end = titulo_match.end()
                    
                    # Get the portion of the text before the match
                    text_before_match = text[:match_start]
                    
                    # Split the text before the match into lines
                    lines_before = text_before_match.splitlines()
                    current_titulo = titulo_match.group(0).strip()
                    # Check if the line before the match is empty
                    if lines_before and lines_before[-1].strip() == "":
                        # Proceed only if the line before is empty
                        print(current_titulo)
                        if current_libro and titulo_match.group(0) != "TITULO PRELIMINAR":
                            if current_titulo not in content_structure[current_libro]:
                                content_structure[current_libro][current_titulo] = {
                                    "articles": [],
                                    "text": ""
                                }
                            # Determine the relevant portion of text for articles
                            if i + 1 < len(matches):  # If there's a next match
                                next_start = matches[i + 1].start()
                                articles_text = text[match_end:next_start]
                                articles_text_before = text[:match_start]
                                if last_titulo != '':
                                    before_articles = re.findall(articles_pattern, articles_text_before)
                                    if before_articles:
                                        # Get the position of the first article match in the text
                                        first_article_start = articles_text_before.find(before_articles[0][0])
                                        # Extract any text before the first article
                                        pre_article_text = text[:first_article_start].strip()
                                        # Append pre-article text to the last article from the previous page
                                        if pre_article_text and len(content_structure[current_libro][last_titulo]["articles"]) > 0:
                                            content_structure[current_libro][last_titulo]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                                        
                                        # ----------------------------------------------------
                                        
                                        # Add articles of the current page
                                        for number, content in before_articles:
                                            if content.strip() == "Derogado":
                                                continue
                                            content_structure[current_libro][last_titulo]["articles"].append({
                                                "page": page_num + 1,
                                                "article_number": number,
                                                "article_text": content.strip().replace("\n", " ")
                                            })
                            else:  # For the last match, take until the end of the text
                                articles_text = text[match_end:]
                                articles_text_before = text[:match_start]
                                if last_titulo != '':
                                    before_articles = re.findall(articles_pattern, articles_text_before)
                                    if before_articles:
                                        # Get the position of the first article match in the text
                                        first_article_start = articles_text_before.find(before_articles[0][0])
                                        # Extract any text before the first article
                                        pre_article_text = text[:first_article_start].strip()
                                        # Append pre-article text to the last article from the previous page
                                        if pre_article_text and len(content_structure[current_libro][last_titulo]["articles"]) > 0:
                                            content_structure[current_libro][last_titulo]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                                        
                                        # ----------------------------------------------------
                                        
                                        # Add articles of the current page
                                        for number, content in before_articles:
                                            if content.strip() == "Derogado":
                                                continue
                                            content_structure[current_libro][last_titulo]["articles"].append({
                                                "page": page_num + 1,
                                                "article_number": number,
                                                "article_text": content.strip().replace("\n", " ")
                                            })
                            last_titulo = current_titulo
                            
                            # Extract articles from the relevant portion of text
                            articles = re.findall(articles_pattern, articles_text)
                    
                            if articles:
                                
                                # --- Handle case where there is an overflow of text from an article of the page before ---
                                
                                # Get the position of the first article match in the text
                                first_article_start = text.find(articles[0][0])
                                # Extract any text before the first article
                                pre_article_text = text[:first_article_start].strip()
                                # Append pre-article text to the last article from the previous page
                                if pre_article_text and len(content_structure[current_libro][current_titulo]["articles"]) > 0:
                                    content_structure[current_libro][current_titulo]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                                
                                # ----------------------------------------------------
                                
                                # Add articles of the current page
                                for number, content in articles:
                                    if content.strip() == "Derogado":
                                        continue
                                    content_structure[current_libro][current_titulo]["articles"].append({
                                        "page": page_num + 1,
                                        "article_number": number,
                                        "article_text": content.strip().replace("\n", " ")
                                    })

                                # If there is no text assigned to the Título subsection
                                if len(content_structure[current_libro][current_titulo]["text"]) == 0:
                                    # Append raw text under the current title
                                    titulo_end = titulo_match.start()+len(current_titulo)
                                    clean_text = ""
                                    if first_article_start < titulo_end:
                                        art_index = text[titulo_end:].find("Art.")
                                        #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                                        if art_index != -1:
                                            clean_text = text[titulo_end:][:art_index].strip()
                                        else:
                                            # If "Art." is not found, keep the original text
                                            clean_text = text[titulo_end:].strip()
                                    else:
                                        art_index = text[titulo_end:].find("Art.")
                                        #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                                        if art_index != -1:
                                            clean_text = text[titulo_end:][:art_index].strip()
                                        else:
                                            # If "Art." is not found, keep the original text
                                            clean_text = text[titulo_end:].strip()
                                            #print(f'{current_titulo}: {clean_text}')

                                    content_structure[current_libro][current_titulo]["text"] = clean_text
                    else:
                        # Proceed only if the line before is empty
                        current_titulo = last_titulo
                        if current_libro and titulo_match.group(0) != "TITULO PRELIMINAR":
                            if current_titulo not in content_structure[current_libro]:
                                content_structure[current_libro][current_titulo] = {
                                    "articles": [],
                                    "text": ""
                                }
                            
                            # Extract articles of the current page
                            articles = re.findall(articles_pattern, text)
                    
                            if articles:
                                
                                # --- Handle case where there is an overflow of text from an article of the page before ---
                                
                                # Get the position of the first article match in the text
                                first_article_start = text.find(articles[0][0])
                                # Extract any text before the first article
                                pre_article_text = text[:first_article_start].strip()
                                # Append pre-article text to the last article from the previous page
                                if pre_article_text and len(content_structure[current_libro][current_titulo]["articles"]) > 0:
                                    content_structure[current_libro][current_titulo]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                                
                                # ----------------------------------------------------
                                
                                # Add articles of the current page
                                for number, content in articles:
                                    if content.strip() == "Derogado":
                                        continue
                                    content_structure[current_libro][current_titulo]["articles"].append({
                                        "page": page_num + 1,
                                        "article_number": number,
                                        "article_text": content.strip().replace("\n", " ")
                                    })

                                # If there is no text assigned to the Título subsection
                                if len(content_structure[current_libro][current_titulo]["text"]) == 0:
                                    # Append raw text under the current title
                                    titulo_end = titulo_match.start()+len(current_titulo)
                                    clean_text = ""
                                    if first_article_start < titulo_end:
                                        art_index = text[titulo_end:].find("Art.")
                                        #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                                        if art_index != -1:
                                            clean_text = text[titulo_end:][:art_index].strip()
                                        else:
                                            # If "Art." is not found, keep the original text
                                            clean_text = text[titulo_end:].strip()
                                    else:
                                        art_index = text[titulo_end:].find("Art.")
                                        #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                                        if art_index != -1:
                                            clean_text = text[titulo_end:][:art_index].strip()
                                        else:
                                            # If "Art." is not found, keep the original text
                                            clean_text = text[titulo_end:].strip()
                                            #print(f'{current_titulo}: {clean_text}')

                                    content_structure[current_libro][current_titulo]["text"] = clean_text
                                content_structure[current_libro][current_titulo]["text"] = clean_text
            else:
                articles = re.findall(articles_pattern, text) 
                current_titulo = last_titulo
                if articles:
                    # --- Handle case where there is an overflow of text from an article of the page before ---
                    
                    # Get the position of the first article match in the text
                    first_article_start = text.find(articles[0][0])
                    # Extract any text before the first article
                    pre_article_text = text[:first_article_start].strip()
                    # Append pre-article text to the last article from the previous page
                    if pre_article_text and len(content_structure[current_libro][current_titulo]["articles"]) > 0:
                        content_structure[current_libro][current_titulo]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                    
                    # ----------------------------------------------------
                    
                    # Add articles of the current page
                    for number, content in articles:
                        if content.strip() == "Derogado":
                            continue
                        content_structure[current_libro][current_titulo]["articles"].append({
                            "page": page_num + 1,
                            "article_number": number,
                            "article_text": content.strip().replace("\n", " ")
                        })

                    # If there is no text assigned to the Título subsection
                    if len(content_structure[current_libro][current_titulo]["text"]) == 0:
                        # Append raw text under the current title
                        titulo_end = titulo_match.start()+len(current_titulo)
                        clean_text = ""
                        if first_article_start < titulo_end:
                            art_index = text[titulo_end:].find("Art.")
                            #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                            if art_index != -1:
                                clean_text = text[titulo_end:][:art_index].strip()
                            else:
                                # If "Art." is not found, keep the original text
                                clean_text = text[titulo_end:].strip()
                        else:
                            art_index = text[titulo_end:].find("Art.")
                            #print(f'Page Nº{page_num}: {current_libro}-{current_titulo}: {art_index}')
                            if art_index != -1:
                                clean_text = text[titulo_end:][:art_index].strip()
                            else:
                                # If "Art." is not found, keep the original text
                                clean_text = text[titulo_end:].strip()
                                #print(f'{current_titulo}: {clean_text}')

                        content_structure[current_libro][current_titulo]["text"] = clean_text
        # Handle case where section is "TITULO PRELIMINAR"
        else:
            if current_libro:
                articles = re.findall(articles_pattern, text)
                
                # Handle case where there is an overflow of the article of the previous page
                if articles:
                    # Get the position of the first article match in the text
                    first_article_start = text.find(articles[0][0])
                    
                    # Extract any text before the first article
                    pre_article_text = text[:first_article_start].strip()
                    # Append pre-article text to the last article from the previous page
                    if pre_article_text and len(content_structure[current_libro]["articles"]) > 0:
                        content_structure[current_libro]["articles"][-1]["article_text"] += " " + pre_article_text.replace("\n", " ")
                        
                for number, content in articles:
                    if content.strip() == "Derogado":
                        continue
                    content_structure[current_libro]["articles"].append({
                        "page": page_num + 1,
                        "article_number": number,
                        "article_text": content.strip().replace("\n", " ")
                    })

                # Append raw text under the current title
                content_structure[current_libro]["text"] += text
            
    return content_structure


def write_json(data_dict):
    with open("chile.json", "w", encoding="utf-8") as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, indent=4)
        
def divide_subsections(content_structure):
    write_json(content_structure)
    return []

def get_data():
    content_structure = get_articles()
    divided = divide_subsections(content_structure)

get_data()