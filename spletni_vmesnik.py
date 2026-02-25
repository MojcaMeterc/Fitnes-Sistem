import sqlite3
import random
import json
import bottle
from model import Uporabnik, Trener, Karta

NASTAVITVE = 'nastavitve.json'

# PIŠKOTKI

try:
    with open(NASTAVITVE) as f:
        nastavitve = json.load(f)
        SKRIVNOST = nastavitve['skrivnost'] 
except FileNotFoundError:
    SKRIVNOST = "".join(chr(random.randrange(32, 128)) for _ in range(32))
    with open(NASTAVITVE, "w") as f:
        json.dump({'skrivnost': SKRIVNOST}, f)

# povezava z bazo
conn = sqlite3.connect("fitnes.db")
conn.row_factory = sqlite3.Row  #(da lahko dostopamo do imenov stolpcev)

bottle.TEMPLATE_PATH.insert(0, './view')

@bottle.get('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')

@bottle.get('/')
def zacetna_stran():
    ime =bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
    if not ime:
        ime = None #tako da vemo da ni nobem prijalvjen
    return bottle.template('spletna_stran.html',ime=ime, random=random.randint(1, 10000))

#-------
# LOGIN/LOGOUT
#-------
def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie('uporabnik', uporabnik.ime, path='/', secret=SKRIVNOST)
    bottle.response.set_cookie('uid', str(uporabnik.uporabnik_id), path='/', secret=SKRIVNOST)
    bottle.redirect('/moj_racun/')

def zahtevaj_prijavo():
    uid = bottle.request.get_cookie('uid', secret=SKRIVNOST)
    if not uid:
        bottle.redirect('/prijava/')
    return int(uid)

@bottle.get('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnik', path="/")
    bottle.response.delete_cookie('uid', path='/')
    bottle.redirect('/')


#---------
# REGISTRACIJA
#------------
@bottle.get('/prijava/')
def prijava():
    ime =bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
    if not ime:
        ime = None #tako da vemo da ni nobem prijalvjen
    return bottle.template('prijava.html',ime=ime, napaka=None, random=random.randint(1, 10000))

@bottle.post('/prijava/')
def prijava_post():
    email = bottle.request.forms.get('email')
    geslo = bottle.request.forms.get('geslo')

    uporabnik = Uporabnik.prijava(conn, email, geslo)
    if uporabnik:
        prijavi_uporabnika(uporabnik)
    else:
        ime = bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
        if not ime:
            ime = None
        return bottle.template('prijava.html', ime=ime, napaka = 'Napčen mail ali geslo', random=random.randint(1, 10000))
    
@bottle.get('/registracija/')
def registracija():
    ime =bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
    if not ime:
        ime = None #tako da vemo da ni nobem prijalvjen
    return bottle.template('registracija.html',ime=ime, napaka=None, random=random.randint(1, 10000))

@bottle.post('/registracija/')
def registracija_post():
    
    ime = bottle.request.forms.get('ime')
    priimek = bottle.request.forms.get('priimek')
    email = bottle.request.forms.get('email')
    telefon = bottle.request.forms.get('telefon')
    geslo = bottle.request.forms.get('geslo')

    try:
        uporabnik = Uporabnik(conn, ime, priimek, email, telefon)
        uporabnik.ustvari_racun(geslo)
        prijavi_uporabnika(uporabnik)

    except sqlite3.IntegrityError:
        ime = bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
        if not ime:
            ime = None
        return bottle.template('registracija.html', ime=ime, napaka = 'Email ali telefonska številka že obstaja', random=random.randint(1, 10000))
      
@bottle.get('/moj_racun/')
def moj_racun():
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    if not uporabnik:
        bottle.redirect('/')

    ime = f"{uporabnik.ime} {uporabnik.priimek}"

    return bottle.template('uporabnik_zacetna.html', ime=ime, priimek=uporabnik, email=uporabnik, telefon=uporabnik, random=random.randint(1, 10000))

# ZAGON APLIKACIJE
bottle.run(host='localhost', port=8080, debug=True)
    
    



