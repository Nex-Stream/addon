import json, os, sys
import socket
import re

path = os.getcwd()
sys.path.insert(0, path)

if sys.version_info[0] >= 3:
    from lib.httplib2 import py3 as httplib2
else:
    from lib.httplib2 import py2 as httplib2

def http_Resp(lst_urls):
    rslt = {}
    for sito in lst_urls:
        try:
            s = httplib2.Http()
            code, resp = s.request(sito, body=None)
            if code.previous:
                rslt['code'] = code.previous['status']
                rslt['redirect'] = code.get('content-location', sito)
                rslt['status'] = code.status
                print("r1 http_Resp: %s %s %s %s" %
                      (code.status, code.reason, rslt['code'], rslt['redirect']))
            else:
                rslt['code'] = code.status
        except httplib2.ServerNotFoundError:
            rslt['code'] = -2  # Sito inesistente o problema di rete
        except socket.error:
            rslt['code'] = 111  # Sito non raggiungibile (Connessione rifiutata)
        except Exception as e:
            print(f"Errore generico in http_Resp: {e}")
            rslt['code'] = 'Connection error'
    return rslt

if __name__ == '__main__':
    fileJson = 'channels.json'

    with open(fileJson) as f:
        data = json.load(f)

    chList = os.listdir('channels')

    for k in data.keys():
        for chann, host in sorted(data[k].items()):
            if chann + '.json' not in chList:
                print(f"{chann} non esiste più")
                del data[k][chann]
                continue

            if k == 'findhost':
                continue

            print(f"check #### INIZIO #### channel - host : {chann} - {host}")

            rslt = http_Resp([host])

            if rslt['code'] == 200:  
                data[k][chann] = host
            elif str(rslt['code']).startswith('3'):  
                data[k][chann] = rslt.get('redirect', host)
            elif rslt['code'] in [429, 503, 403]:  
                from lib import proxytranslate

                print('Cloudflare riconosciuto')
                try:
                    response = proxytranslate.process_request_proxy(host)
                    
                    if response:
                        print(f"DEBUG: Risposta proxytranslate: {response}")  
                        page_data = response.get('data', '')
                        match = re.search(r'<base href="([^"]+)', page_data)
                        if match:
                            data[k][chann] = match.group(1)
                            rslt['code_new'] = 200
                        else:
                            print(f"Errore: Nessun base href trovato per {host}")
                    else:
                        print(f"Errore: proxytranslate ha restituito None per {host}")

                except Exception as e:
                    print(f"Errore in proxytranslate: {e}")
                    import traceback
                    traceback.print_exc()
            elif rslt['code'] == -2:
                print(f"Host sconosciuto: {host}")
            elif rslt['code'] == 111:
                print(f"Host non raggiungibile: {host}")
            else:
                print(f"Errore sconosciuto {rslt['code']} per {host}")

            print(f"check #### FINE #### rslt : {rslt}")

            if data[k][chann].endswith('/'):
                data[k][chann] = data[k][chann][:-1]

    with open(fileJson, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
