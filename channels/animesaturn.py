# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per AnimeSaturn
# ----------------------------------------------------------

from core import support

host = support.config.get_channel_url()
__channel__ = 'animesaturn'
cookie = support.config.get_setting('cookie', __channel__)

# Aggiungi User-Agent come parte del dizionario headers
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
    # Aggiorna gli headers con il nuovo cookie e User-Agent
    headers['Cookie'] = cookie
    headers['User-Agent'] = user_agent  # Assicurati di aggiornare l'User-Agent

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

# Assicurati che tutte le richieste HTTP usino gli headers corretti
@support.scrape
def peliculas(item):
    anime = True

    deflang = 'Sub-ITA'
    action = 'check'
    page = None
    post = "page=" + str(item.page if item.page else 1) if item.page and int(item.page) > 1 else None
    data = get_data(item)  # Assicurati che venga usato il cookie e User-Agent

    # debug = True

    if item.args == 'top':
        data = item.other
        patron = r'light">(?P<title2>[^<]+)</div>\s*(?P<title>[^<]+)[^>]+>[^>]+>\s*<a href="(?P<url>[^"]+)">(?:<a[^>]+>|\s*)<img.*?src="(?P<thumb>[^"]+)"'
    else:
        data = support.match(item, post=post, headers=headers).data  # Usa gli headers corretti per la richiesta
        if item.args == 'updated':
            page = support.match(data, patron=r'data-page="(\d+)" title="Next">').match
            patron = r'<a href="(?P<url>[^"]+)" title="(?P<title>[^"(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-Za-z-]+)\))?">\s*<img src="(?P<thumb>[^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s\s*(?P<type>[^\s]+)\s*(?P<episode>\d+)'
            typeContentDict = {'Movie':'movie', 'Episodio':'episode'} #item.contentType='episode'
            action = 'findvideos'
            def itemlistHook(itemlist):
                if page:
                    itemlist.append(item.clone(title=support.typo(support.config.get_localized_string(30992), 'color kod bold'), page=page, thumbnail=support.thumb()))
                return itemlist
        elif 'filter' in item.args:
            page = support.match(data, patron=r'totalPages:\s*(\d+)').match
            patron = r'<a href="(?P<url>[^"]+)" title="(?P<title>[^"(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-Za-z-]+)\))?">\s*<img src="(?P<thumb>[^"]+)"'
            def itemlistHook(itemlist):
                if item.nextpage: item.nextpage += 1
                else: item.nextpage = 2
                if page and item.nextpage < int(page):
                    itemlist.append(item.clone(title=support.typo(support.config.get_localized_string(30992), 'color kod bold'), url='{}&page={}'.format(item.url, item.nextpage), infoLabels={}, thumbnail=support.thumb()))
                return itemlist
        else:
            # pagination = ''
            if item.args == 'incorso':
                patron = r'<a href="(?P<url>[^"]+)"[^>]+>(?P<title>[^<(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-za-z-]+)\))?</a>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*<img width="[^"]+" height="[^"]+" src="(?P<thumb>[^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>(?P<plot>[^<]+)<'
            else:
                patron = r'<img src="(?P<thumb>[^"]+)" alt="(?P<title>[^"\(]+)(?:\((?P<lang>[Ii][Tt][Aa])\))?(?:\s*\((?P<year>\d+)\))?[^"]*"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*<a class="[^"]+" href="(?P<url>[^"]+)">[^>]+>[^>]+>[^>]+>\s*<p[^>]+>(?:(?P<plot>[^<]+))?<'

    return locals()
