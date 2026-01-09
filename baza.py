import csv
import sqlite3

PARAM_FMT = ':{}'

class Tabela:
    """
    Osnovni razder za tabelo v bazi
    """
    ime = None
    podatki = None

    def __init__(self, conn):
        self.conn = conn

    def ustvari(self):
        raise NotImplementedError

    def izbrisi(self):
        self.conn.execute(f"DROP TABLE IF EXISTS {self.ime};")

    def izprazni(self):
        self.conn.execute(f"DELETE FROM {self.ime};")

    def dodajanje(self, stolpci):
        return f"""
            INSERT INTO {self.ime} ({", ".join(stolpci)})
            VALUES({", ".join(PARAM_FMT.format(s) for s in stolpci)});
        """
    def dodaj_vrstico(self, **podatki):
        podatki = {k: v for k, v in podatki.items() if v is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid

    def uvozi(self, encoding='UTF-8'):
        if self.podatki is None:
            return
        with open(self.podatki, encoding=encoding, newline="") as f:
            bralnik = csv.reader(f)
            stolpci = next(bralnik)
            for vrstica in bralnik:
                podatki = {
                    k: None if v == "" else v
                    for k, v in zip(stolpci, vrstica)
                }
                self.dodaj_vrstico(**podatki)

class Uporabniki(Tabela):
    ime = 'uporabniki'
    podatki = "podatki/uporabniki.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE uporabniki (
                uporabnik_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT NOT NULL,
                priimek TEXT NOT NULL,
                email TEXT UNIQUE,
                telefon TEXT UNIQUE
                );
     """)

class Trener(Tabela):
    ime = 'trener'
    podatki = 'podatki/trenerji.csv'

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE trener(
                trener_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT NOT NULL,
                priimek TEXT NOT NULL,
                specializacija TEXT NOT NULL
            );
        """)

class Dvorane(Tabela):
    ime = 'dvorane'
    podatki = 'podatki/dvorane.csv'

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE dvorane(
                dvorana_id INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT NOT NULL,
                kapaciteta INTEGER NOT NULL CHECK (kapaciteta > 0)
        );
    """)

class Karta(Tabela):
    ime = 'karta'
    podatki = 'podatki/karte.csv'

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE karta(
                karta_id INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT NOT NULL,
                trajanje_dni INTEGER NOT NULL CHECK(trajanje_dni > 0),
                cena REAL NOT NULL CHECK(cena > 0)
            );
        """)

class Termin(Tabela):
    ime = 'termini'
    podatki = 'podatki/termini.csv'

    def ustvari(self):
       self.conn.execute("""
            CREATE TABLE termini(
                termin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dvorana TEXT NOT NULL,
                datum TEXT NOT NULL,
                ura_pricetka TEXT NOT NULL,
                ura_konca TEXT NOT NULL         
            );
  """)

class Rezervacija(Tabela):
    ime = 'rezervacije'
    podatki = 'podatki/rezervacije.csv'

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE rezervacija(
                rezervacija_id INTEGER PRIMARY KEY AUTOINCREMENT,
                termin_id INTEGER
            );
""")

def pripravi_tabele(conn):
    return[
        Uporabniki(conn),
        Trener(conn),
        Dvorane(conn),
        Karta(conn),
        Termin(conn),
        Rezervacija(conn)
    ]

def ustvari_bazo(conn):
    conn.execute('PRAGMA foreign_keys = ON')
    tabele = pripravi_tabele(conn)
    for t in reversed(tabele):
        t.izbrisi()
    for t in tabele:
        t.ustvari()
    for t in tabele:
        t.uvozi()

if __name__ == '__main__':
    conn = sqlite3.connect('fitnes.db')
    ustvari_bazo(conn)
    conn.close()
