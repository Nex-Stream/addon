# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per AnimeSaturn
# ----------------------------------------------------------

from core import support

host = support.config.get_channel_url()
__channel__ = 'animesaturn'
cookie = support.config.get_setting('cookie', __channel__)

# Aggiungi l'header User-Agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': cookie,
    'User-Agent': user_agent  # User-Agent personalizzato
}

def get_cookie(data):
    global cookie, headers
    cookie = support.match(data, patron=r'document.cookie="([^\s]+)').match
    support.config.set_setting('cookie', cookie, __channel__)
    headers = [['Cookie', cookie], ['User-Agent', user_agent]]  # Assicurati che l'User-Agent venga aggiornato anche qui

def get_data(item):
    data = support.match(item.url, headers=headers, follow_redirects=True).data
    if 'ASCookie' in data:
        get_cookie(data)
        data = get_data(item)
    return data

@support.menu
def mainlist(item):
    anime = ['/animelist?load_all=1&d=1',
             ('ITA',['', 'submenu', '/filter?language%5B0%5D=1']),
             ('SUB-ITA',['', 'submenu', '/filter?language%5B0%5D=0']),
             ('Più Votati',['/toplist','menu', 'top']),
             ('In Corso',['/animeincorso','peliculas','incorso']),
             ('Ultimi Episodi',['/fetch_pages.php?request=episodes&d=1','peliculas','updated'])]
    return locals()

def search(item, texto):
    support.info(texto)
    item.url = host + '/animelist?search=' + texto
    item.contentType = 'tvshow'
    try:
        return peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("%s" % line)
        return []

def newest(categoria):
    support.info()
    itemlist = []
    item = support.Item()
    try:
        if categoria == "anime":
            item.url = host + '/fetch_pages.php?request=episodes&d=1'
            item.args = "updated"
            return peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("{0}".format(line))
        return []

    return itemlist

# Le altre funzioni seguiranno lo stesso schema per utilizzare gli headers aggiornati...
# Assicurati che tutte le richieste HTTP utilizzino `headers=headers` per applicare l'User-Agent personalizzato

