import sqlite3
from model import Uporabnik, Trener, Termin, Karta 

def prikazi_proste_termine(conn):
    print("Prosti termini (naslednjih 14 dni):")
    for t in Termin.prosti_termini(conn, dni=14):
        print(f"{t[0]}: dvorana {t[1]}, {t[2]} {t[3]} - {t[4]}")

def rezerviraj_termin_U(conn, uporabnik):
    '''funkcija termin uspešno rezervira ali javi napako
    '''
    if not uporabnik.ima_veljavno_karto():
        izbira = input("Nimate veljavne karte.  (*) za nakup: ")
        if izbira == "*":
            kupi_karto(conn, uporabnik)
        return 
    
    prikazi_proste_termine(conn)
    termin_id = input("Vnesi ID termina, ki ga želiš rezervirati: ")
    try:
        uporabnik.izberi_termin(int(termin_id))
        print("Termin rezerviran")
    except Exception as e:
        print("Napaka pri rezervaciji:", e)

def rezerviraj_termin_T(conn, trener):
    '''funkcija termin uspešno rezervira ali javi napako
    '''
    prikazi_proste_termine(conn)
    termin_id = input("Vnesi ID termina, ki ga želiš rezervirati: ")
    try:
        trener.izberi_termin(int(termin_id))
        print("Termin rezerviran!")
    except Exception as e:
        print("Napaka pri rezervaciji:", e)

def kupi_karto(conn, uporabnik):
    print("Razpoložljive karte:")
    for k in conn.execute("SELECT karta_id, naziv, trajanje, cena FROM karta"):
        print(f"{k[0]}: {k[1]}, trajanje {k[2]} dni, cena {k[3]} EUR")
    karta_id = input("Vnesi številko karte, ki jo želiš kupiti:")
    try:
        uporabnik.kupi_karto(int(karta_id))
        print("Karta kupljena!")
    except Exception as e:
        print("Napaka pri nakupu:", e)

def preveri_karte(conn, uporabnik):
    print("Tvoje karte:")
    for k in uporabnik.aktivne_karte():
        print(f"- {k[0]}, kupljena {k[1]}, trajanje {k[2]} dni")

def meni_uporabnik(conn, uporabnik):
    while True:
        print("1) Poglej termine")
        print("2) Rezerviraj termin")
        print("3) Kupi karto")
        print("4) Preveri svoje karte")
        print("5) Izhod")

        izbira = input("> ")

        if izbira == "1":
            prikazi_proste_termine(conn)
        elif izbira == "2":
            rezerviraj_termin_U(conn, uporabnik)
        elif izbira == "3":
            kupi_karto(conn, uporabnik)
        elif izbira == "4":
            preveri_karte(conn, uporabnik)
        elif izbira == "5":
            break
        else:
            print("Neveljavna izbira")

def meni_trener(conn, trener):
    while True:
        print("1) Poglej termine")
        print("2) Rezerviraj termin")
        print("3) Izhod")

        izbira = input("> ")

        if izbira == "1":
            prikazi_proste_termine(conn)
        elif izbira == "2":
            rezerviraj_termin_T(conn, trener)
        elif izbira == "3":
            break
        else:
            print("Neveljavna izbira")

def glavni_meni(conn):
    print("Dobrodošli v fitnes sistemu!")
    tip = input("Si uporabnik (u) ali trener(t)?")

    if tip.lower() == "u":
        email = input("vnesi svoj email: ")
        uporabnik = Uporabnik.prijava(conn, email)

        if uporabnik:
            meni_uporabnik(conn, uporabnik)
        else:
            print("Uporabnik ne obstaja")

    elif tip.lower() == "t":
        ime = input("Vnesi ime: ")
        priimek = input("Vnesi priimek:")

        vrstica = conn.execute(
            "SELECT trener_id, specializacija FROM trener WHERE ime = ? AND priimek = ?",
            (ime, priimek)
        ).fetchone()

        if vrstica:
            trener = Trener(conn, ime, priimek, vrstica[1], vrstica[0])
            meni_trener(conn, trener)
        
        else:
            print("Trener ne obstaja")

    else:
        print("Neveljavna izbira")

if __name__ == "__main__":
    conn = sqlite3.connect("fitnes.db")
    glavni_meni(conn)
    conn.close()