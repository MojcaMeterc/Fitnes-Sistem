import sqlite3
from model import Uporabnik, Trener, Termin, Karta 

def prikazi_proste_termine(conn):
    print("Prosti termni:")
    for t in Termin.prosti_termini(conn):
        print(f"{t[0]}: dvorana {t[1]}, {t[2]} {t[3]} - {t[4]}")

def rezerviraj_termin_U(conn, uporabnik):
    prikazi_proste_termine(conn)
    termin_id = input("Vnesi ID termina, ki ga želiš rezervirati: ")
    try:
        uporabnik.izberi_termin(int(termin_id))
        print("Termin rezerviran")
    except Exception as e:
        print("Napaka pri rezervaciji:", e)

#rezervacija kot trener

def kupi_karto(conn, uporabnik):
    print("Razpoložljive karte:")
    for k in conn.execute("SELECT karta_id, nazivn trajanje_dni, cena FROM karta"):
        print(f"{k[0]}: {k[1]}, trajanje")
    karta_id = input("Vnesi ID karte, ki jo želiš kupiti:")
    try:
        uporabnik.kupi_karto(int(karta_id))
        print("Karta kupljena!")