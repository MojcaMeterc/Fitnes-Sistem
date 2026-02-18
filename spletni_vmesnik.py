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

# za login
def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie('uporabnik', uporabnik.ime, path='/', secret=SKRIVNOST)
    bottle.response.set_cookie('uid', str(uporabnik.uporabnik_id), path='/', secret=SKRIVNOST)
    bottle.redirect('/')

def zahtevaj_prijavo():
    uid = bottle.request.get_cookie('uid', secret=SKRIVNOST)
    if not uid:
        bottle.redirect('/prijava/')
    return int(uid)

@bottle.get('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')

# prijava
@bottle.get('/prijava/')
def prijava():
    return bottle.template('prijava.html', napaka=None, email="")

