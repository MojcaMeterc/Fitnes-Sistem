import sqlite3

from model import Karta, Termin, Trener, Uporabnik


def prikazi_proste_termine(conn):
    print("\nProsti termini (naslednjih 14 dni):")

    trenutni_datum = None

    for t in Termin.termini_brez_trenerja(conn):
        termin_id, datum, zacetek, konec, dvorana = t

        if datum != trenutni_datum:
            trenutni_datum = datum
            print(f"\n===== {datum} =====")

        print(f"{termin_id} Dvorana: {dvorana} | {zacetek} - {konec}")


def rezerviraj_termin_U(conn, uporabnik):
    """funkcija termin uspešno rezervira ali javi napako"""
    if not uporabnik.ima_veljavno_karto():
        izbira = input("\nNimate veljavne karte.  (*) za nakup: ")
        if izbira == "*":
            kupi_karto(conn, uporabnik)
        return

    prikazi_proste_termine(conn)
    termin_id = input("Vnesi ID termina, ki ga želiš rezervirati: ")
    try:
        uporabnik.izberi_termin(int(termin_id))
        print("\nTermin rezerviran")
    except Exception as e:
        print("\nNapaka pri rezervaciji:", e)


def rezerviraj_termin_T(conn, trener):
    """funkcija termin uspešno rezervira ali javi napako"""
    prikazi_proste_termine(conn)
    termin_id = input("Vnesi ID termina, ki ga želiš rezervirati: ")
    try:
        trener.izberi_termin(int(termin_id))
        print("\nTermin rezerviran!")
    except Exception as e:
        print("\nNapaka pri rezervaciji:", e)


def kupi_karto(conn, uporabnik):
    """Omogoča nakup karte."""
    print("\nRazpoložljive karte:")
    for k in conn.execute("SELECT karta_id, naziv, trajanje, cena FROM karta"):
        print(f"{k[0]}: {k[1]}, trajanje {k[2]} dni, cena {k[3]} EUR")
    karta_id = input("Vnesi številko karte, ki jo želiš kupiti:")
    try:
        uporabnik.kupi_karto(int(karta_id))
        print("\nKarta kupljena!")
    except Exception as e:
        print("\nNapaka pri nakupu:", e)


def preveri_karte(conn, uporabnik):
    """"Prikaže kupljene karte"""
    print("\nTvoje karte:")
    for k in uporabnik.aktivne_karte():
        print(f"- {k[0]}, kupljena {k[1]}, trajanje {k[2]} dni")

def prikazi_moje_rezveracijeU(uporabnik):
    """Prikaže rezervirane termine uporabnika"""
    print("\nMoje rezervacije:")
    for r in uporabnik.moje_rezervacije():
        datum, zacetek, konec, dvorana = r[0], r[1], r[2], r[3]
        print(f"  {datum}  |  {zacetek} - {konec} | {dvorana}")

def prikaz_moje_rezervacijeT(trener):
    print("\nMoji termini: ")
    for t in trener.moji_termini():
        print(f"  {t[1]}  |  {t[2]} - {t[3]}  |  {t[4]}  |  prijavljenih: {t[5]}")



def meni_uporabnik(conn, uporabnik):
    while True:
        print("\n1) Poglej termine")
        print("2) Rezerviraj termin")
        print("3) Kupi karto")
        print("4) Preveri svoje karte")
        print("5) Moje rezervacije")
        print("6) Izhod")

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
            prikazi_moje_rezveracijeU(uporabnik)
        elif izbira == "6":
            break
        else:
            print("Neveljavna izbira")


def meni_trener(conn, trener):
    while True:
        print("\n1) Poglej termine")
        print("2) Rezerviraj termin")
        print("3) Prikaz rezerviranih terminov:")
        print("4) Izhod")

        izbira = input("> ")

        if izbira == "1":
            prikazi_proste_termine(conn)
        elif izbira == "2":
            rezerviraj_termin_T(conn, trener)
        elif izbira == "3":
            prikaz_moje_rezervacijeT(trener)
        elif izbira == "4":
            break
        else:
            print("Neveljavna izbira")


def glavni_meni(conn):
    print("Dobrodošli v fitnes sistemu!")
    tip = input("Si uporabnik (u) ali trener(t)?")

    if tip.lower() == "u":
<<<<<<< HEAD
        email = input("vnesi svoj email: ")
        geslo = input('Vnesi geslo: ')
=======
        email = input("Vnesi svoj email: ")
        geslo = input("Vnesi geslo: ")
>>>>>>> b38bbae85521fd140bce7e92a1ff649d5cc9e75e
        uporabnik = Uporabnik.prijava(conn, email, geslo)

        if uporabnik:
            meni_uporabnik(conn, uporabnik)
        else:
            print("Uporabnik ne obstaja")

    elif tip.lower() == "t":
        email = input("Vnesi svoj email: ")
        geslo = input("Vnesi geslo: ")

        trener = Trener.prijava(conn, email, geslo)

        if trener:
            meni_trener(conn, trener)

        else:
            print("Trener ne obstaja")

    else:
        print("Neveljavna izbira")


if __name__ == "__main__":
    conn = sqlite3.connect("fitnes.db")
    glavni_meni(conn)
    conn.close()