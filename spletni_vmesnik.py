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

@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna_stran.html')

#-------
# LOGIN/LOGOUT
#-------
def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie('uporabnik', uporabnik.ime, path='/', secret=SKRIVNOST)
    bottle.response.set_cookie('uid', str(uporabnik.uporabnik_id), path='/', secret=SKRIVNOST)
    bottle.redirect('/')

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

#------
#STATIC
#------

@bottle.get('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')

#---------
# REGISTRACIJA
#------------
@bottle.get('/prijava/')
def prijava():
    return bottle.template('prijava.html', napaka=None, email="")

@bottle.post('/prijava/')
def prijava_post():
    email = bottle.request.form.getunicode('email')
    geslo = bottle.request.form.getunicode('geslo')
    uporabnik = Uporabnik.prijava(conn, email, geslo)
    if uporabnik:
        prijavi_uporabnika(uporabnik)
    else:
        return bottle.template('prijava.html', napaka = 'Napčen mail ali geslo')
    
@bottle.get('/registracija/')
def registracija():
    return bottle.template('registracija.html', napaka = None)

@bottle.post('/registracija/')
def registracija_post():
    ime = bottle.request.form.getunicode('ime')
    priimek = bottle.request.form.getunicode('priimek')
    email = bottle.request.form.getunicode('email')
    telefon = bottle.request.form.getunicode('telefon')
    geslo = bottle.request.form.getunicode('geslo')
    try:
        uporabnik = Uporabnik(conn, ime, priimek, email, telefon)
        uporabnik.ustvari_racun(geslo)
        prijavi_uporabnika(uporabnik)
    except sqlite3.IntegrityError:
        return bottle.template('registracija.html', napaka = 'Email ali telefonska številka že obstaja')
    
    



