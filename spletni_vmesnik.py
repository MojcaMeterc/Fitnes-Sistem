import json
import random
import sqlite3
import sys

import bottle
from model import Admin, Dvorana, Karta, Termin, Trener, Uporabnik

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
NASTAVITVE = "nastavitve.json"

# PIŠKOTKI

try:
    with open(NASTAVITVE) as f:
        nastavitve = json.load(f)
        SKRIVNOST = nastavitve["skrivnost"]
except FileNotFoundError:
    SKRIVNOST = "".join(chr(random.randrange(32, 128)) for _ in range(32))
    with open(NASTAVITVE, "w") as f:
        json.dump({"skrivnost": SKRIVNOST}, f)

# povezava z bazo
conn = sqlite3.connect("fitnes.db", check_same_thread=False)
conn.row_factory = sqlite3.Row  # (da lahko dostopamo do imenov stolpcev)

bottle.TEMPLATE_PATH.insert(0, "./view")


@bottle.get("/static/<filename:path>")
def static(filename):
    return bottle.static_file(filename, root="static")


# -------------------
#  POMOŽNE FUNKCIJE
# -------------------


def get_nav():
    admin_ime = bottle.request.get_cookie("admin_ime", secret=SKRIVNOST)
    if admin_ime:
        return admin_ime, False, True
    trener_ime = bottle.request.get_cookie("trener_ime", secret=SKRIVNOST)
    if trener_ime:
        return trener_ime, True, False
    ime = bottle.request.get_cookie("uporabnik", secret=SKRIVNOST)
    return ime, False, False


def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie("uporabnik", uporabnik.ime, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie(
        "uid", str(uporabnik.uporabnik_id), path="/", secret=SKRIVNOST
    )
    bottle.redirect("/moj_racun/")


def prijavi_trenerja(trener):
    bottle.response.set_cookie("trener_ime", trener.ime, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("tid", str(trener.trener_id), path="/", secret=SKRIVNOST)
    bottle.redirect("/trener/")


def zahtevaj_prijavo():
    uid = bottle.request.get_cookie("uid", secret=SKRIVNOST)
    print("COOKIE UID", repr(uid))
    if not uid:
        bottle.redirect("/prijava/")
    return int(uid)


def zahtevaj_trenerja():
    tid = bottle.request.get_cookie("tid", secret=SKRIVNOST)
    if not tid:
        bottle.redirect("/prijava/")
    return int(tid)


# -------------------
#  JAVNA STRAN
# -------------------


@bottle.get("/")
def zacetna_stran():
    ime, je_trener, je_admin = get_nav()
    return bottle.template(
        "spletna_stran.html",
        ime=ime,
        je_trener=je_trener,
        je_admin=je_admin,
        random=random.randint(1, 1000),
    )


@bottle.get("/ponudba/")
def ponudba():
    ime, je_trener, je_admin = get_nav()
    uid = bottle.request.get_cookie("uid", secret=SKRIVNOST)
    iztek_po_karti = {}

    if uid:
        uporabnik = Uporabnik.pridobi_po_id(conn, int(uid))
        for karta in uporabnik.aktivne_karte():
            iztek_po_karti[karta[0]] = karta[4]

    return bottle.template(
        "ponudba.html",
        ime=ime,
        je_trener=je_trener,
        je_admin=je_admin,
        uid=uid,
        iztek_po_karti=iztek_po_karti,
        random=random.randint(1, 1000),
    )


# ----------
# ODJAVA
# ----------


@bottle.get("/odjava/")
def odjava():
    bottle.response.delete_cookie("uporabnik", path="/", secret=SKRIVNOST)
    bottle.response.delete_cookie("uid", path="/", secret=SKRIVNOST)
    bottle.response.delete_cookie("trener_ime", path="/", secret=SKRIVNOST)
    bottle.response.delete_cookie("tid", path="/", secret=SKRIVNOST)
    bottle.response.delete_cookie("admin_ime", path="/", secret=SKRIVNOST)
    bottle.response.delete_cookie("aid", path="/", secret=SKRIVNOST)
    bottle.redirect("/")


# --------------
# ADMIN
# --------------
def prijava_admin(admin):
    bottle.response.set_cookie("admin_ime", admin.ime, path="/", secret=SKRIVNOST)
    bottle.response.set_cookie("aid", str(admin.admin_id), path="/", secret=SKRIVNOST)
    bottle.redirect("/admin/")


def zahtevaj_admin():
    aid = bottle.request.get_cookie("aid", secret=SKRIVNOST)
    if not aid:
        bottle.redirect("/prijava/")
    return int(aid)


@bottle.get("/admin/")
def admin_zacetna():
    aid = zahtevaj_admin()
    admin = Admin.pridobi_po_id(conn, aid)
    if not admin:
        bottle.redirect("/prijava/")
    return bottle.template(
        "admin_zacetna.html",
        ime=admin.ime,
        email=admin.email,
        je_trener=False,
        je_admin=True,
        random=random.randint(1, 10000),
    )


@bottle.get("/admin/trenerji/")
def admin_trenerji():
    aid = zahtevaj_admin()
    print("AID:", aid)
    admin = Admin.pridobi_po_id(conn, aid)
    print(admin)
    print(type(admin))
    trenerji = admin.vsi_trenerji()
    return bottle.template(
        "admin_trenerji.html",
        ime=admin.ime,
        trenerji=trenerji,
        je_trener=False,
        je_admin=True,
        random=random.randint(1, 10000),
    )


@bottle.post("/admin/dodaj_trenerja/")
def admin_dodaj_trenerja():
    aid = zahtevaj_admin()
    admin = Admin.pridobi_po_id(conn, aid)

    ime = bottle.request.forms.getunicode("ime")
    priimek = bottle.request.forms.getunicode("priimek")
    email = bottle.request.forms.get("email")
    specializacija = bottle.request.forms.get("specializacija")
    geslo = bottle.request.forms.get("geslo")

    try:
        admin.dodaj_trenerja(ime, priimek, email, specializacija, geslo)
    except sqlite3.IntegrityError:
        # email že obstaja
        trenerji = admin.vsi_trenerji()
        return bottle.template(
            "admin_trenerji.html",
            ime=admin.ime,
            trenerji=trenerji,
            napaka="Trener s tem emailom že obstaja",
            je_trener=False,
            je_admin=True,
            random=random.randint(1, 10000),
        )
    bottle.redirect("/admin/trenerji/")


@bottle.post("/admin/izbrisi_trenerja/")
def admin_izbirs_trenerja():
    aid = zahtevaj_admin()
    admin = Admin.pridobi_po_id(conn, aid)
    trener_id = bottle.request.forms.get("trener_id")
    admin.izbrisi_trenerja(trener_id)
    bottle.redirect("/admin/trenerji/")


# ----------------------------------
# PRIJAVA / REGISTRACIJA
# ----------------------------------


@bottle.get("/prijava/")
def prijava():
    ime, je_trener, je_admin = get_nav()
    return bottle.template(
        "prijava.html",
        ime=ime,
        je_trener=je_trener,
        je_admin=je_admin,
        napaka=None,
        random=random.randint(1, 10000),
    )


@bottle.post("/prijava/")
def prijava_post():
    email = bottle.request.forms.get("email")
    geslo = bottle.request.forms.get("geslo")

    if admin := Admin.prijava(conn, email, geslo):
        prijava_admin(admin)
        return

    if trener := Trener.prijava(conn, email, geslo):
        prijavi_trenerja(trener)
        return

    if uporabnik := Uporabnik.prijava(conn, email, geslo):
        prijavi_uporabnika(uporabnik)
        return

    ime, je_trener, je_admin = get_nav()
    return bottle.template(
        "prijava.html",
        ime=ime,
        je_trener=je_trener,
        je_admin=je_admin,
        napaka="Napačen mail ali geslo",
        random=random.randint(1, 10000),
    )


@bottle.get("/registracija/")
def registracija():
    ime, je_trener, je_admin = get_nav()
    return bottle.template(
        "registracija.html",
        ime=ime,
        je_admin=je_admin,
        je_trener=je_trener,
        napaka=None,
        random=random.randint(1, 10000),
    )


@bottle.post("/registracija/")
def registracija_post():
    ime = bottle.request.forms.get("ime")
    priimek = bottle.request.forms.get("priimek")
    email = bottle.request.forms.get("email")
    telefon = bottle.request.forms.get("telefon")
    geslo = bottle.request.forms.get("geslo")

    try:
        uporabnik = Uporabnik(conn, ime, priimek, email, telefon)
        uporabnik.ustvari_racun(geslo)
        prijavi_uporabnika(uporabnik)

    except sqlite3.IntegrityError:
        ime, je_trener, je_admin = get_nav()
        return bottle.template(
            "registracija.html",
            ime=ime,
            je_admin=je_admin,
            je_trener=je_trener,
            napaka="Email ali telefonska številka že obstaja",
            random=random.randint(1, 10000),
        )


# ----------------
# TRENER
# ----------------
@bottle.get("/trener/")
def trener_zacetna():
    tid = zahtevaj_trenerja()
    trener = Trener.pridobi_po_id(conn, tid)
    if not trener:
        bottle.redirect("/prijava/")
    termini = list(trener.moji_termini())
    return bottle.template(
        "trener_zacetna.html",
        ime=trener.ime,
        priimek=trener.priimek,
        email=trener.email,
        specializacija=trener.special,
        je_trener=True,
        je_admin=False,
        termini=termini,
        random=random.randint(1, 10000),
    )


@bottle.get("/trener/termini/")
def trener_termini():
    tid = zahtevaj_trenerja()
    trener_ime = bottle.request.get_cookie("trener_ime", secret=SKRIVNOST)
    trener = Trener.pridobi_po_id(conn, tid)
    termini = trener.moji_termini()
    return bottle.template(
        "trener_termini.html",
        ime=trener_ime,
        je_trener=True,
        je_admin=False,
        termini=termini,
        random=random.randint(1, 10000),
    )


@bottle.get("/trener/prosti_termini/")
def trener_prosti_termini():
    tid = zahtevaj_trenerja()
    trener_ime = bottle.request.get_cookie("trener_ime", secret=SKRIVNOST)
    dvorana_filter = bottle.request.query.get("dvorana_id")
    if dvorana_filter:
        dvorana_filter = int(dvorana_filter)
    termini = Termin.termini_brez_trenerja(conn, dvorana_filter)
    dvorane = Dvorana.vse_dvorane(conn)
    return bottle.template(
        "trener_prosti_termini.html",
        ime=trener_ime,
        je_trener=True,
        je_admin=False,
        termini=termini,
        dvorana_filter=dvorana_filter,
        dvorane=dvorane,
        random=random.randint(1, 10000),
    )


@bottle.post("/trener/izberi_termin/")
def trener_izberi_termin():
    tid = zahtevaj_trenerja()
    termin_id = bottle.request.forms.get("termin_id")
    trener = Trener.pridobi_po_id(conn, tid)
    trener.izberi_termin(termin_id)
    bottle.redirect("/trener/")


# ------------
# UPORABNIK
# ------------


@bottle.get("/moj_racun/")
def moj_racun():
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    if not uporabnik:
        bottle.redirect("/")
    karte = list(uporabnik.aktivne_karte())
    rezervacije = list(uporabnik.moje_rezervacije())
    return bottle.template(
        "uporabnik_zacetna.html",
        ime=uporabnik.ime,
        priimek=uporabnik.priimek,
        email=uporabnik.email,
        telefon=uporabnik.telefon,
        karte=karte,
        rezervacije=rezervacije,
        je_trener=False,
        je_admin=False,
        random=random.randint(1, 10000),
    )


@bottle.get("/moje_karte/")
def moje_karte():
    uid = zahtevaj_prijavo()
    ime = bottle.request.get_cookie("uporabnik", secret=SKRIVNOST)

    karte = []  # ZAČASNO DOKLER NE POVEŽEVA Z BAZO

    return bottle.template(
        "moje_karte.html",
        ime=ime,
        karte=karte,
        je_admin=False,
        je_trener=False,
        random=random.randint(1, 10000),
    )


@bottle.get("/prosti_termini/")
def prosti_termini():
    uid = zahtevaj_prijavo()
    ime = bottle.request.get_cookie("uporabnik", secret=SKRIVNOST)

    termini = Termin.prosti_term_trener(conn, uid)

    return bottle.template(
        "prosti_termini.html",
        ime=ime,
        je_trener=False,
        je_admin=False,
        termini=termini,
        random=random.randint(1, 1000),
    )


@bottle.post("/rezerviraj/")
def rezerviraj():
    uid = zahtevaj_prijavo()
    termin_id = bottle.request.forms.get("termin_id")
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)

    try:
        uporabnik.izberi_termin(termin_id)

    except Exception as e:
        return str(e)

    bottle.redirect("/moj_racun/")


@bottle.get("/moje_rezervacije/")
def moje_rezervacije():
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    rezervacije = uporabnik.moje_rezervacije()
    ime = uporabnik.ime

    return bottle.template(
        "moje_rezervacije.html",
        ime=ime,
        rezervacije=rezervacije,
        je_trener=False,
        je_admin=False,
        random=random.randint(1, 10000),
    )


# -------
# KARTE
# ------


@bottle.get("/kupi/<karta_id>/")
def kupi(karta_id):
    """Omogoča nakup karte"""
    uid = zahtevaj_prijavo()
    uporabnik = Uporabnik.pridobi_po_id(conn, uid)
    uporabnik.kupi_karto(karta_id)
    bottle.redirect("/moj_racun/")


# ZAGON APLIKACIJE
sys.stdout.reconfigure(encoding="utf-8")
bottle.run(host="localhost", port=8080, debug=True)
