import sqlite3
import random
import json
import bottle
from model import Uporabnik, Trener, Karta, Termin

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

#-------------------
#  POMOŽNE FUNKCIJE
#-------------------

def get_nav():
    trener_ime = bottle.request.get_cookie('trener_ime', secret = SKRIVNOST)
    if trener_ime:
        return trener_ime, True
    ime = bottle.request.get_cookie('uporabnik', secret = SKRIVNOST)
    return ime, False

def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie('uporabnik', uporabnik.ime, path='/', secret=SKRIVNOST)
    bottle.response.set_cookie('uid', str(uporabnik.uporabnik_id), path='/', secret=SKRIVNOST)
    bottle.redirect('/moj_racun/')


def prijavi_trenerja(trener):
    bottle.response.set_cookie('trener_ime', trener.ime, path='/', secret = SKRIVNOST)
    bottle.response.set_cookie('tid', str(trener.trener_id), path = '/', secret = SKRIVNOST)
    bottle.redirect('/trener/')

def zahtevaj_prijavo():
    uid = bottle.request.get_cookie('uid', secret = SKRIVNOST)
    print("COOKIE UID", repr(uid))
    if not uid:
        bottle.redirect('/prijava/')
    return int(uid)

def zahtevaj_trenerja():
    tid = bottle.request.get_cookie('tid', secret = SKRIVNOST)
    if not tid:
        bottle.redirect('/prijava/')
    return int(tid)

#-------------------
#  JAVNA STRAN
#-------------------

@bottle.get('/')
def zacetna_stran():
    ime, je_trener = get_nav()
    return bottle.template('spletna_stran.html', ime = ime, je_trener = je_trener,
                           random = random.randint(1, 1000))

@bottle.get('/ponudba/')
def ponudba():
    ime, je_trener = get_nav()
    return bottle.template('ponudba.html', ime = ime, je_trener = je_trener,
                           random = random.randint(1, 1000))

#----------
# ODJAVA
#----------

@bottle.get('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnik', path="/")
    bottle.response.delete_cookie('uid', path='/')
    bottle.response.delete_cookie('trener_ime', path="/")
    bottle.response.delete_cookie('tid', path='/')
    bottle.redirect('/')


#----------------------------------
# PRIJAVA / REGISTRACIJA 
#----------------------------------

@bottle.get('/prijava/')
def prijava():
    ime, je_trener =get_nav()
    return bottle.template('prijava.html', ime=ime, je_trener=je_trener, napaka=None, random=random.randint(1, 10000))

@bottle.post('/prijava/')
def prijava_post():
    email = bottle.request.forms.get('email')
    geslo = bottle.request.forms.get('geslo')
    uporabnik = Uporabnik.prijava(conn, email, geslo)

    if uporabnik:
        prijavi_uporabnika(uporabnik)
    else:
        ime, je_trener = get_nav()
        return bottle.template('prijava.html', ime=ime, je_trener=je_trener, napaka = 'Napčen mail ali geslo', random=random.randint(1, 10000))

@bottle.get('/prijava_trener/')
def prijava_trener():
    bottle.redirect('/prijava/')

@bottle.post('/prijava_trener/')
def prijava_trener_post():
    email = bottle.request.forms.get('email')
    geslo = bottle.request.forms.get('geslo')
    trener = Trener.prijava(conn, email, geslo)
    if trener:
        prijavi_trenerja(trener)
    else:
        ime, je_trener = get_nav()
        return bottle.template('prijava.html', ime = ime, je_trener = je_trener,
                               napaka = 'Napačen e-mail ali geslo',
                               random = random.randint(1, 1000))
    
@bottle.get('/registracija/')
def registracija():
    ime, je_trener =get_nav()
    return bottle.template('registracija.html', ime=ime, je_trener=je_trener, napaka=None, random=random.randint(1, 10000))

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
        ime, je_trener = get_nav()
        return bottle.template('registracija.html', ime=ime, je_trener=je_trener, napaka = 'Email ali telefonska številka že obstaja', random=random.randint(1, 10000))

#----------------
# TRENER 
#----------------
@bottle.get('/trener/')
def trener_zacetna():
    tid = zahtevaj_trenerja()
    trener = Trener.pridobi_po_id(conn, tid)
    if not trener:
        bottle.redirect('/prijava/')
    return bottle.template('trener_zacetna.html', 
                           ime=trener.ime, 
                           priimek=trener.priimek,
                           email = trener.email,
                           specializacija = trener.special,
                           je_trener = True,
                           random = random.randint(1, 10000))

@bottle.get('/trener/termini/')
def trener_termini():
    tid = zahtevaj_trenerja()
    trener_ime = bottle.request.get_cookie('trener_ime', secret = SKRIVNOST)
    trener = Trener.pridobi_po_id(conn, tid)
    termini = trener.moji_termini()
    return bottle.template('trener_termini.html', ime=trener_ime, je_trener = True,
                            termini=termini, random=random.randint(1, 10000))

@bottle.get('/trener/prosti_termini/')
def trener_prosti_termini():
    tid = zahtevaj_trenerja()
    trener_ime = bottle.request.get_cookie('trener_ime', secret = SKRIVNOST)
    termini = Termin.termini_brez_trenerja(conn)
    return bottle.template('trener_prosti_termini.html', ime=trener_ime, je_trener=True,
                           termini=termini, random=random.randint(1, 10000))

@bottle.post('/trener/izberi_termin/')
def trener_izberi_termin():
    tid = zahtevaj_trenerja()
    termin_id = bottle.request.forms.get('termin_id')
    trener = Trener.pridobi_po_id(conn, tid)
    trener.izberi_termin(termin_id)
    bottle.redirect('/trener/termini/')

#------------
# UPROABNIK 
#------------

@bottle.get('/moj_racun/')
def moj_racun():
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    if not uporabnik:
        bottle.redirect('/')
    return bottle.template('uporabnik_zacetna.html',
                           ime=uporabnik.ime,
                           priimek=uporabnik.priimek,
                           email=uporabnik.email,
                           telefon=uporabnik.telefon,
                           je_trener = False,
                           random=random.randint(1,10000) )


@bottle.get('/moje_karte/')
def moje_karte():
    uid = zahtevaj_prijavo()
    ime = bottle.request.get_cookie('uporabnik', secret=SKRIVNOST)

    karte = [] # ZAČASNO DOKLER NE POVEŽEVA Z BAZO

    return bottle.template('moje_karte.html', ime=ime, karte=karte, je_trener=False, random=random.randint(1, 10000))

@bottle.get('/prosti_termini/')
def prosti_termini():
    uid = zahtevaj_prijavo()
    ime = bottle.request.get_cookie('uporabnik', secret=SKRIVNOST)

    termini = Termin.prosti_term_trener(conn, uid) 

    return bottle.template('prosti_termini.html', ime=ime, je_trener = False, 
                           termini=termini,random=random.randint(1,1000))

@bottle.post('/rezerviraj/')
def rezerviraj():
    uid = zahtevaj_prijavo()
    termin_id = bottle.request.forms.get('termin_id')
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)

    try:
        uporabnik.izberi_termin(termin_id)

    except Exception as e:
        return str(e)
    
    bottle.redirect('/moje_rezervacije/')

@bottle.get('/moje_rezervacije/')
def moje_rezervacije():
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    rezervacije = uporabnik.moje_rezervacije()
    ime = uporabnik.ime

    return bottle.template('moje_rezervacije.html', ime=ime, rezervacije=rezervacije, 
                           je_trener=False, random=random.randint(1, 10000))

    
# ZAGON APLIKACIJE
bottle.run(host='localhost', port=8080, debug=True)
    





