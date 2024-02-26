import datetime
import json
from .extract_rss import consultas_feed
import telegram_notifications


def cargar_filtros():
    with open("Archivos Json/Filtros_Stocks.json", 'r', encoding="utf-8") as filtros_file:
        diccionario_filtros = json.load(filtros_file)
        return diccionario_filtros


def filtrar_contenido(nombre_fuente, contenido):
    """AQUI SE RETORNA UNA LISTA CON DICCIONARIOS QUE REPRESENTAN Y TIENE
    LOS DETALLES RELEVANTES DE UN ARTICULO DE LA FUENTE ESPECIFICADA"""
    # La variable lista_diccionario_entries es una lista de diccionarios en la
    # cual cada diccionario representa una noticia del día de hoy con las
    # llaves "titulo", "link" y "puntaje"
    lista_diccionarios_entries = list()
    filters_dict = cargar_filtros()
    symbols = filters_dict["symbols"]
    companies = filters_dict["names"]
    unwanted_words = []
    # -----------------------------------------------------------------------
    for entry in contenido.entries:
        """Loop por todos los articulos de la fuente"""
        try:
          titulo_noticia = entry.title
        except:
          titulo_noticia = ""
        contenido = ""
        link = ""
        try:
            link = entry.link
        except AttributeError as error:
            pass
        """AQUI EL PROBLEMA"""
        if "summary" in entry.keys():
            try:
                contenido = entry.summary
            except AttributeError as error:
                pass
        elif "value" in entry.keys():
            try:
                contenido = entry.value
            except AttributeError as error:
                pass
        """----------------------"""
        fecha_actual = datetime.datetime.now().ctime()
        # Se separa el string de la fecha en sus componentes para asi poder
        # obtener las noticias que han salido sólo el día de hoy
        lista_elementos_fecha_actual = fecha_actual.split(" ")
        """La llave 'published' no siempre existe en el diccionario entregado por
         el RSS feed por lo que se debe tomar en cuenta la llave 'updated'"""
        if "published" in entry.keys():
            pubdate = entry.published
            text = titulo_noticia + " " + contenido
            words = text.split(" ")
            for word in words:
                if word.lower() in companies or word in symbols and word not in unwanted_words:
                    lista_diccionarios_entries.append({"titulo":titulo_noticia,
                                                "link":link,
                                                       "summary": contenido,
                                                       "pubDate": pubdate,
                                                       "fuente": nombre_fuente,
                                                       "company": word})
                    continue
        elif "pubDate" in entry.keys():
            pubdate = entry.pubDate
            text = titulo_noticia + " " + contenido
            words = text.split(" ")
            for word in words:
                if word.lower() in companies or word in symbols and word not in unwanted_words:
                    lista_diccionarios_entries.append({"titulo":titulo_noticia,
                                                "link":link,
                                                       "summary": contenido,
                                                       "pubDate": pubdate,
                                                       "fuente": nombre_fuente,
                                                       "company": word})
                    continue           
    return lista_diccionarios_entries

def transformar():
    diccionario_noticias_fuentes = consultas_feed()
    for tupla in diccionario_noticias_fuentes.values():
        lista_entries = filtrar_contenido(tupla[0], tupla[1])
        diccionario_noticias_fuentes[tupla[0]] = lista_entries
    return diccionario_noticias_fuentes